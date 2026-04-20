# tools/tool_registry.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("tool_registry")


# ── ToolResult ─────────────────────────────────────────────────────────────

@dataclass
class ToolResult:
    # ── Structured result returned by ToolRegistry.invoke() ────────────────
    # Always returned — never raises. Callers inspect success to determine
    # whether to use output or handle the error.
    #
    # Tool boundary audit pattern (in run() modules):
    #   tim.invoke() handles pre-call and post-call logging via
    #   ToolInvocationManager — no logging needed in run() itself.

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


# ── ToolAdapter Protocol ───────────────────────────────────────────────────

@runtime_checkable
class ToolAdapter(Protocol):
    # ── All tool adapters must implement execute() ─────────────────────────
    # Must return a dict. Should not raise — any exception that escapes is
    # caught by ToolRegistry.invoke() and wrapped in a ToolResult.
    async def execute(self, payload: dict, context: dict) -> dict:
        ...


# ── ToolRegistry ───────────────────────────────────────────────────────────

class ToolRegistry:
    # ── Shared registry for all tool adapters ─────────────────────────────
    # Agents invoke tools by name via invoke().
    # invoke() always returns a ToolResult — never raises.

    def __init__(self) -> None:
        self._adapters: Dict[str, ToolAdapter] = {}

    def register(self, name: str, adapter: ToolAdapter) -> None:
        # ── Overwrites silently on re-registration — allows lazy reload ────
        if name in self._adapters:
            LOG.write(
                event_type="ToolRegistry.Overwrite",
                payload={"tool_name": name},
                context=None,
            )
        self._adapters[name] = adapter
        LOG.write(
            event_type="ToolRegistry.Registered",
            payload={"tool_name": name},
            context=None,
        )

    def get(self, name: str) -> Optional[ToolAdapter]:
        return self._adapters.get(name)

    def list_tools(self) -> list[str]:
        return list(self._adapters.keys())

    async def invoke(
        self,
        name: str,
        payload: dict,
        context: dict,
    ) -> ToolResult:
        # ── Never raises — all failures returned as ToolResult ─────────────
        # The calling run() module's ToolInvocationManager handles
        # pre-call and post-call audit logging.
        adapter = self.get(name)
        if adapter is None:
            LOG.write(
                event_type="ToolRegistry.NotFound",
                payload={"tool_name": name},
                context=None,
            )
            return ToolResult.not_found(name)

        try:
            raw_output = await adapter.execute(payload, context)
        except Exception as exc:
            LOG.write(
                event_type="ToolRegistry.ExecutionError",
                payload={"tool_name": name, "error": str(exc)},
                context=None,
            )
            return ToolResult.execution_error(name, exc)

        if not isinstance(raw_output, dict):
            detail = f"Tool '{name}' returned {type(raw_output).__name__}, expected dict."
            LOG.write(
                event_type="ToolRegistry.BadOutput",
                payload={"tool_name": name, "detail": detail},
                context=None,
            )
            return ToolResult.bad_output(name, detail)

        return ToolResult.ok(name, raw_output)
