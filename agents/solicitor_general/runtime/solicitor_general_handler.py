# agents/solicitor_general/runtime/solicitor_general_handler.py
#
# Direct API Lambda handler for the Solicitor-General (Mode B).
#
# Bypasses A2ATransport and the SG routing pipeline.
# Use for: direct capability invocation, isolated testing, AI-first
# training cycles where call_ai() is still handling transformation.
#
# Transport boundary responsibilities:
#   - Extract aws_request_id → seeds correlation_id
#   - Extract ctx_data block from body → seeds all YoAiContext fields
#   - Call generate_message_ids() to resolve correlation_id / task_id
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
from core.platform_agent import PlatformEventBus
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability
from core.yoai_context import input_schema_name, output_schema_name
from core.observability.logging.log_bootstrapper import get_logger
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.utils.validators.schema_validator import validate_input, load_schema


# ── Capability map loader ──────────────────────────────────────────────────

def _load_sg_routes() -> dict[str, str]:
    # ── routes section from capability_map.yaml ────────────────────────────
    # Falls back to hardcoded SG routes on any load failure.
    try:
        map_path = (
            Path(__file__).resolve().parents[3]
            / "shared" / "artifacts" / "capability_map.yaml"
        )
        if map_path.exists():
            with map_path.open("r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            path_map = {}
            for route in raw.get("routes", {}).get("solicitor-general", []):
                path = route.get("path", "")
                capability = route.get("capability", "")
                segment = path.rstrip("/").split("/")[-1]
                if segment and capability:
                    path_map[segment] = capability
            if path_map:
                return path_map
    except Exception as e:
        print(f"[sg_handler] WARNING: capability_map.yaml failed to load: {e}")

    return {
        "justAsk":                  "Just-Ask",
        "eventLog":                 "Event.Log",
        "requestResponseCorrelate": "Request-Response.Correlate",
    }


# ── Module-level singletons ────────────────────────────────────────────────
# One set per Lambda execution environment.

_logger = get_logger("solicitor-general-handler")

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
    # ── Steps ──────────────────────────────────────────────────────────────
    # 1. Load input + output schemas (names derived from ctx.capability_id)
    # 2. Validate input — non-blocking, logs warning on failure
    # 3. Dispatch to run() module or fall back to call_ai()
    # 4. Shape output
    # 5. Log execution event

    # 1. Schemas — derived from capability_id already bound in ctx
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

    # 2. Input validation — non-blocking
    if i_schema:
        try:
            validate_input(i_schema_name, payload)
        except Exception as e:
            _logger.write({
                "actor":      "solicitor-general-handler",
                "event_type": "input_validation_warning",
                "level":      "WARNING",
                "payload":    {"error": str(e), "capability": capability_id},
            })

    # 3. Dispatch
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

    # 5. Log
    _logger.write({
        "actor":      _sg.instance_id,
        "event_type": "capability_executed",
        "level":      "INFO",
        "payload": {
            "capability":     capability_id,
            "correlation_id": ctx.get("correlation_id"),
            "task_id":        ctx.get("task_id"),
            "slim":           ctx.get("slim"),
            "dry_run":        ctx.get("dry_run"),
            "aws_request_id": aws_request_id,
        },
    })

    return shaped


async def _dispatch(
    capability_id: str,
    payload: dict,
    ctx: YoAiContext,
    aws_request_id: str | None,
    raw_path: str,
    o_schema: dict,
) -> dict:
    # ── Try run() module first; fall back to call_ai() ─────────────────────
    # Stage 1 (training): call_ai() handles everything
    # Stage 2 (convergence): run() module replaces call_ai() for this capability
    # Stage 3 (production): all capabilities have run() modules

    module_name = _capability_id_to_module(capability_id)
    try:
        mod = importlib.import_module(f"agents.solicitor_general.{module_name}")
        if hasattr(mod, "run"):
            # ── run() module exists — pass YoAiContext directly ────────────
            # ctx already carries correlation_id, task_id, startup_mode,
            # caller, subject_ref, profile, and all governance knobs.
            # No stub construction needed.
            return await mod.run(payload, ctx)
    except ModuleNotFoundError:
        pass
    except Exception as e:
        _logger.write({
            "actor":      "solicitor-general-handler",
            "event_type": "run_module_error",
            "level":      "WARNING",
            "payload":    {"error": str(e), "capability": capability_id},
        })

    # ── Fallback: call_ai() synthesis ─────────────────────────────────────
    if ctx.get("dry_run"):
        return {"status": "dry_run", "capability": capability_id, "payload": payload}

    ai_prompt = {
        "agentId":    _sg.name,
        "capability": capability_id,
        "input":      payload,
        "context": {
            "awsRequestId":   aws_request_id,
            "rawPath":        raw_path,
            "correlationId":  ctx.get("correlation_id"),
            "taskId":         ctx.get("task_id"),
            "slim":           ctx.get("slim"),
            "step":           ctx.get("step"),
        },
    }

    return call_ai(ai_prompt, _sg)


# ── Schema name helpers ────────────────────────────────────────────────────

def _capability_id_to_module(capability_id: str) -> str:
    # ── "Just-Ask" → "just_ask" ────────────────────────────────────────────
    return capability_id.lower().replace(".", "_").replace("-", "_").replace(" ", "_")


# ── Lambda entrypoint ──────────────────────────────────────────────────────

def lambda_handler(event, context):
    # ── Transport boundary — seed YoAiContext here ─────────────────────────
    #
    # This is the outermost platform boundary for Mode B (Direct API).
    # Every field that belongs in YoAiContext for an auditable trail is
    # extracted here, before any downstream code runs.
    #
    # Field sourcing:
    #   correlation_id  ← aws_request_id (JSON-RPC alignment) via generate_message_ids()
    #   task_id         ← ctx_data.task_id or falls back to correlation_id
    #   startup_mode    ← "api" (hardcoded — this is the Direct API path)
    #   capability_id   ← bound via ctx_for_capability() after route resolution
    #   actor_kind      ← "Agent" (from as_actor_stub() inside _build_context)
    #   slim            ← ctx_data.slim (default True for Direct API)
    #   dry_run         ← ctx_data.dry_run
    #   trace           ← ctx_data.trace
    #   tools           ← ctx_data.tools
    #   caller          ← ctx_data.caller
    #   profile         ← ctx_data.profile
    #   subject_ref     ← ctx_data.subject_ref
    #   step            ← ctx_data.step
    #   prior_outputs   ← ctx_data.prior_outputs
    #   state           ← ctx_data.state

    try:
        # ── Route resolution ───────────────────────────────────────────────
        raw_path = event.get("rawPath", "")
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
        except json.JSONDecodeError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Invalid JSON body: {e}"}),
            }

        # ── Payload and ctx_data extraction ────────────────────────────────
        # Structured body: { "payload": {...}, "ctx": {...} }
        # Flat body (legacy): treat entire body as payload, no ctx fields
        if "payload" in body:
            payload  = body.get("payload", {})
            ctx_data = body.get("ctx", {})       # "ctx" — aligned with envelope shape
        else:
            payload  = body
            ctx_data = {}

        # ── AWS request id ─────────────────────────────────────────────────
        request_context = event.get("requestContext") or {}
        aws_request_id = (
            getattr(context, "aws_request_id", None)
            or request_context.get("requestId")
        )

        # ── Seed correlation_id and task_id at the transport boundary ──────
        # generate_message_ids() is pure — returns (correlation_id, task_id).
        # aws_request_id is the JSON-RPC id; ctx_data may carry a task_id
        # from an orchestrating workflow step.
        correlation_id, task_id = _sg.generate_message_ids(
            request_id=aws_request_id,
            task_id=ctx_data.get("task_id"),
        )

        # ── Build the pipeline-level YoAiContext from the envelope ─────────
        # Merges agent identity (as_actor_stub) with all transport-boundary
        # fields extracted above. capability_id is not bound yet — that
        # happens in ctx_for_capability() below so the pipeline ctx and
        # capability ctx are distinct and auditable separately.
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

        # ── Bind capability_id — produces the capability-level ctx ─────────
        # Response face (profile_patch, governance_labels) reset to clean.
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
        # correlation_id and task_id come from ctx — the request-scoped
        # values, not from self.* on the agent singleton.
        response_body = {
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
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body),
        }

    except Exception as e:
        _logger.write({
            "actor":      "solicitor-general-handler",
            "event_type": "handler_error",
            "level":      "ERROR",
            "payload":    {"error": str(e), "raw_path": event.get("rawPath", "")},
        })
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id":      None,
                "error":   {"code": -32603, "message": str(e)},
                "metadata": {"taskId": None, "status": "failed"},
            }),
        }
