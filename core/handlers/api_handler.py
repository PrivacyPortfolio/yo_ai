# core/handlers/api_handler.py
#
# Mode: api — agent-scoped OpenAI API handler.
#
# Contract:
#   Receive an API Gateway event whose path follows the convention
#   POST /agents/{agentName}/api/{capability}
#   Extract agentName and capability from the path. Look up the canonical
#   capability name in the capability map. Wrap the payload in a JSON-RPC
#   envelope. Call route_fn. Return an API Gateway proxy response.
#   Know nothing about what the capability does.
#
# Path convention (camelCase):
#   POST /agents/doorKeeper/api/trustAssign
#        ─────────────────────────────────
#        segments: ["agents", "doorKeeper", "api", "trustAssign"]
#                               [1]          [2]       [3]
#
# Capability map:
#   shared/registries/capability_map.yaml — single source of truth.
#   Loaded once at cold start. The capability segment (segments[3]) is
#   the lookup key. No capability paths are hard-coded here.

import json
import uuid
from pathlib import Path
from typing import Awaitable, Callable

import yaml

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("api_handler")

RouteFn = Callable[[dict], Awaitable[dict]]

_CAPABILITY_MAP_PATH = (
    Path(__file__).resolve().parent.parent
    / "shared" / "registries" / "capability_map.yaml"
)


# ── Capability map loader (shared with op_handler) ─────────────────────────

def load_capability_segment_map(map_path: Path = _CAPABILITY_MAP_PATH) -> dict[str, str]:
    # Returns {camelCase_segment: "Canonical.CapabilityName"}
    # e.g. {"trustAssign": "Trust.Assign", "visitorIdentify": "Visitor.Identify"}
    # Returns {} on any failure — handler surfaces a clean 400 per request.
    try:
        if not map_path.exists():
            LOG.write(
                event_type="api_handler.CapabilityMapMissing",
                payload={"path": str(map_path)},
                context=None,
            )
            return {}
        with map_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        seg_map: dict[str, str] = {}
        # Primary source: routes section keyed by agent, each entry has path + capability
        for agent_routes in raw.get("routes", {}).values():
            for route in agent_routes:
                path       = route.get("path", "")
                capability = route.get("capability", "")
                if path and capability:
                    # Extract the capability segment — last non-empty path component
                    segment = path.rstrip("/").split("/")[-1]
                    if segment:
                        seg_map[segment] = capability

        # Flat path_map override section for direct segment → capability entries
        seg_map.update(raw.get("path_map", {}))
        return seg_map

    except Exception as exc:
        LOG.write(
            event_type="api_handler.CapabilityMapLoadFailed",
            payload={"error": str(exc)},
            context=None,
        )
        return {}


# Loaded once per Lambda execution environment (cold start)
_CAPABILITY_SEGMENT_MAP: dict[str, str] = load_capability_segment_map()


# ── Request parser ─────────────────────────────────────────────────────────

def parse_request(event: dict) -> tuple[str, str, dict, dict | None, dict | None, str]:
    # Returns (agent_name, capability_name, payload, caller, subject, correlation_id)
    # Raises ValueError on unrecognisable path, unknown capability, or bad body.

    raw_path = event.get("rawPath", "") or event.get("path", "")
    segments = [s for s in raw_path.split("/") if s]
    # Expected: ["agents", "{agentName}", "api", "{capability}"]

    if len(segments) < 4 or segments[0] != "agents" or segments[2] != "api":
        raise ValueError(
            f"Path must be /agents/{{agentName}}/api/{{capability}}. Got: {raw_path!r}"
        )

    agent_name       = segments[1]   # camelCase agent name, e.g. "doorKeeper"
    capability_seg   = segments[3]   # camelCase capability, e.g. "trustAssign"

    capability_name = _CAPABILITY_SEGMENT_MAP.get(capability_seg)
    if not capability_name:
        raise ValueError(
            f"Unknown capability segment: {capability_seg!r}. "
            f"Known: {sorted(_CAPABILITY_SEGMENT_MAP.keys())}"
        )

    # Body
    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}")

    # Subject — extracted without mutating body
    subject = body.get("subject")
    payload = {k: v for k, v in body.items() if k != "subject"}

    # Caller identity from API Gateway authorizer context
    request_context = event.get("requestContext") or {}
    authorizer      = request_context.get("authorizer") or {}
    caller = {
        "agent_id":      authorizer.get("agentId"),
        "subscriber_id": authorizer.get("subscriberId"),
        "principal_id":  authorizer.get("principalId"),
    } if authorizer else None

    # Correlation ID — seeded from API Gateway requestId
    correlation_id = (
        request_context.get("requestId")
        or event.get("correlationId")
        or str(uuid.uuid4())
    )

    return agent_name, capability_name, payload, caller, subject, correlation_id


# ── Envelope builder ───────────────────────────────────────────────────────

def build_envelope(
    *,
    agent_name: str,
    capability_name: str,
    payload: dict,
    caller: dict | None,
    subject: dict | None,
    correlation_id: str,
) -> dict:
    # JSON-RPC 2.0 / A2A v1.0 envelope.
    # correlation_id → JSON-RPC "id" → generate_message_ids() seed.
    # governance_labels omitted — platform-assigned on responses only.
    return {
        "jsonrpc": "2.0",
        "id":      correlation_id,
        "method":  "a2a.message",
        "params": {
            "caller":     caller,
            "subject":    subject,
            "agent_name": agent_name,
            "message": {
                capability_name: payload,
            },
        },
        "ctx": {
            "startup_mode": "api",
        },
    }


# ── Handler ────────────────────────────────────────────────────────────────

async def api_handler(event: dict, route_fn: RouteFn) -> dict:
    try:
        agent_name, capability_name, payload, caller, subject, correlation_id = \
            parse_request(event)
    except ValueError as exc:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id":      None,
                "error":   {"code": -32600, "message": str(exc)},
            }),
        }

    LOG.write(
        event_type="api_handler.Dispatch",
        payload={
            "agent_name":      agent_name,
            "capability_name": capability_name,
            "correlation_id":  correlation_id,
        },
        context=None,
    )

    envelope    = build_envelope(
        agent_name=agent_name,
        capability_name=capability_name,
        payload=payload,
        caller=caller,
        subject=subject,
        correlation_id=correlation_id,
    )
    result      = await route_fn(envelope)
    status_code = 400 if "error" in result else 200

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }
