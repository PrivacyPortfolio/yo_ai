# tools/tool_invocation_manager.py
#
# Async tool dispatcher — the agent-facing API for tool invocation.
#
# Sits above ToolRegistry. Adds:
#   - Tool boundary audit log entries (pre-call + post-call)
#   - ToolResult inspection and structured error reporting
#   - dry_run support — skips actual invocation when ctx["dry_run"] is True
#   - Correlation and actor identity in every log entry
#
# Usage in run() modules:
#
#   result = await agent.tool_manager.invoke(
#       tool_name="AccessAdministrator",
#       payload={"action": "grant", "subjectId": subject_id},
#       ctx=ctx,
#   )
#
#   if not result.success:
#       # handle error — result.error describes what went wrong

from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger
from tools.tool_registry import ToolRegistry, ToolResult

_LOG = get_platform_logger("tool_invocation_manager")


class ToolInvocationManager:
    # ── Agent-facing API for tool invocation ──────────────────────────────
    # Wraps ToolRegistry.invoke() with audit logging, dry_run support,
    # and structured ToolResult returns — never raises.
    #
    # Instantiated per-agent, injected with the agent's ToolRegistry.
    # Tool credentials are held by each adapter (from the extended card),
    # not by this manager.

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    async def invoke(
        self,
        tool_name: str,
        payload: dict,
        ctx: YoAiContext,
    ) -> ToolResult:
        # ── Tool boundary audit pattern ────────────────────────────────────
        # 1. Log pre-call entry  — before invocation
        # 2. Skip if dry_run     — return synthetic ok result
        # 3. Invoke tool         — via ToolRegistry
        # 4. Log post-call entry — outcome only, never raw output
        #
        # Raw tool output is never logged — it may contain personal data.

        # 1. Pre-call audit entry
        _LOG.write(
            event_type=f"{tool_name}.Call",
            payload={
                "tool":           tool_name,
                "action":         payload.get("action"),
                "dry_run":        ctx.get("dry_run"),
                "correlation_id": ctx.get("correlation_id"),
                "task_id":        ctx.get("task_id"),
                "actor_kind":     ctx.get("actor_kind"),
                "capability":     ctx.get("capability_id"),
            },
            context=ctx,
        )

        # 2. dry_run: skip actual invocation
        if ctx.get("dry_run"):
            result = ToolResult.ok(
                tool_name=tool_name,
                output={"dry_run": True, "message": f"Tool '{tool_name}' skipped — dry_run=True."},
            )
            self._log_post_call(tool_name, result, ctx, dry_run=True)
            return result

        # 3. Invoke
        try:
            result = await self.registry.invoke(
                name=tool_name,
                payload=payload,
                context={
                    "correlation_id": ctx.get("correlation_id"),
                    "task_id":        ctx.get("task_id"),
                },
            )
        except Exception as exc:
            # ToolRegistry.invoke() should never raise — this is a safety net.
            _LOG.write(
                event_type="tool_invocation_unexpected_error",
                payload={
                    "tool":           tool_name,
                    "correlation_id": ctx.get("correlation_id"),
                    "error":          str(exc),
                },
                context=ctx,
            )
            result = ToolResult.execution_error(tool_name, exc)

        # 4. Post-call audit entry
        self._log_post_call(tool_name, result, ctx, dry_run=False)

        return result

    def _log_post_call(
        self,
        tool_name: str,
        result: ToolResult,
        ctx: YoAiContext,
        dry_run: bool,
    ) -> None:
        _LOG.write(
            event_type=f"{tool_name}.Return",
            payload={
                "tool":           tool_name,
                "success":        result.success,
                "error_type":     result.error_type,
                "error":          result.error,
                "dry_run":        dry_run,
                "correlation_id": ctx.get("correlation_id"),
                "task_id":        ctx.get("task_id"),
                "actor_kind":     ctx.get("actor_kind"),
                "capability":     ctx.get("capability_id"),
                # output intentionally excluded — may contain personal data
            },
            context=ctx,
        )
