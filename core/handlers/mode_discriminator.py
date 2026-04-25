# core/handlers/mode_discriminator.py
#
# Contract:
#   Inspect an inbound event and return the startup_mode that tells
#   lambda_handler which handler to invoke. Read the path suffix only.
#   Know nothing about agents, capabilities, or routing decisions.
#
# URL convention (camelCase segments):
#   /a2a                                — shared A2A root (legacy / external callers)
#   /agents/{agentName}/a2a             — agent-scoped A2A
#   /agents/{agentName}/api/{capability}— agent-scoped OpenAI API
#   /agents/{agentName}/app             — agent-scoped MCP / Starlette
#   /op/{capability}                    — capability-addressed REST (no agent in path)
#
# mesh has no Lambda / API Gateway path — in-process via PlatformEventBus only.
#
# Startup modes returned:
#   "a2a"      — JSON-RPC envelope in body, full A2A pipeline
#   "api"      — OpenAI API convention, agent + capability in path
#   "app"      — Starlette / MCP async request object
#   "op"       — REST, capability-addressed (no agent segment)
#   "mesh"     — direct dict with jsonrpc/capability field (no HTTP)
#   "unknown"  — unrecognisable; caller returns 400

from __future__ import annotations

from typing import Any

StartupMode = str  # "a2a" | "api" | "app" | "op" | "mesh" | "unknown"


def discriminate(event: Any) -> StartupMode:
    # Starlette / MCP Request — has async .json(), not a dict
    if not isinstance(event, dict):
        return "app" if hasattr(event, "json") else "unknown"

    raw_path: str = event.get("rawPath", "") or event.get("path", "")
    segments = [s for s in raw_path.split("/") if s]
    # segments examples:
    #   /a2a                              → ["a2a"]
    #   /agents/doorKeeper/a2a            → ["agents", "doorKeeper", "a2a"]
    #   /agents/doorKeeper/api/trustAssign→ ["agents", "doorKeeper", "api", "trustAssign"]
    #   /agents/doorKeeper/app            → ["agents", "doorKeeper", "app"]
    #   /op/trustAssign                   → ["op", "trustAssign"]

    # Shared /a2a root — kept for external / legacy callers
    if segments == ["a2a"]:
        return "a2a"

    # /op/{capability} — capability-addressed REST, no agent segment
    if len(segments) >= 1 and segments[0] == "op":
        return "op"

    # /agents/{agentName}/{mode}[/{capability}]
    if len(segments) >= 3 and segments[0] == "agents":
        mode_segment = segments[2]
        if mode_segment == "a2a": return "a2a"
        if mode_segment == "api": return "api"
        if mode_segment == "app": return "app"

    # Direct dict invocation (mesh) — no HTTP path, carries envelope fields
    if "jsonrpc" in event or "capability" in event:
        return "mesh"

    return "unknown"
