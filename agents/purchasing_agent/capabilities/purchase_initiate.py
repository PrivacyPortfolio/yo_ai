# agents/purchasing_agent/capabilities/purchase_initiate.py

"""
Capability: Purchase.Initiate
Stub — returns pending status. Next: integrate with AP2 purchase flow / Stripe / PayPal.
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
    item = payload.get("item")
    price = payload.get("price")
    vendor = payload.get("vendor")

    LOG.write(
        event_type="purchase_initiate.Request",
        payload={
            "item": item,
            "price": price,
            "vendor": vendor
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Purchase.Initiate",
        "status": "stub",
        "message": "Stub Purchase.Initiate response.",
        "item": item,
        "price": price,
        "vendor": vendor,
        "status": "dry_run" if ctx.dry_run else "pending",
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
