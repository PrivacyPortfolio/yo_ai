# agents/purchasing_agent/capabilities/order_status_track.py

"""
Capability: Order-Status.Track
Stub — returns fake in-transit status. Next: integrate with order tracking provider.
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
    order_id = payload.get("orderId")

    LOG.write(
        event_type="order_status_track.Request",
        payload={
            "orderId": order_id
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

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
