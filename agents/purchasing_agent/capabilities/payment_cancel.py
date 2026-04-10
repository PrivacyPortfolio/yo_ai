# agents/purchasing_agent/capabilities/payment_cancel.py

"""
Capability: Payment.Cancel
Stub — acknowledges cancellation. Next: integrate with payment provider cancel API.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — AgentContext | None  (governance, startup_mode, caller)
    """
    payment_id = payload.get("paymentId")

    return {
        "capability": "Payment.Cancel",
        "status": "stub",
        "message": "Stub Payment.Cancel response.",
        "paymentId": payment_id,
        "status": "dry_run" if ctx.dry_run else "cancelled",
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
