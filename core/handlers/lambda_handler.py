# core/handlers/lambda_handler.py
#
# Unified Lambda / HTTP entrypoint for the Yo-ai Platform.
#
# Contract:
#   Receive any inbound event (Lambda proxy, Starlette request, direct dict).
#   Determine its startup mode. Delegate to the correct mode handler.
#   Return a response. Know nothing about agents, capabilities, routing,
#   or what route_fn is backed by.
#
# Cold start:
#   bootstrap() is called once at module load. It constructs every stateful
#   platform object (SG, IR, transport, runtime, event bus) and returns
#   route_fn — a plain async callable. This file never imports an agent class.
#
# Warm invocations:
#   bootstrap() is idempotent — returns the cached route_fn immediately.

import json

from core.runtime.platform_bootstrap import bootstrap
from core.handlers.mode_discriminator import discriminate
from core.handlers.a2a_handler   import handle as handle_a2a
from core.handlers.api_handler   import api_handler as handle_api
from core.handlers.app_handler   import handle as handle_app
from core.handlers.mesh_handler  import handle as handle_mesh
from core.handlers.op_handler    import handle as handle_op

# Cold-start: wire all platform singletons and get route_fn
_route_fn = bootstrap()

# Well-known agent directory URL — no agent import needed
AGENT_DIRECTORY_URL = "https://privacyportfolio.com/.well-known/agent.json"


async def yo_ai_handler(event, context=None):
    # Non-A2A paths — served before mode discrimination
    if isinstance(event, dict):
        raw_path = event.get("rawPath", "") or event.get("path", "")

        if raw_path == "/.well-known/agent-card.json":
            return {
                "statusCode": 301,
                "headers": {
                    "Location":      AGENT_DIRECTORY_URL,
                    "Cache-Control": "public, max-age=3600",
                },
                "body": "",
            }

        if raw_path == "/":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/plain"},
                "body": (
                    f"Yo-ai Platform\n"
                    f"Agent directory: {AGENT_DIRECTORY_URL}\n"
                    f"A2A endpoint:    POST /a2a\n"
                ),
            }

        if raw_path == "/agent/extended":
            return {
                "statusCode": 501,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error":   "not_implemented",
                    "message": f"{raw_path} is not yet wired to a Door-Keeper capability.",
                }),
            }

    # Mode discrimination — one branch per startup mode
    mode = discriminate(event)

    if mode == "a2a":
        return await handle_a2a(event, _route_fn)

    if mode == "api":
        return await handle_api(event, _route_fn)

    if mode == "app":
        return await handle_app(event, _route_fn)

    if mode == "mesh":
        envelope = event  # mesh events arrive as pre-formed dicts
        return await handle_mesh(envelope, _route_fn)

    if mode == "op":
        return await handle_op(event, _route_fn)

    # Unknown mode
    return {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "jsonrpc": "2.0",
            "id":      None,
            "error":   {"code": -32600, "message": "Unrecognised request format"},
        }),
    }
