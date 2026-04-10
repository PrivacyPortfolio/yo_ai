# agents/the_sentinel/the_sentinel_handler.py

"""
Lambda handler for the The-Sentinel agent.

Dispatch model: run() first, call_ai() fallback only.
See door_keeper_handler.py for full pattern documentation.
"""

import json
import logging
from datetime import datetime, timezone

from the_sentinel import TheSentinelAgent
from core.runtime.schema_validator import schema_validator
from core.runtime.ai_transform import call_ai
from core.runtime.output_shaper import shape_output
from core.runtime.log_bootstrapper import LogBootstrapper
from core.runtime.platform_event_bus import PlatformEventBus


logger = logging.getLogger()
logger.setLevel(logging.INFO)

AGENT = TheSentinelAgent(slim=True)
LOG   = LogBootstrapper(agent_name=AGENT.name)
BUS   = PlatformEventBus()

CAPABILITY_ROUTER = {
    "PlatformMonitor": "Platform.Monitor",
}

CAPABILITY_DISPATCH = {
    "Platform.Monitor": AGENT.platform_monitor,
}


def lambda_handler(event, context):
    raw_path       = event.get("rawPath", "")
    aws_request_id = context.aws_request_id if context else None

    try:
        if raw_path:
            capability_name = raw_path.rstrip("/").split("/")[-1]
            if capability_name not in CAPABILITY_ROUTER:
                return _error(400, f"Unknown capability path segment: {capability_name}")
            capability_id = CAPABILITY_ROUTER[capability_name]
            params  = json.loads(event.get("body") or "{}")
            payload = params.get("payload", params)
        else:
            capability_id = event.get("capability", "")
            if capability_id not in CAPABILITY_DISPATCH:
                return _error(400, f"Unknown capability: {capability_id}")
            params  = event
            payload = event.get("payload", {})

        schema_url = (
            f"https://yo-ai.ai/schemas/"
            f"{capability_id.lower().replace('.', '-')}.input.schema.json"
        )
        validation_errors = schema_validator.validate_input(schema_url, payload)
        if validation_errors:
            LOG.write(
                event_type="Handler.ValidationFailed",
                message=f"Input validation failed for {capability_id}.",
                data={"capability": capability_id, "errors": validation_errors,
                      "awsRequestId": aws_request_id}
            )
            return _error(400, f"Input validation failed: {validation_errors}")

        agent_ctx      = AGENT._build_agent_context(params)
        capability_ctx = AGENT._build_capability_context(capability_id, params)

        result = None
        try:
            result = await_or_call(
                CAPABILITY_DISPATCH[capability_id], payload, agent_ctx, capability_ctx
            )
        except NotImplementedError:
            LOG.write(
                event_type="Handler.CallAiFallback",
                message=f"run() not implemented for {capability_id} — falling back to call_ai().",
                data={"capability": capability_id, "awsRequestId": aws_request_id}
            )

        if result is None:
            result = call_ai(
                {"persona": AGENT.name, "capability": capability_id, "input": payload,
                 "context": {"awsRequestId": aws_request_id, "rawPath": raw_path}},
                AGENT
            )

        output_schema_url = (
            f"https://yo-ai.ai/schemas/"
            f"{capability_id.lower().replace('.', '-')}.output.schema.json"
        )
        shaped_output = shape_output(result, output_schema_url)

        LOG.write(
            event_type="Handler.Complete",
            message=f"{capability_id} completed.",
            data={"agentName": AGENT.name, "capability": capability_id,
                  "correlationId": agent_ctx.correlation_id, "taskId": agent_ctx.task_id,
                  "dryRun": capability_ctx.dry_run, "awsRequestId": aws_request_id}
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "method":  f"a2a.{capability_id}",
                "result":  shaped_output,
                "metadata": {
                    "agentName":     AGENT.name,
                    "capability":    capability_id,
                    "correlationId": agent_ctx.correlation_id,
                    "taskId":        agent_ctx.task_id,
                    "timestamp":     datetime.now(timezone.utc).isoformat(),
                }
            }),
        }

    except Exception as e:
        logger.exception("Handler error")
        LOG.write(
            event_type="Handler.Error",
            message="Unhandled exception in the_sentinel_handler.",
            data={"error": str(e), "awsRequestId": aws_request_id, "rawPath": raw_path}
        )
        return _error(500, str(e))


def await_or_call(fn, payload, agent_ctx, capability_ctx):
    import asyncio, inspect
    if inspect.iscoroutinefunction(fn):
        return asyncio.get_event_loop().run_until_complete(
            fn(payload, agent_ctx, capability_ctx)
        )
    return fn(payload, agent_ctx, capability_ctx)


def _error(status_code: int, message: str) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }
