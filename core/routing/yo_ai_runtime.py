# core/routing/yo_ai_runtime.py

from typing import Dict, Any

class YoAiRuntime:
    """
    Yo-ai Platform runtime singleton.
    """

    def __init__(self, *, capability_map: Dict[str, Any], tools: Dict[str, Any]):
        """
        Construct the runtime spine.
        - capability_map: dynamic routing table (UCM)
        - tools: RPC adapters (lambda_invoke, http_call, storage, logging, etc.)
        """
        self.capability_map = capability_map
        self.tools = tools
        self._instance_cache = {}       # correlation-scoped state
        self._task_state = {}           # task lifecycle state

    # ------------------------------------------------------------
    # Core entrypoint: semantic routing
    # ------------------------------------------------------------
    async def route(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main semantic router.
        - Extract capability
        - Build contexts
        - Select target agent + dispatch mode
        - Invoke via RPC adapter
        - Return semantic result (not JSON-RPC wrapped)
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Internal A2A direct path (optional)
    # ------------------------------------------------------------
    async def route_internal(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal agent-to-agent dispatch.
        Uses RPC adapters instead of local Python imports.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Task + correlation state
    # ------------------------------------------------------------
    def get_or_create_instance(self, correlation_id: str):
        """Return or create correlation-scoped runtime instance."""
        return self._instance_cache.setdefault(correlation_id, {})

    def update_task_state(self, task_id: str, state: Dict[str, Any]):
        """Persist task lifecycle state."""
        self._task_state[task_id] = state

    # ------------------------------------------------------------
    # Platform logging
    # ------------------------------------------------------------
    async def log_event(self, event: Dict[str, Any]):
        """Write to the official platform log sink."""
        await self.tools["platform_log"].write(event)
