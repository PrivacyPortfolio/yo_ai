# agents/purchasing_agent/capabilities/mandate_manage.py

"""
Capability: Mandate.Manage
Stub — acknowledges mandate action. Next: integrate with payment provider mandate API.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    mandate = payload.get("mandate")
    action = payload.get("action")

    LOG.write(
        event_type="mandate_manage.Request",
        payload={
            "mandate": mandate,
            "action": action
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

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
