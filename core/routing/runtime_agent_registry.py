# core/routing/runtime_agent_registry.py
#
# Platform-wide registry of known agents (local or Lambda-backed).
#
# Stores metadata, not Python object references — safe to query from any
# PlatformAgent and serializable across transports.
#
# Module-level singleton (REGISTRY) is the shared instance used by all
# callers. Import it directly:
#
#   from core.routing.runtime_agent_registry import REGISTRY
#

import time
import inspect
from typing import Any, Dict, List, Optional

from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("runtime_agent_registry")


# ── Logging helper ─────────────────────────────────────────────────────────

def _log(
    event_type: str,
    payload: dict | None = None,
    ctx: YoAiContext | None = None,
) -> None:
    # ── ctx is a YoAiContext dict — passed as context= to LOG.write ────────
    # When no ctx is available, captures caller module for traceability.
    if ctx:
        LOG.write(
            event_type=event_type,
            payload=payload or {},
            context=ctx,
        )
    else:
        try:
            caller = inspect.getmodule(inspect.stack()[2][0]).__name__
        except Exception:
            caller = "unknown"
        LOG.write(
            event_type=event_type,
            payload={**(payload or {}), "caller": caller},
            context=None,
        )


# ── RuntimeAgentRegistry ───────────────────────────────────────────────────

class RuntimeAgentRegistry:

    def __init__(self) -> None:
        self._agents: Dict[str, Dict[str, Any]] = {}

    # ── Registration ───────────────────────────────────────────────────────

    def register_local_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        entrypoint: str,
        description: Optional[str] = None,
        ctx: YoAiContext | None = None,
    ) -> None:
        self._agents[agent_id] = {
            "type":           "local",
            "agent_id":       agent_id,
            "capabilities":   capabilities,
            "entrypoint":     entrypoint,
            "description":    description,
            "status":         "warm",
            "last_heartbeat": self._now(),
        }
        _log("AgentRegistry.RegisterLocal", {"agent_id": agent_id, "capabilities": capabilities}, ctx)

    def register_lambda_agent(
        self,
        agent_id: str,
        function_name: str,
        capabilities: List[str],
        description: Optional[str] = None,
        ctx: YoAiContext | None = None,
    ) -> None:
        self._agents[agent_id] = {
            "type":           "lambda",
            "agent_id":       agent_id,
            "function_name":  function_name,
            "capabilities":   capabilities,
            "description":    description,
            "status":         "warm",
            "last_heartbeat": self._now(),
        }
        _log("AgentRegistry.RegisterLambda", {"agent_id": agent_id, "function_name": function_name}, ctx)

    def register(self, payload: dict, ctx: YoAiContext | None = None) -> None:
        # ── Generic registration from a payload dict ───────────────────────
        # Dispatches to register_local_agent or register_lambda_agent
        # based on payload["type"].
        agent_type = payload.get("type", "local")
        agent_id   = payload.get("agent_id", "")
        if not agent_id:
            _log("AgentRegistry.RegisterError", {"error": "missing agent_id", "payload": payload}, ctx)
            return
        if agent_type == "lambda":
            self.register_lambda_agent(
                agent_id=agent_id,
                function_name=payload.get("function_name", ""),
                capabilities=payload.get("capabilities", []),
                description=payload.get("description"),
                ctx=ctx,
            )
        else:
            self.register_local_agent(
                agent_id=agent_id,
                capabilities=payload.get("capabilities", []),
                entrypoint=payload.get("entrypoint", ""),
                description=payload.get("description"),
                ctx=ctx,
            )

    # ── Heartbeat / lifecycle ──────────────────────────────────────────────

    def heartbeat(
        self,
        agent_id: str,
        instance_id: str | None = None,
        ts: str | None = None,
        status: str = "warm",
        ctx: YoAiContext | None = None,
    ) -> None:
        if agent_id in self._agents:
            self._agents[agent_id]["last_heartbeat"] = ts or self._now()
            self._agents[agent_id]["status"]         = status
            if instance_id:
                self._agents[agent_id]["instance_id"] = instance_id
        _log("AgentRegistry.Heartbeat", {"agent_id": agent_id, "status": status}, ctx)

    def mark_stopped(
        self,
        agent_id: str,
        instance_id: str | None = None,
        ts: str | None = None,
        ctx: YoAiContext | None = None,
    ) -> None:
        if agent_id in self._agents:
            self._agents[agent_id]["status"]         = "stopped"
            self._agents[agent_id]["last_heartbeat"] = ts or self._now()
            if instance_id:
                self._agents[agent_id]["instance_id"] = instance_id
        _log("AgentRegistry.Stopped", {"agent_id": agent_id}, ctx)

    # ── Queries ────────────────────────────────────────────────────────────

    def get_agent(
        self,
        agent_id: str,
        ctx: YoAiContext | None = None,
    ) -> Optional[Dict[str, Any]]:
        _log("AgentRegistry.Read", {"agent_id": agent_id}, ctx)
        return self._agents.get(agent_id)

    def get_agents(self, ctx: YoAiContext | None = None) -> Dict[str, Dict[str, Any]]:
        _log("AgentRegistry.ReadAll", {}, ctx)
        return {k: dict(v) for k, v in self._agents.items()}

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())

    def agents_supporting(self, capability: str) -> List[str]:
        return [
            agent_id
            for agent_id, meta in self._agents.items()
            if capability in meta.get("capabilities", [])
        ]

    def running_agents(self) -> List[str]:
        return [
            agent_id
            for agent_id, meta in self._agents.items()
            if meta.get("status") == "warm"
        ]

    def all_metadata(self) -> Dict[str, Dict[str, Any]]:
        return {k: dict(v) for k, v in self._agents.items()}

    # ── Internal ───────────────────────────────────────────────────────────

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ── Module-level singleton ─────────────────────────────────────────────────
# All callers import this directly.

REGISTRY = RuntimeAgentRegistry()
