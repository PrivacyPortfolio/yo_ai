# core/handlers/app_handler.py
#
# Mode 4 — Starlette / MCP handler.
#
# Contract:
#   Receive a Starlette Request object (or any object with an async .json()
#   method). Read the body asynchronously. Treat the parsed body as a
#   JSON-RPC envelope and call route_fn. Return the raw response dict —
#   Starlette callers handle their own HTTP response construction.
#   Know nothing about agents, capabilities, or routing decisions.

from __future__ import annotations

import json
from typing import Any, Awaitable, Callable

RouteFn = Callable[[dict], Awaitable[dict]]


async def handle(request: Any, route_fn: RouteFn) -> dict:
    try:
        envelope = await request.json()
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id":      None,
            "error":   {"code": -32700, "message": f"Parse error: {exc}"},
        }

    if not isinstance(envelope, dict):
        return {
            "jsonrpc": "2.0",
            "id":      None,
            "error":   {"code": -32600, "message": "Request body must be a JSON object"},
        }

    envelope.setdefault("ctx", {})["startup_mode"] = "starlette"
    return await route_fn(envelope)
