# agents/the_sentinel/runtime/the_sentinel_handler.py
#
# Lambda handler for The-Sentinel agent.
# Dispatch model: run() first, call_ai() fallback only.

import asyncio
import inspect
import json
from datetime import datetime, timezone

from agents.the_sentinel.runtime.the_sentinel import TheSentinelAgent
from core.platform_event_bus import PlatformEventBus
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability
from core.yoai_context import input_schema_name, output_schema_name
from core.utils.validators.schema_validator import schema_validator
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.observability.logging.platform_logger import get_platform_logger

_logger = get_platform_logger("the-sentinel-handler")


# -- Module-level singletons ----------------------------------------------

_event_bus = PlatformEventBus()

_AGENT = TheSentinelAgent(
    event_bus=_event_bus,
    slim=True,
)

# -- Capability routing ---------------------------------------------------

_CAPABILITY_ROUTER = {
    "PlatformMonitor": "Platform.Monitor",
}

_CAPABILITY_DISPATCH = {
    "Platform.Monitor": _AGENT.platform_monitor,
}


# -- Lambda entrypoint ----------------------------------------------------

def lambda_handler(event, context):
    raw_path       = event.get("rawPath", "")
    aws_request_id = getattr(context, "aws_request_id", None) if context else None

    try:
        # Route resolution
        if raw_path:
            path_segment  = raw_path.rstrip("/").split("/")[-1]
            capability_id = _CAPABILITY_ROUTER.get(path_segment)
            if not capability_id:
                return _error(400, f"Unknown capability path segment: {path_segment}")
            body     = json.loads(event.get("body") or "{}")
            payload  = body.get("payload", body)
            ctx_data = body.get("ctx", {})
        else:
            capability_id = event.get("capability", "")
            if capability_id not in _CAPABILITY_DISPATCH:
                return _error(400, f"Unknown capability: {capability_id}")
            payload  = event.get("payload", {})
            ctx_data = event.get("ctx", {})

        # Seed YoAiContext at the transport boundary
        correlation_id, task_id = _AGENT.generate_message_ids(
            request_id=aws_request_id,
            task_id=ctx_data.get("task_id"),
        )

        envelope = {
            "payload": payload,
            "ctx": {
                "startup_mode":  ctx_data.get("startup_mode", "api"),
                "caller":        ctx_data.get("caller"),
                "profile":       ctx_data.get("profile"),
                "subject_ref":   ctx_data.get("subject_ref"),
                "slim":          ctx_data.get("slim", True),
                "tools":         ctx_data.get("tools"),
                "dry_run":       ctx_data.get("dry_run", False),
                "trace":         ctx_data.get("trace", False),
                "step":          ctx_data.get("step"),
                "prior_outputs": ctx_data.get("prior_outputs"),
                "state":         ctx_data.get("state"),
            },
        }

        pipeline_ctx: YoAiContext = ctx_from_envelope(
            envelope,
            **_AGENT.as_actor_stub(),
            instance_id=_AGENT.instance_id,
            correlation_id=correlation_id,
            task_id=task_id,
            profile=ctx_data.get("profile"),
        )

        ctx: YoAiContext = ctx_for_capability(pipeline_ctx, capability_id)

        # Input validation
        i_schema_name = input_schema_name(ctx)
        validation_errors = schema_validator.validate_input(i_schema_name, payload)
        if validation_errors:
            _logger.write(
                event_type="Handler.ValidationFailed",
                payload={
                    "capability":    capability_id,
                    "errors":        validation_errors,
                    "correlationId": ctx.get("correlation_id"),
                },
                context=ctx,
            )
            return _error(400, f"Input validation failed: {validation_errors}")

        # Dispatch: run() first, call_ai() fallback
        handler = _CAPABILITY_DISPATCH[capability_id]
        result  = None

        try:
            result = _invoke(handler, payload, ctx)
        except NotImplementedError:
            _logger.write(
                event_type="Handler.CallAiFallback",
                payload={
                    "capability":    capability_id,
                    "correlationId": ctx.get("correlation_id"),
                },
                context=ctx,
            )

        if result is None:
            if ctx.get("dry_run"):
                result = {"status": "dry_run", "capability": capability_id, "payload": payload}
            else:
                result = call_ai(
                    {
                        "persona":    _AGENT.name,
                        "capability": capability_id,
                        "input":      payload,
                        "context": {
                            "awsRequestId":  aws_request_id,
                            "rawPath":       raw_path,
                            "correlationId": ctx.get("correlation_id"),
                            "taskId":        ctx.get("task_id"),
                        },
                    },
                    _AGENT,
                )

        # Output shaping
        o_schema_name = output_schema_name(ctx)
        shaped_output = shape_output(result, o_schema_name) if o_schema_name else result

        _logger.write(
            event_type="Handler.Complete",
            payload={
                "agentName":     _AGENT.name,
                "capability":    capability_id,
                "correlationId": ctx.get("correlation_id"),
                "taskId":        ctx.get("task_id"),
                "dryRun":        ctx.get("dry_run"),
                "awsRequestId":  aws_request_id,
            },
            context=ctx,
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "method":  f"a2a.{capability_id}",
                "result":  shaped_output,
                "metadata": {
                    "agentName":     _AGENT.name,
                    "capability":    capability_id,
                    "correlationId": ctx.get("correlation_id"),
                    "taskId":        ctx.get("task_id"),
                    "timestamp":     datetime.now(timezone.utc).isoformat(),
                },
            }),
        }

    except Exception as exc:
        _logger.write(
            event_type="Handler.Error",
            payload={
                "error":        str(exc),
                "awsRequestId": aws_request_id,
                "rawPath":      raw_path,
            },
            context=None,
        )
        return _error(500, str(exc))


# -- Async dispatcher -----------------------------------------------------

def _invoke(fn, payload: dict, ctx: YoAiContext):
    if inspect.iscoroutinefunction(fn):
        return asyncio.get_event_loop().run_until_complete(fn(payload, ctx))
    return fn(payload, ctx)


# -- Error helper ---------------------------------------------------------

def _error(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }
