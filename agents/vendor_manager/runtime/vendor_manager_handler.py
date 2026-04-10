# agents/vendor_manager/runtime/vendor_manager_handler.py

"""
AI-first Lambda handler for the Vendor-Manager agent.

This is the per-agent Direct API handler (Mode B). It bypasses
A2ATransport, the SG routing pipeline, and AgentContext construction.

Use this handler for:
  - Direct capability invocation in development and testing
  - Isolated capability execution without platform overhead
  - AI-first training cycles (call_ai → code replacement)

Use api_handler.py (Mode 3) for:
  - Full platform pipeline with AgentContext and governance
  - CapabilityContext injection with Mode 1 governance simultaneously
  - Orchestrated workflow steps involving multiple agents
  - Capabilities requiring governance label evaluation

Agent lifecycle:
  One slim VendorManagerAgent instance per Lambda execution environment.
  No profile at module level — profile injected per-request via
  capability_ctx.profile in the request body. slim=True: no fingerprints,
  knowledge, or tools.

Capabilities served:
  Org-Profile.Manage → org_profile_manage
"""

import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import yaml

from agents.vendor_manager.runtime.vendor_manager import VendorManagerAgent
from core.base_agent import CapabilityContext
from core.observability.logging.log_bootstrapper import get_logger
from core.utils.ai.ai_transform import call_ai
from core.utils.ai.output_shaper import shape_output
from core.utils.validators.schema_validator import validate_input, load_schema


# ---------------------------------------------------------------------------
# Route loader
# ---------------------------------------------------------------------------

def _load_vm_routes() -> dict[str, str]:
    """
    Load VendorManager capability route map from capability_map.yaml.
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
            vm_routes = raw.get("routes", {}).get("vendor-manager", [])
            for route in vm_routes:
                path = route.get("path", "")
                capability = route.get("capability", "")
                if path and capability:
                    segment = path.rstrip("/").split("/")[-1]
                    if segment:
                        path_map[segment] = capability
            if path_map:
                return path_map
    except Exception as e:
        print(f"[vm_handler] WARNING: capability_map.yaml failed to load: {e}")

    # Hardcoded fallback
    return {
        "orgProfileManage": "Org-Profile.Manage",
    }


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_logger = get_logger("vendor-manager-handler")

# Slim singleton — no profile, no governance artifacts.
# Profile injected per-request from the request body.
_capability_ctx = CapabilityContext(slim=True)
_agent = VendorManagerAgent(capability_ctx=_capability_ctx)

_ROUTES: dict[str, str] = _load_vm_routes()


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

    if input_schema:
        try:
            validate_input(input_schema_name, payload)
        except Exception as e:
            _logger.write({
                "actor": "vendor-manager-handler",
                "event_type": "input_validation_warning",
                "level": "WARNING",
                "message": f"Input validation failed for {capability_id} — proceeding",
                "payload": {"error": str(e), "capability": capability_id},
            })

    result = await _dispatch(
        capability_id=capability_id,
        payload=payload,
        capability_ctx=capability_ctx,
        aws_request_id=aws_request_id,
        raw_path=raw_path,
        output_schema=output_schema,
    )

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
    AI-first training cycle:
      Stage 1: call_ai() handles synthesis         (training wheels)
      Stage 2: run() module handles it in code     (production)
    """
    module_name = _module_name(capability_id)

    try:
        import importlib
        mod = importlib.import_module(f"agents.vendor_manager.{module_name}")
        if hasattr(mod, "run"):
            return await mod.run(payload, None, capability_ctx)
    except ModuleNotFoundError:
        pass
    except Exception as e:
        _logger.write({
            "actor": "vendor-manager-handler",
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
    Direct API Lambda entrypoint for the Vendor-Manager (Mode B).

    Expected API Gateway HTTP API event:
      {
        "rawPath": "/agents/vendorManager/<capabilityPath>",
        "body": "{...}",
        "requestContext": { "requestId": "..." }
      }

    Structured body (preferred):
      {
        "payload": { "action": "fetch", "orgId": "ABC-Corp" },
        "capability_ctx": {
          "slim": true,
          "dry_run": false,
          "profile": { "name": "ABC Corp", "type": "organization", "payload": {} },
          "correlation_id": "...",
          "task_id": "..."
        }
      }

    Flat body (legacy):
      { "action": "fetch", "orgId": "ABC-Corp" }

    Profile is injected per-request via capability_ctx.profile.
    Governance labels are not available in Mode B — use api_handler.py
    (Mode 3) when governance label evaluation is required.
    """
    try:
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

        raw_body = event.get("body") or "{}"
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Invalid JSON body: {e}"}),
            }

        if "payload" in body:
            payload = body.get("payload", {})
            ctx_data = body.get("capability_ctx", {})
        else:
            payload = body
            ctx_data = {}

        capability_ctx = CapabilityContext(
            slim=ctx_data.get("slim", True),
            tools=ctx_data.get("tools"),
            dry_run=ctx_data.get("dry_run", False),
            trace=ctx_data.get("trace", False),
            correlation_id=ctx_data.get("correlation_id"),
            task_id=ctx_data.get("task_id"),
            profile=ctx_data.get("profile"),
            profile_patch=ctx_data.get("profile_patch"),
            caller=ctx_data.get("caller"),
            subject_ref=ctx_data.get("subject_ref"),
            step=ctx_data.get("step"),
            prior_outputs=ctx_data.get("prior_outputs"),
            state=ctx_data.get("state"),
        )

        request_context = event.get("requestContext") or {}
        aws_request_id = (
            getattr(context, "aws_request_id", None)
            or request_context.get("requestId")
        )

        result = asyncio.get_event_loop().run_until_complete(
            _execute_capability(
                capability_id=capability_id,
                payload=payload,
                capability_ctx=capability_ctx,
                aws_request_id=aws_request_id,
                raw_path=raw_path,
            )
        )

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
            "actor": "vendor-manager-handler",
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
