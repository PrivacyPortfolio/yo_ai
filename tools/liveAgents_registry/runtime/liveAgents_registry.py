# tools/liveAgents_registry/runtime/liveAgents_registry.py

import time
import inspect
from typing import Dict, Any, List, Optional
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("agent_registry")

def _log(event_type, message, payload=None, agent_ctx=None, capability_ctx=None):
    """
    Unified logging helper for all registry reads/writes.
    Automatically captures caller module when no agent context is provided.
    """
    if agent_ctx:
        LOG.write(
            event_type=event_type,
            message=message,
            payload=payload or {},
            agent_ctx=agent_ctx,
            capability_ctx=capability_ctx,
        )
    else:
        caller = inspect.getmodule(inspect.stack()[2][0]).__name__
        LOG.write(
            event_type=event_type,
            message=message,
            payload={**(payload or {}), "caller": caller},
        )
        
class LiveAgentsRegistry:
    """
    Platform-wide registry of known agents (local or Lambda-backed).

    This registry stores *metadata*, not Python object references,
    so it can be safely queried by any PlatformAgent (Door-Keeper,
    Sentinel, Incident-Responder, etc.) and serialized across transports.
    """

    def __init__(self):
        # agent_id → metadata
        self._agents: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------
    def register_local_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        entrypoint: str,
        description: Optional[str] = None,
    ) -> None:
        """
        Register a local in-process agent.

        Args:
            agent_id: canonical agent identifier
            capabilities: list of capability IDs supported by the agent
            entrypoint: module/function name for local dispatch
            description: optional human-readable description
        """
        self._agents[agent_id] = {
            "type": "local",
            "agent_id": agent_id,
            "capabilities": capabilities,
            "entrypoint": entrypoint,
            "description": description,
            "status": "warm",
            "last_heartbeat": self._now(),
        }

    def register_lambda_agent(
        self,
        agent_id: str,
        function_name: str,
        capabilities: List[str],
        description: Optional[str] = None,
    ) -> None:
        """
        Register a Lambda-backed agent.

        Args:
            agent_id: canonical agent identifier
            function_name: AWS Lambda function name or ARN
            capabilities: list of capability IDs supported by the agent
            description: optional human-readable description
        """
        self._agents[agent_id] = {
            "type": "lambda",
            "agent_id": agent_id,
            "function_name": function_name,
            "capabilities": capabilities,
            "description": description,
            "status": "warm",
            "last_heartbeat": self._now(),
        }


    # ------------------------------------------------------------
    # Heartbeats
    # ------------------------------------------------------------
    def heartbeat(self, agent_id: str, status: str = "warm") -> None:
        """
        Update the agent's heartbeat timestamp and status.
        """
        if agent_id in self._agents:
            self._agents[agent_id]["last_heartbeat"] = self._now()
            self._agents[agent_id]["status"] = status

    # ------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------
    def list_agents(self) -> List[str]:
        """Return a list of all registered agent IDs."""
        return list(self._agents.keys())

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Return metadata for a specific agent."""
        return self._agents.get(agent_id)

    def agents_supporting(self, capability: str) -> List[str]:
        """
        Return all agents that support a given capability.
        """
        return [
            agent_id
            for agent_id, meta in self._agents.items()
            if capability in meta.get("capabilities", [])
        ]

    def running_agents(self) -> List[str]:
        """Return all agents currently marked as warm."""
        return [
            agent_id
            for agent_id, meta in self._agents.items()
            if meta.get("status") == "warm"
        ]

    def all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Return a deep copy of the registry metadata."""
        return {k: dict(v) for k, v in self._agents.items()}

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------
    @staticmethod
    def _now() -> str:
        """Return ISO-like timestamp for heartbeats."""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
