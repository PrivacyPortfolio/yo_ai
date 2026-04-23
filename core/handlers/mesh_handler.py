# core/handlers/mesh_handler.py
#
# Mode 2 — A2A Direct (mesh) handler.
#
# Contract:
#   Handle internal agent-to-agent calls that arrive via PlatformEventBus
#   rather than HTTP. The calling agent publishes a pre-formed JSON-RPC
#   envelope to the bus; this handler receives it, calls route_fn, and
#   publishes the response back on the bus for the caller to receive.
#   Know nothing about agents, capabilities, or routing decisions.
#
# Two usage patterns:
#
#   1. Bus-mediated (async pub/sub):
#      Caller publishes "a2a.mesh.request" with the envelope as data.
#      MeshHandler subscribes, calls route_fn, publishes "a2a.mesh.response".
#
#   2. Direct call (in-process):
#      Caller has a reference to handle() and awaits it directly.
#      Used in tests and workflow steps that don't need pub/sub overhead.
#
# Bus subscription is set up in register_on_bus(). Call this once at
# platform bootstrap after the event bus exists.

from __future__ import annotations

from typing import Awaitable, Callable

from core.runtime.platform_event_bus import PlatformEventBus

RouteFn = Callable[[dict], Awaitable[dict]]

MESH_REQUEST_EVENT  = "a2a.mesh.request"
MESH_RESPONSE_EVENT = "a2a.mesh.response"


async def handle(envelope: dict, route_fn: RouteFn) -> dict:
    # Direct call path — envelope is already a well-formed dict.
    if not isinstance(envelope, dict):
        return {
            "jsonrpc": "2.0",
            "id":      None,
            "error":   {"code": -32600, "message": "Mesh envelope must be a dict"},
        }
    envelope.setdefault("ctx", {})["startup_mode"] = "direct"
    return await route_fn(envelope)


def register_on_bus(bus: PlatformEventBus, route_fn: RouteFn) -> None:
    # Subscribe to MESH_REQUEST_EVENT on the platform bus.
    # When an envelope arrives, call route_fn and publish the response.
    # Async listener — bus.publish_async() must be used by the caller.
    async def _on_mesh_request(event_type: str, data: dict) -> None:
        envelope = data if isinstance(data, dict) else {}
        response = await handle(envelope, route_fn)
        await bus.publish_async(
            MESH_RESPONSE_EVENT,
            data=response,
            source="mesh_handler",
        )

    bus.subscribe(MESH_REQUEST_EVENT, _on_mesh_request, owner="mesh_handler")
