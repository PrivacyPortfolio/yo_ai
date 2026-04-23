# core/handlers/mode_discriminator.py
#
# Contract:
#   Inspect an inbound event and return the startup_mode string that tells
#   the Lambda entrypoint which handler to invoke. Know nothing about
#   agents, capabilities, or routing decisions.
#
# Startup modes:
#   "a2a"      — API Gateway HTTP proxy with rawPath="/a2a"
#                JSON-RPC envelope in body, full A2A pipeline
#   "api"      — API Gateway HTTP proxy with OpenAPI path convention
#                /agents/{agentName}/{capabilityPath}
#   "app"      — Starlette / MCP request object (has async .json())
#   "mesh"     — Direct dict invocation carrying a pre-formed envelope
#                (internal A2A direct, no HTTP layer)
#   "op"       — REST operation, rawPath="/op/..." per-capability endpoint
#   "unknown"  — Cannot determine mode; caller should return 400

from __future__ import annotations

from typing import Any


StartupMode = str   # "a2a" | "api" | "app" | "mesh" | "op" | "unknown"


def discriminate(event: Any) -> StartupMode:
    # Starlette / FastAPI Request — has async .json(), no dict interface
    if not isinstance(event, dict):
        if hasattr(event, "json"):
            return "app"
        return "unknown"

    raw_path: str = event.get("rawPath", "") or event.get("path", "")

    # Explicit A2A endpoint
    if raw_path == "/a2a":
        return "a2a"

    # REST operation endpoint
    if raw_path.startswith("/op/") or raw_path == "/op":
        return "op"

    # OpenAPI path convention: /agents/{agentName}/{capabilityPath}
    if raw_path.startswith("/agents/"):
        return "api"

    # Direct dict invocation (mesh / internal A2A) — no HTTP routing keys,
    # but carries a jsonrpc field or a capability field
    if "jsonrpc" in event or "capability" in event:
        return "mesh"

    # API Gateway event with requestContext but no recognisable path
    # — treat as a2a and let the handler return a clean error
    if "requestContext" in event:
        return "a2a"

    return "unknown"
