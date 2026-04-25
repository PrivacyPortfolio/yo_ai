# core/handlers/op_handler.py
#
# Mode: op — capability-addressed REST handler.
#
# Contract:
#   Receive an API Gateway event whose path follows the convention
#   POST /op/{capability}
#   The caller addresses the capability directly — no agent name in the path.
#   The capability map resolves the canonical capability name identically to
#   api_handler. Wrap the payload in a JSON-RPC envelope. Call route_fn.
#   Return an API Gateway proxy response. Know nothing about which agent
#   owns the capability or what it does.
#
# Path convention (camelCase):
#   POST /op/trustAssign
#        ── ──────────
#        [0]    [1]   capability segment
#
# Capability resolution:
#   Shares load_capability_segment_map() with api_handler — same map,
#   same lookup key, different URL shape.

import json
import uuid
from typing import Awaitable, Callable

from core.handlers.api_handler import load_capability_segment_map
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("op_handler")

RouteFn = Callable[[dict], Awaitable[dict]]

# Loaded once at cold start — same map as api_handler, separate instance
# so op_handler Lambda and api_handler Lambda each own their copy.
_CAPABILITY_SEGMENT_MAP: dict[str, str] = load_capability_segment_map()


# ── Request parser ─────────────────────────────────────────────────────────

def parse_request(event: dict) -> tuple[str, dict, str]:
    # Returns (capability_name, payload, correlation_id)
    # Raises ValueError on unrecognisable path, unknown capability, or bad body.

    raw_path = event.get("rawPath", "") or event.get("path", "")
    segments = [s for s in raw_path.split("/") if s]
    # Expected: ["op", "{capability}"]

    if len(segments) < 2 or segments[0] != "op":
        raise ValueError(
            f"Path must be /op/{{capability}}. Got: {raw_path!r}"
        )

    capability_seg  = segments[1]
    capability_name = _CAPABILITY_SEGMENT_MAP.get(capability_seg)
    if not capability_name:
        raise ValueError(
            f"Unknown capability segment: {capability_seg!r}. "
            f"Known: {sorted(_CAPABILITY_SEGMENT_MAP.keys())}"
        )

    raw_body = event.get("body") or "{}"
    try:
        payload = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}")

    if not isinstance(payload, dict):
        payload = {"input": payload}

    request_context = event.get("requestContext") or {}
    correlation_id  = (
        request_context.get("requestId")
        or event.get("correlationId")
        or str(uuid.uuid4())
    )

    return capability_name, payload, correlation_id


# ── Handler ────────────────────────────────────────────────────────────────

async def handle(event: dict, route_fn: RouteFn) -> dict:
    try:
        capability_name, payload, correlation_id = parse_request(event)
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
        event_type="op_handler.Dispatch",
        payload={
            "capability_name": capability_name,
            "correlation_id":  correlation_id,
        },
        context=None,
    )

    # Envelope shape is identical to api_handler — no agent_name in params
    # since op callers are capability-addressed and agent resolution happens
    # inside YoAiRuntime via the capability map.
    envelope = {
        "jsonrpc": "2.0",
        "id":      correlation_id,
        "method":  "a2a.message",
        "params": {
            "capability": capability_name,
            "payload":    payload,
        },
        "ctx": {
            "startup_mode": "op",
        },
    }

    result      = await route_fn(envelope)
    status_code = 400 if "error" in result else 200

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }
