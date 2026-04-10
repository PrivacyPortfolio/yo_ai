# /http/agents/data_steward/data_steward_handler.py

"""
AI-first Lambda handler for the Data-Steward agent.

This is the per-agent Direct API handler (Mode B). It bypasses
A2ATransport, the SG routing pipeline, and AgentContext construction.

Use this handler for:
  - Direct capability invocation in development and testing
  - Isolated capability execution without platform overhead
  - AI-first training cycles (call_ai → code replacement)

Use api_handler.py (Mode 3) for:
  - Full platform pipeline with AgentContext and governance
  - CapabilityContext injection with Mode 1 governance simultaneously
  - Orchestrated workflow steps
  - Capabilities touching governed personal data (vault access)

Agent lifecycle:
  One slim DataSteward instance per Lambda execution environment.
  No profile at module level — profile injected per-request from
  the request body. slim=True: no fingerprints, knowledge, or tools.

Capabilities served:
  Phone.Call                → phone_call
  Phone.Answer              → phone_answer
  Data-Request.Govern       → data_request_govern
  Email.Read                → email_read
  Email.Send                → email_send
"""

import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import yaml

from data_steward import DataSteward
from core.utils.validators.schema_validator import schema_validator
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.observability.logging.log_bootstrapper import LogBootstrapper


# ---------------------------------------------------------------------------
# Route loader
# ---------------------------------------------------------------------------

