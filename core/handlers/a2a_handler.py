# core/handlers/a2a_handler.py
#
# Mode 1 — A2A HTTP handler.
#
# Contract:
#   Receive an API Gateway HTTP proxy event whose body contains a
#   JSON-RPC 2.0 / A2A v1.0 envelope. Extract the envelope from the body.
#   Call route_fn. Return an API Gateway proxy response. Know nothing about
#   agents, capabilities, or routing decisions.
#
# route_fn is injected at Lambda cold start by platform_bootstrap.bootstrap().
# It is A2ATransport.handle_a2a — a plain async callable.

from __future__ import annotations

import json
from typing import Awaitable, Callable

RouteFn = Callable[[dict], Awaitable[dict]]


def _extract_envelope(event: dict) -> dict | None:
    body = event.get("body")
    if body is None:
        # Direct dict invocation — treat the event itself as the envelope
        return event
    try:
        return json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError as exc:
        return {
            "jsonrpc": "2.0",
            "id":      None,
            "error":   {"code": -32700, "message": f"Parse error: {exc}"},
        }


async def handle(event: dict, route_fn: RouteFn) -> dict:
    envelope = _extract_envelope(event)

    # If extraction itself produced an error envelope, return it directly
    if "error" in envelope and "jsonrpc" in envelope:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(envelope),
        }

    # Stamp startup_mode so ctx_from_envelope picks it up
    envelope.setdefault("ctx", {})["startup_mode"] = "a2a"

    response    = await route_fn(envelope)
    status_code = 400 if "error" in response else 200

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }
