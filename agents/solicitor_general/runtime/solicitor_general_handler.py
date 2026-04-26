# agents/solicitor_general/runtime/solicitor_general_handler.py
#
# Direct API Lambda handler for the Solicitor-General.
#
# Purpose:
#   Bypasses A2ATransport and the full routing pipeline.
#   Used for: direct SG capability invocation, isolated testing,
#   and AI-first training cycles where call_ai() handles transformation.
#
#   This is NOT the platform routing path — that is lambda_handler.py +
#   api_handler.py. This handler owns its own slim SG singleton and seeds
#   YoAiContext directly at the transport boundary.
#
# Transport boundary responsibilities:
#   - Extract aws_request_id → seeds correlation_id via generate_message_ids()
#   - Extract ctx_data block from body → seeds all YoAiContext fields
#   - Call ctx_for_capability() to bind capability_id before dispatch
#   - Pass the fully-seeded YoAiContext into every downstream call
#
# The singleton _sg is slim — identity and AI execution only.
# No event_bus routing, no fingerprints, no knowledge loading.

import importlib
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import yaml

from agents.solicitor_general.runtime.solicitor_general import SolicitorGeneralAgent
from core.runtime.platform_event_bus import PlatformEventBus
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability
from core.yoai_context import input_schema_name, output_schema_name
from core.observability.logging.platform_logger import get_platform_logger
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.utils.validators.schema_validator import validate_input, load_schema

LOG = get_platform_logger("solicitor-general-handler")


# ── Capability map loader ──────────────────────────────────────────────────

def _load_sg_routes() -> dict[str, str]:
    # Loads SG routes from shared/registries/capability_map.yaml.
    # Falls back to hardcoded SG routes on any load failure.
    try:
        map_path = (
            Path(__file__).resolve().parents[3]
            / "shared" / "registries" / "capability_map.yaml"
        )
        if map_path.exists():
            with map_path.open("r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            path_map = {}
            for route in raw.get("routes", {}).get("solicitorGeneral", []):
                path = route.get("path", "")
                capability = route.get("capability", "")
                segment = path.rstrip("/").split("/")[-1]
                if segment and capability:
                    path_map[segment] = capability
            if path_map:
                return path_map
    except Exception as exc:
        LOG.write(
            event_type="sg_handler.CapabilityMapLoadFailed",
            payload={"error": str(exc)},
            context=None,
        )

    return {
        "justAsk":                  "Just-Ask",
        "eventLog":                 "Event.Log",
        "requestResponseCorrelate": "Request-Response.Correlate",
    }


# ── Module-level singletons ────────────────────────────────────────────────

# Slim SG — identity and AI execution only.
# event_bus required by PlatformAgent constructor; unused in slim mode.
_sg = SolicitorGeneralAgent(
    event_bus=PlatformEventBus(),
    slim=True,
)

_ROUTES: dict[str, str] = _load_sg_routes()


# ── Capability executor ────────────────────────────────────────────────────

async def _execute_capability(
    capability_id: str,
    payload: dict,
    ctx: YoAiContext,
    aws_request_id: str | None,
    raw_path: str,
) -> dict:
    # 1. Schema names derived from capability_id bound in ctx
    i_schema_name = input_schema_name(ctx)
    o_schema_name = output_schema_name(ctx)

    try:
        i_schema = load_schema(i_schema_name)
    except FileNotFoundError:
        i_schema = {}

    try:
        o_schema = load_schema(o_schema_name)
    except FileNotFoundError:
        o_schema = {}

    # 2. Input validation — non-blocking, logs warning on failure
    if i_schema:
        try:
            validate_input(i_schema_name, payload)
        except Exception as exc:
            LOG.write(
                event_type="sg_handler.InputValidationWarning",
                payload={"error": str(exc), "capability": capability_id},
                context=ctx,
            )

    # 3. Dispatch to run() or call_ai() fallback
    result = await _dispatch(
        capability_id=capability_id,
        payload=payload,
        ctx=ctx,
        aws_request_id=aws_request_id,
        raw_path=raw_path,
        o_schema=o_schema,
    )

    # 4. Shape output
    shaped = shape_output(result, o_schema) if o_schema else result

    # 5. Completion log
    LOG.write(
        event_type="sg_handler.CapabilityExecuted",
        payload={
            "capability":     capability_id,
            "correlation_id": ctx.get("correlation_id"),
            "task_id":        ctx.get("task_id"),
            "slim":           ctx.get("slim"),
            "dry_run":        ctx.get("dry_run"),
            "aws_request_id": aws_request_id,
        },
        context=ctx,
    )

    return shaped


async def _dispatch(
    capability_id: str,
    payload: dict,
    ctx: YoAiContext,
    aws_request_id: str | None,
    raw_path: str,
    o_schema: dict,
) -> dict:
    # Stage 1 (training):    call_ai() handles everything
    # Stage 2 (convergence): run() module replaces call_ai() per capability
    # Stage 3 (production):  all capabilities have run() modules

    module_name = _capability_id_to_module(capability_id)
    try:
        mod = importlib.import_module(f"agents.solicitor_general.{module_name}")
        if hasattr(mod, "run"):
            return await mod.run(payload, ctx)
    except ModuleNotFoundError:
        pass
    except Exception as exc:
        LOG.write(
            event_type="sg_handler.RunModuleError",
            payload={"error": str(exc), "capability": capability_id},
            context=ctx,
        )

    # Fallback: call_ai()
    if ctx.get("dry_run"):
        return {"status": "dry_run", "capability": capability_id, "payload": payload}

    return call_ai(
        {
            "agentId":    _sg.name,
            "capability": capability_id,
            "input":      payload,
            "context": {
                "awsRequestId":  aws_request_id,
                "rawPath":       raw_path,
                "correlationId": ctx.get("correlation_id"),
                "taskId":        ctx.get("task_id"),
                "slim":          ctx.get("slim"),
                "step":          ctx.get("step"),
            },
        },
        _sg,
    )


def _capability_id_to_module(capability_id: str) -> str:
    # "Just-Ask" → "just_ask"
    return capability_id.lower().replace(".", "_").replace("-", "_").replace(" ", "_")


# ── Lambda entrypoint ──────────────────────────────────────────────────────

def lambda_handler(event, context):
    try:
        # ── Route resolution ───────────────────────────────────────────────
        raw_path     = event.get("rawPath", "")
        path_segment = raw_path.rstrip("/").split("/")[-1]
        capability_id = _ROUTES.get(path_segment)

        if not capability_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error":       f"Unknown capability path: '{path_segment}'",
                    "known_paths": sorted(_ROUTES.keys()),
                }),
            }

        # ── Body parsing ───────────────────────────────────────────────────
        raw_body = event.get("body") or "{}"
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError as exc:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Invalid JSON body: {exc}"}),
            }

        # ── Payload and ctx_data extraction ────────────────────────────────
        # Structured body: { "payload": {...}, "ctx": {...} }
        # Flat body (legacy): treat entire body as payload
        if "payload" in body:
            payload  = body.get("payload", {})
            ctx_data = body.get("ctx", {})
        else:
            payload  = body
            ctx_data = {}

        # ── AWS request id — seeds correlation_id ──────────────────────────
        request_context = event.get("requestContext") or {}
        aws_request_id = (
            getattr(context, "aws_request_id", None)
            or request_context.get("requestId")
        )

        # ── Seed correlation_id and task_id at the transport boundary ──────
        correlation_id, task_id = _sg.generate_message_ids(
            request_id=aws_request_id,
            task_id=ctx_data.get("task_id"),
        )

        # ── Build pipeline-level YoAiContext ───────────────────────────────
        # capability_id not bound here — bound below via ctx_for_capability()
        # so the pipeline ctx and capability ctx are separately auditable.
        envelope = {
            "payload": payload,
            "ctx": {
                "startup_mode":  "api",
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
            **_sg.as_actor_stub(),
            instance_id=_sg.instance_id,
            correlation_id=correlation_id,
            task_id=task_id,
            profile=ctx_data.get("profile"),
        )

        # ── Bind capability_id ─────────────────────────────────────────────
        ctx: YoAiContext = ctx_for_capability(pipeline_ctx, capability_id)

        # ── Execute ────────────────────────────────────────────────────────
        result = asyncio.get_event_loop().run_until_complete(
            _execute_capability(
                capability_id=capability_id,
                payload=payload,
                ctx=ctx,
                aws_request_id=aws_request_id,
                raw_path=raw_path,
            )
        )

        # ── Response envelope ──────────────────────────────────────────────
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id":      ctx.get("correlation_id"),
                "method":  "a2a.message",
                "result": {
                    "agentId":    _sg.name,
                    "capability": capability_id,
                    "output":     result,
                },
                "metadata": {
                    "taskId":    ctx.get("task_id"),
                    "status":    "completed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }),
        }

    except Exception as exc:
        LOG.write(
            event_type="sg_handler.HandlerError",
            payload={
                "error":    str(exc),
                "raw_path": event.get("rawPath", ""),
            },
            context=None,
        )
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id":      None,
                "error":   {"code": -32603, "message": str(exc)},
                "metadata": {"taskId": None, "status": "failed"},
            }),
        }
