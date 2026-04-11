# agents/purchasing_agent/capabilities/return_or_refund_initiate.py

"""
Capability: Return-Or-Refund.Initiate
Initiates a return or refund process for a prior purchase.

Stage: Stub — acknowledges initiation. Next: integrate with vendor return portal
       or payment provider refund API. Trigger Purchase-Issues.Resolve for disputes.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — { "item": str, "reason": str, "orderId": str, ... }
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    item = payload.get("item")
    reason = payload.get("reason")
    order_id = payload.get("orderId")

    LOG.write(
        event_type="return_or_refund_initiate.Request",
        payload={
            "item": item,
            "reason": reason,
            "orderId": order_id
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Return-Or-Refund.Initiate",
        "status": "stub",
        "message": "Stub return/refund initiated." if not ctx.dry_run else "Stub dry_run — no action taken.",
        "item": item,
        "reason": reason,
        "orderId": order_id,
        "initiated": not ctx.dry_run,
        "subjectProfile": ctx.profile,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
