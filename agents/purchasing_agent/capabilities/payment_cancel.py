# agents/purchasing_agent/capabilities/payment_cancel.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Payment.Cancel
    Stub — acknowledges cancellation. Next: integrate with payment provider cancel API.
    Args:
      payload       — capability-specific input fields
      ctx           — AgentContext | None  (governance, startup_mode, caller)
    """
    payment_id = payload.get("paymentId")

    LOG.write(
        event_type="payment_cancel.Request",
        payload={
            "paymentId": payment_id
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Payment.Cancel",
        "status": "stub",
        "message": "Stub Payment.Cancel response.",
        "paymentId": payment_id,
        "status": "dry_run" if ctx.get("dry_run") else "cancelled",
        "subjectProfile": ctx.get("profile"),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
    }
