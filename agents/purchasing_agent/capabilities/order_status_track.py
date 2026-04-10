# agents/purchasing_agent/capabilities/order_status_track.py

"""
Capability: Order-Status.Track
Stub — returns fake in-transit status. Next: integrate with order tracking provider.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    order_id = payload.get("orderId")

    return {
        "capability": "Order-Status.Track",
        "status": "stub",
        "message": "Stub Order-Status.Track response.",
        "orderId": order_id,
        "status": "in-transit",
        "eta": "2026-02-21",
        "subjectProfile": ctx.profile,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId": ctx.task_id,
    }
