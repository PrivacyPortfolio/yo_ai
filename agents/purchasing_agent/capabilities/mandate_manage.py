# agents/purchasing_agent/capabilities/mandate_manage.py

"""
Capability: Mandate.Manage
Stub — acknowledges mandate action. Next: integrate with payment provider mandate API.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    mandate = payload.get("mandate")
    action = payload.get("action")

    return {
        "capability": "Mandate.Manage",
        "status": "stub",
        "message": "Stub Mandate.Manage response.",
        "mandate": mandate,
        "action": action,
        "status": "dry_run" if ctx.dry_run else "updated",
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
