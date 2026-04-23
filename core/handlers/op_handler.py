# core/handlers/op_handler.py
#
# Mode 5 — REST Operation handler.
#
# Contract:
#   Receive an API Gateway event whose rawPath follows the /op/{capability}
#   convention. Extract the capability name from the path, wrap the body
#   payload in a minimal JSON-RPC envelope, and call route_fn. Return an
#   API Gateway proxy response. Know nothing about what the capability does.
#
# REST operations are thin wrappers over the A2A pipeline — the envelope
# they produce is identical in shape to what api_handler produces.
# The difference is path convention: /op/{CapabilityName} is a direct
# capability address with no agent-name segment.

from __future__ import annotations

import json
import uuid
from typing import Awaitable, Callable

RouteFn = Callable[[dict], Awaitable[dict]]


def _parse(event: dict) -> tuple[str, dict, str]:
    # Returns (capability_name, payload, correlation_id)
    raw_path = event.get("rawPath", "") or event.get("path", "")
    segments = [s for s in raw_path.split("/") if s]
    # /op/{CapabilityName} — capability is the segment after "op"
    capability_name = segments[1] if len(segments) >= 2 else ""

    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        body = {}

    request_context = event.get("requestContext") or {}
    correlation_id  = (
        request_context.get("requestId")
        or event.get("correlationId")
        or str(uuid.uuid4())
    )

    return capability_name, body, correlation_id


async def handle(event: dict, route_fn: RouteFn) -> dict:
    capability_name, payload, correlation_id = _parse(event)

    if not capability_name:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing capability name in /op path"}),
        }

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

    response    = await route_fn(envelope)
    status_code = 400 if "error" in response else 200

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }
