# agents/purchasing_agent/capabilities/purchase_history_generate.py

"""
Capability: Purchase-History.Generate
Stub — returns hardcoded history. Next: fetch from purchase history store.
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
    history = payload.get("history")

    LOG.write(
        event_type="purchase_history_generate.Request",
        payload={
            "history": history
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Purchase-History.Generate",
        "status": "stub",
        "message": "Stub Purchase-History.Generate response.",
        "history": [] if ctx.dry_run else [
            {"item": "Example Item A", "price": 19.99, "timestamp": "2026-01-01"},
            {"item": "Example Item B", "price": 42.00, "timestamp": "2026-01-15"},
        ],
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