def _load_ds_routes() -> dict[str, str]:
    """
    Load DataSteward capability route map from capability_map.yaml.
    Falls back to hardcoded routes on failure.
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
            ds_routes = raw.get("routes", {}).get("data-steward", [])
            for route in ds_routes:
                path = route.get("path", "")
                capability = route.get("capability", "")
                if path and capability:
                    segment = path.rstrip("/").split("/")[-1]
                    if segment:
                        path_map[segment] = capability
            if path_map:
                return path_map
    except Exception as e:
        print(f"[ds_handler] WARNING: capability_map.yaml failed to load: {e}")

    # Hardcoded fallback
    return {
        "phoneCall":          "Phone.Call",
        "phoneAnswer":        "Phone.Answer",
        "dataRequestGovern":  "Data-Request.Govern",
        "emailRead":          "Email.Read",
        "emailSend":          "Email.Send",
    }


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_logger = get_logger("data-steward-handler")

# Slim singleton — no profile, no governance artifacts.
# Profile injected per-request from the request body.
_capability_ctx = CapabilityContext(slim=True)
_agent = DataSteward(capability_ctx=_capability_ctx)

_ROUTES: dict[str, str] = _load_ds_routes()


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
    Dispatch to run() module if implemented, fall back to call_ai().
    Validate input and shape output around the dispatch.
    """

    # Load schemas
    input_schema_name = _schema_name(capability_id, "input")
    output_schema_name = _schema_name(capability_id, "output")

    try:
        input_schema = load_schema(input_schema_name)
    except FileNotFoundError:
        input_schema = {}

    try:
        output_schema = load_schema(output_schema_name)
    except FileNotFoundError:
        output_schema = {}

    # Validate input — non-blocking
    if input_schema:
        try:
            validate_input(input_schema_name, payload)
        except Exception as e:
            _logger.write({
                "actor": "data-steward-handler",
                "event_type": "input_validation_warning",
                "level": "WARNING",
                "message": f"Input validation failed for {capability_id} — proceeding",
                "payload": {"error": str(e), "capability": capability_id},
            })

    # Dispatch — run() module first, call_ai() fallback
    result = await _dispatch(
        capability_id=capability_id,
        payload=payload,
        capability_ctx=capability_ctx,
        aws_request_id=aws_request_id,
        raw_path=raw_path,
        output_schema=output_schema,
    )

    # Shape output
    shaped = shape_output(result, output_schema) if output_schema else result

    _logger.write({
        "actor": _agent.instance_id,
        "event_type": "capability_executed",
        "level": "INFO",
        "message": f"{capability_id} executed via direct handler",
        "payload": {
            "capability": capability_id,
            "slim": capability_ctx.slim,
            "dry_run": capability_ctx.dry_run,
            "profile_name": (capability_ctx.profile or {}).get("name"),
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
    Try run() module first. Fall back to call_ai() if not yet implemented.
    This is the AI-first training cycle:
      Stage 1: call_ai() handles synthesis         (training wheels)
      Stage 2: run() module handles it in code     (production)
    """
    module_name = _module_name(capability_id)

    try:
        import importlib
        mod = importlib.import_module(f"agents.data_steward.{module_name}")
        if hasattr(mod, "run"):
            return await mod.run(payload, None, capability_ctx)
    except ModuleNotFoundError:
        pass
    except Exception as e:
        _logger.write({
            "actor": "data-steward-handler",
            "event_type": "run_module_error",
            "level": "WARNING",
            "message": f"run() error for {capability_id} — falling back to call_ai()",
            "payload": {"error": str(e)},
        })

    if capability_ctx.dry_run:
        return {"status": "dry_run", "capability": capability_id, "payload": payload}

    ai_prompt = {
        "agentId": _agent.name,
        "capability": capability_id,
        "input": payload,
        "context": {
            "awsRequestId": aws_request_id,
            "rawPath": raw_path,
            "slim": capability_ctx.slim,
            "step": capability_ctx.step,
            "profile": capability_ctx.profile,
        },
    }

    return call_ai(ai_prompt, _agent)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _schema_name(capability_id: str, direction: str) -> str:
    slug = capability_id.lower().replace(".", "-").replace(" ", "-")
    return f"{slug}.{direction}.schema.json"


def _module_name(capability_id: str) -> str:
    return capability_id.lower().replace(".", "_").replace("-", "_").replace(" ", "_")


# ---------------------------------------------------------------------------
# Lambda entrypoint
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    """
    Direct API Lambda entrypoint for the Data-Steward (Mode B).

    Expected API Gateway HTTP API event:
      {
        "rawPath": "/agents/dataSteward/<capabilityPath>",
        "body": "{...}",
        "requestContext": { "requestId": "..." }
      }

    The body supports both flat and structured formats:

      Flat (legacy):
        { "to": "...", "message": "..." }

      Structured (preferred):
        {
          "payload": { "to": "...", "message": "..." },
          "capability_ctx": {
            "slim": true,
            "dry_run": false,
            "profile": { "name": "BillyJo", "type": "person", "payload": {} },
            "correlation_id": "...",
            "task_id": "..."
          }
        }

    Profile is injected per-request via capability_ctx.profile.
    No profile is loaded at module level — the singleton is profile-free.
    """
    try:
        # Extract path and capability
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

        # Parse body
        raw_body = event.get("body") or "{}"
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Invalid JSON body: {e}"}),
            }

        # Extract payload and capability_ctx
        if "payload" in body:
            payload = body.get("payload", {})
            ctx_data = body.get("capability_ctx", {})
        else:
            payload = body
            ctx_data = {}

        # Build CapabilityContext — slim=True default for Direct API
        capability_ctx = CapabilityContext(
            slim=ctx_data.get("slim", True),
            tools=ctx_data.get("tools"),
            dry_run=ctx_data.get("dry_run", False),
            trace=ctx_data.get("trace", False),
            correlation_id=ctx_data.get("correlation_id"),
            task_id=ctx_data.get("task_id"),
            profile=ctx_data.get("profile"),         # per-request profile injection
            profile_patch=ctx_data.get("profile_patch"),
            caller=ctx_data.get("caller"),
            subject_ref=ctx_data.get("subject_ref"),
            step=ctx_data.get("step"),
            prior_outputs=ctx_data.get("prior_outputs"),
            state=ctx_data.get("state"),
        )

        # AWS request context
        request_context = event.get("requestContext") or {}
        aws_request_id = (
            getattr(context, "aws_request_id", None)
            or request_context.get("requestId")
        )

        # Execute
        result = asyncio.get_event_loop().run_until_complete(
            _execute_capability(
                capability_id=capability_id,
                payload=payload,
                capability_ctx=capability_ctx,
                aws_request_id=aws_request_id,
                raw_path=raw_path,
            )
        )

        # Response envelope — valid JSON-RPC 2.0 + A2A v1.0
        response_body = {
            "jsonrpc": "2.0",
            "id": aws_request_id,
            "method": "a2a.message",
            "result": {
                "agentId": _agent.name,
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
            "actor": "data-steward-handler",
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
                "error": {"code": -32603, "message": str(e)},
                "metadata": {"taskID": None, "status": "failed"},
            }),
        }
