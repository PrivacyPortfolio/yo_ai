# tools/tool_registry.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("tool_registry")


# ---------------------------------------------------------------------------
# ToolResult — structured return from every tool invocation
# ---------------------------------------------------------------------------

@dataclass
class ToolResult:
    """
    Structured result returned by ToolRegistry.invoke().

    Always returned — never raises. Callers inspect success to determine
    whether to use output or handle the error.

    Usage in run() modules (per LOGGING.md tool boundary pattern):
        agent_ctx.log(event_type="VaultAdapter.Call", ...)     # pre-call
        result = await registry.invoke("VaultAdapter", payload, ctx)
        agent_ctx.log(event_type="VaultAdapter.Return", ...)   # post-call

        if not result.success:
            # handle error — result.error describes what went wrong
    """
    success:    bool
    output:     Dict[str, Any] = field(default_factory=dict)
    error:      Optional[str]  = None
    tool_name:  Optional[str]  = None
    error_type: Optional[str]  = None   # "not_found" | "execution_error" | "bad_output"

    @classmethod
    def ok(cls, tool_name: str, output: dict) -> "ToolResult":
        return cls(success=True, output=output, tool_name=tool_name)

    @classmethod
    def not_found(cls, tool_name: str) -> "ToolResult":
        return cls(
            success=False,
            error=f"Tool not found: '{tool_name}'",
            tool_name=tool_name,
            error_type="not_found",
        )

    @classmethod
    def execution_error(cls, tool_name: str, exc: Exception) -> "ToolResult":
        return cls(
            success=False,
            error=str(exc),
            tool_name=tool_name,
            error_type="execution_error",
        )

    @classmethod
    def bad_output(cls, tool_name: str, detail: str) -> "ToolResult":
        return cls(
            success=False,
            error=detail,
            tool_name=tool_name,
            error_type="bad_output",
        )


# ---------------------------------------------------------------------------
# ToolAdapter Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class ToolAdapter(Protocol):
    """
    Protocol all tool adapters must implement.

    execute() receives the tool payload and a context dict.
    It must return a dict. It should not raise — use ToolResult
    for structured error returns. Any exception that does escape
    is caught by ToolRegistry.invoke() and wrapped in a ToolResult.
    """
    async def execute(self, payload: dict, context: dict) -> dict:
        ...


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """
    Shared registry for all tool adapters.
    Agents use this to invoke tools by name via invoke().

    invoke() always returns a ToolResult — never raises.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, ToolAdapter] = {}

    def register(self, name: str, adapter: ToolAdapter) -> None:
        """
        Register a tool adapter by name.

        If a tool with this name is already registered, logs a warning
        and overwrites — does not raise. This allows lazy reload without
        crashing the agent.
        """
        if name in self._adapters:
            logger.warning(
                "ToolRegistry: '%s' already registered — overwriting.", name
            )
        self._adapters[name] = adapter
        logger.debug("ToolRegistry: registered tool '%s'.", name)

    def get(self, name: str) -> Optional[ToolAdapter]:
        """
        Return the adapter for a tool name, or None if not registered.
        Does not raise.
        """
        return self._adapters.get(name)

    def list_tools(self) -> list[str]:
        """Return names of all registered tools."""
        return list(self._adapters.keys())

    async def invoke(
        self,
        name: str,
        payload: dict,
        context: dict,
    ) -> ToolResult:
        """
        Invoke a tool by name and return a ToolResult.

        Never raises. All failures — not found, execution error, bad output —
        are returned as ToolResult(success=False, ...).

        The calling run() module is responsible for:
          1. Logging before the call (audit bridge pre-call)
          2. Inspecting the result
          3. Logging after the call (audit bridge post-call)
          per LOGGING.md tool boundary pattern.
        """
        adapter = self.get(name)
        if adapter is None:
            logger.warning("ToolRegistry: invoke called for unknown tool '%s'.", name)
            return ToolResult.not_found(name)

        try:
            raw_output = await adapter.execute(payload, context)
        except Exception as exc:
            logger.error(
                "ToolRegistry: execution error for tool '%s' — %s", name, exc
            )
            return ToolResult.execution_error(name, exc)

        # Validate output is a dict
        if not isinstance(raw_output, dict):
            detail = (
                f"Tool '{name}' returned {type(raw_output).__name__}, expected dict."
            )
            logger.error("ToolRegistry: %s", detail)
            return ToolResult.bad_output(name, detail)

        return ToolResult.ok(name, raw_output)
