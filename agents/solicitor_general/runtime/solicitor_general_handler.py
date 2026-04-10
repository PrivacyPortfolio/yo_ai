# agents/solicitor_general/runtime/solicitor_general_handler.py

"""
AI-first Lambda handler for the Solicitor-General agent.

This is the per-agent Direct API handler (Mode B). It bypasses
A2ATransport, the SG routing pipeline, and AgentContext construction.
Use this for:
  - Direct capability invocation in development and testing
  - Isolated capability execution without platform overhead
  - AI-first training cycles where call_ai() is being replaced with code

When to use this vs api_handler.py (Mode 3):
  Use THIS handler when:
    - You want to invoke a single SG capability directly
    - You don't need platform governance (AgentContext, correlation, fingerprints)
    - You are developing or testing a capability in isolation
    - call_ai() is still handling the transformation (training stage)

  Use api_handler.py (Mode 3) when:
    - You want full platform pipeline (AgentContext, UCR, governance)
    - You need CapabilityContext injection with Mode 1 governance
    - You are running an orchestrated workflow step
    - The capability touches governed data or requires correlation

Agent lifecycle:
  The SG instance is a warm singleton — constructed once per Lambda
  execution environment with slim=True (no fingerprints, knowledge,
  or tool loading). This is correct for the AI-first execution path
  which uses call_ai() rather than vault or tool access.

  Note: This handler does NOT construct the full SolicitorGeneralAgent
  with event_bus and capability_map — those are only needed for the
  platform routing path (Mode 1/3). Here the SG is used purely as an
  identity and AI execution carrier.

Capabilities served:
  Just-Ask                → just_ask
  Event.Log               → event_log
  Request-Response.Correlate → request_response_correlate

  Capability routing is loaded from shared/artifacts/capability_map.yaml
  (routes section) — no hard-coded path maps in this file.
"""

import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import yaml

from agents.solicitor_general.runtime.solicitor_general import SolicitorGeneralAgent
from core.platform_agent import PlatformEventBus
from core.base_agent import CapabilityContext
from core.observability.logging.log_bootstrapper import get_logger
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.utils.validators.schema_validator import validate_input, load_schema


# ---------------------------------------------------------------------------
# Capability map loader — routes section only
# ---------------------------------------------------------------------------

def _load_sg_routes() -> dict[str, str]:
    """
    Load the SG's capability route map from shared/artifacts/capability_map.yaml.
    Returns a dict of { camelCasePath: canonical-capability-name }.
    Falls back to hardcoded SG routes on any failure.
    """
    try:
        map_path = (
            Path(__file__).resolve().parents[3]
            / "shared" / "artifacts" / "capability_map.yaml"
        )
        if map_path.exists():
            with map_path.open("r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}

            path_map = {}
            sg_routes = raw.get("routes", {}).get("solicitor-general", [])
            for route in sg_routes:
                path = route.get("path", "")
                capability = route.get("capability", "")
                if path and capability:
                    segment = path.rstrip("/").split("/")[-1]
                    if segment:
                        path_map[segment] = capability
            if path_map:
                return path_map
    except Exception as e:
        print(f"[sg_handler] WARNING: capability_map.yaml failed to load: {e}")

    # Hardcoded fallback — matches capability_map.yaml routes section
    return {
        "justAsk":                  "Just-Ask",
        "eventLog":                 "Event.Log",
        "requestResponseCorrelate": "Request-Response.Correlate",
    }


# ---------------------------------------------------------------------------
# Module-level singletons
# One set per Lambda execution environment.
# ---------------------------------------------------------------------------

_logger = get_logger("solicitor-general-handler")

# Slim SG instance — identity and AI execution only.
# No event_bus, no capability_map, no routing pipeline.
# This is correct for the AI-first Direct API path.
_capability_ctx = CapabilityContext(slim=True)
_sg = SolicitorGeneralAgent(
    event_bus=PlatformEventBus(),   # required by PlatformAgent — unused in slim mode
    capability_ctx=_capability_ctx,
)

# Route map — loaded once at cold start
_ROUTES: dict[str, str] = _load_sg_routes()


# ---------------------------------------------------------------------------
# Capability executor
# ---------------------------------------------------------------------------

async def _execute_capability(
    capability_id: str,
    payload: dict,
    capability_ctx: CapabilityContext,
    aws_request_id: str | None,
    raw_path: str,
) -> dict:
    """
    Execute a single SG capability using the AI-first pattern.

    Steps:
      1. Load input + output schemas for the capability
      2. Validate input (non-blocking — logs warning on failure)
      3. Dispatch to capability run() module if implemented,
         otherwise fall back to call_ai() synthesis
      4. Shape output to declared output schema
      5. Log the capability event

    The capability run() module is the convergence point between
    AI-first (Mode B) and platform-governed (Mode A) execution.
    Both paths ultimately call the same run(payload, agent_ctx, capability_ctx).
    """

    # 1. Load schemas
    input_schema_name = _capability_id_to_schema(capability_id, "input")
    output_schema_name = _capability_id_to_schema(capability_id, "output")

    try:
        input_schema = load_schema(input_schema_name)
    except FileNotFoundError:
        input_schema = {}

    try:
        output_schema = load_schema(output_schema_name)
    except FileNotFoundError:
        output_schema = {}

    # 2. Validate input — non-blocking
    validated_input = payload
    if input_schema:
        try:
            validate_input(input_schema_name, payload)
        except Exception as e:
            _logger.write({
                "actor": "solicitor-general-handler",
                "event_type": "input_validation_warning",
                "level": "WARNING",
                "message": f"Input validation failed for {capability_id} — proceeding",
                "payload": {"error": str(e), "capability": capability_id},
            })

    # 3. Dispatch — try run() module first, fall back to call_ai()
    result = await _dispatch(
        capability_id=capability_id,
        payload=validated_input,
        capability_ctx=capability_ctx,
        aws_request_id=aws_request_id,
        raw_path=raw_path,
        output_schema=output_schema,
    )

    # 4. Shape output
    shaped = shape_output(result, output_schema) if output_schema else result

    # 5. Log
    _logger.write({
        "actor": _sg.instance_id,
        "event_type": "capability_executed",
        "level": "INFO",
        "message": f"{capability_id} executed via direct handler",
        "payload": {
            "capability": capability_id,
            "slim": capability_ctx.slim,
            "dry_run": capability_ctx.dry_run,
            "aws_request_id": aws_request_id,
        },
    })

    return shaped


async def _dispatch(
    capability_id: str,
    payload: dict,
    capability_ctx: CapabilityContext,
    aws_request_id: str | None,
    raw_path: str,
    output_schema: dict,
) -> dict:
    """
    Dispatch to the capability's run() module if implemented.
    Falls back to call_ai() synthesis when run() is not yet written.

    This is the AI-first training cycle in action:
      Stage 1: call_ai() handles everything        (training wheels)
      Stage 2: run() module handles it in code     (production)

    Switching from Stage 1 to Stage 2 requires no handler changes —
    just implement the run() module and it takes precedence.
    """
    # Map capability_id to module path and try importing run()
    module_name = _capability_id_to_module(capability_id)

    try:
        import importlib
        mod = importlib.import_module(
            f"agents.solicitor_general.{module_name}"
        )
        if hasattr(mod, "run"):
            # run() module exists — use it (Mode A convergence point)
            # Build a minimal AgentContext so run() modules can call
            # agent_ctx.log(), agent_ctx.correlation_id, etc. without
            # crashing. startup_mode="api" — this is the Direct API path.
            from core.base_agent import AgentContext
            stub_agent_ctx = AgentContext(
                correlation_id=capability_ctx.correlation_id,
                task_id=capability_ctx.task_id,
                startup_mode="api",
                caller=capability_ctx.caller,
                subject_ref=capability_ctx.subject_ref,
                governance_labels=[],
            )
            return await mod.run(payload, stub_agent_ctx, capability_ctx)
    except ModuleNotFoundError:
        pass   # run() module not yet implemented — fall through to call_ai()
    except Exception as e:
        _logger.write({
            "actor": "solicitor-general-handler",
            "event_type": "run_module_error",
            "level": "WARNING",
            "message": f"run() module error for {capability_id} — falling back to call_ai()",
            "payload": {"error": str(e)},
        })

    # Fall back to call_ai() synthesis
    if capability_ctx.dry_run:
        return {"status": "dry_run", "capability": capability_id, "payload": payload}

    ai_prompt = {
        "agentId": _sg.name,
        "capability": capability_id,
        "input": payload,
        "context": {
            "awsRequestId": aws_request_id,
            "rawPath": raw_path,
            "slim": capability_ctx.slim,
            "step": capability_ctx.step,
        },
    }

    return call_ai(ai_prompt, _sg)


# ---------------------------------------------------------------------------
# Schema name helpers
# ---------------------------------------------------------------------------

def _capability_id_to_schema(capability_id: str, direction: str) -> str:
    """
    Derive canonical schema filename from capability ID.
    Matches CapabilityContext.input_schema_name / output_schema_name.
      "Just-Ask"  → "just-ask.input.schema.json"   (hyphens preserved)
      "Event.Log" → "event.log.input.schema.json"   (dots preserved)
    """
    slug = capability_id.lower().replace(" ", "-")
    return f"{slug}.{direction}.schema.json"


def _capability_id_to_module(capability_id: str) -> str:
    """Convert 'Just-Ask' → 'just_ask'"""
    return capability_id.lower().replace(".", "_").replace("-", "_").replace(" ", "_")


# ---------------------------------------------------------------------------
# Lambda entrypoint
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    """
    Direct API Lambda entrypoint for the Solicitor-General (Mode B).

    Expected API Gateway HTTP API event:
      {
        "rawPath": "/agents/solicitorGeneral/<capabilityPath>",
        "body": "{ ...payload... }",
        "requestContext": { "requestId": "..." }
      }

    The body may optionally include a capability_ctx block:
      {
        "payload": { ... },
        "capability_ctx": {
          "slim": true,
          "dry_run": false,
          "trace": false,
          "step": 1,
          "prior_outputs": { ... },
          "state": { ... }
        }
      }

    Returns API Gateway Lambda proxy response.
    """
    try:
        # --- Extract path and capability ---
        raw_path = event.get("rawPath", "")
        path_segment = raw_path.rstrip("/").split("/")[-1]

        capability_id = _ROUTES.get(path_segment)
        if not capability_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Unknown capability path: '{path_segment}'",
                    "known_paths": sorted(_ROUTES.keys()),
                }),
            }

        # --- Parse body ---
        raw_body = event.get("body") or "{}"
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Invalid JSON body: {e}"}),
            }

        # --- Extract payload and capability_ctx ---
        # Support both flat body (legacy) and structured body with capability_ctx
        if "payload" in body:
            payload = body.get("payload", {})
            ctx_data = body.get("capability_ctx", {})
        else:
            # Flat body — treat entire body as payload, no capability_ctx
            payload = body
            ctx_data = {}

        # --- Build CapabilityContext ---
        # slim=True by default for Direct API — no governance artifacts needed
        # Caller may override via capability_ctx block
        capability_ctx = CapabilityContext(
            capability_id=capability_id,            # enables input/output_schema_name
            slim=ctx_data.get("slim", True),
            tools=ctx_data.get("tools"),
            dry_run=ctx_data.get("dry_run", False),
            trace=ctx_data.get("trace", False),
            startup_mode="api",
            correlation_id=ctx_data.get("correlation_id"),
            task_id=ctx_data.get("task_id"),
            profile=ctx_data.get("profile"),
            profile_patch=ctx_data.get("profile_patch"),
            caller=ctx_data.get("caller"),
            subject_ref=ctx_data.get("subject_ref"),   # was "subject" — renamed in v2
            step=ctx_data.get("step"),
            prior_outputs=ctx_data.get("prior_outputs"),
            state=ctx_data.get("state"),
        )

        # --- AWS request context ---
        request_context = event.get("requestContext") or {}
        aws_request_id = (
            getattr(context, "aws_request_id", None)
            or request_context.get("requestId")
        )

        # --- Execute ---
        result = asyncio.get_event_loop().run_until_complete(
            _execute_capability(
                capability_id=capability_id,
                payload=payload,
                capability_ctx=capability_ctx,
                aws_request_id=aws_request_id,
                raw_path=raw_path,
            )
        )

        # --- Response envelope ---
        response_body = {
            "jsonrpc": "2.0",
            "id": aws_request_id,
            "method": "a2a.message",
            "result": {
                "agentId": _sg.name,
                "capability": capability_id,
                "output": result,
            },
            "metadata": {
                "taskID": capability_ctx.task_id or aws_request_id,
                "status": "completed",
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
            "actor": "solicitor-general-handler",
            "event_type": "handler_error",
            "level": "ERROR",
            "message": str(e),
            "payload": {"raw_path": event.get("rawPath", "")},
        })
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": str(e),
                },
                "metadata": {
                    "taskID": None,
                    "status": "failed",
                },
            }),
        }
