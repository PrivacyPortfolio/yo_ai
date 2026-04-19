# agents/complaint_manager/capabilities/stakeholder_notify.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("complaint_manager")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Stakeholder.Notify

    Stub: sends a notification to a stakeholder.
    """

    stakeholder = payload.get("stakeholder")
    complaint_id = payload.get("complaintId")

    LOG.write(
        event_type="stakeholder-notify.Request",
        payload={
            "stakeholder": stakeholder,
            "complaintId": complaint_id
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub stakeholder notification.",
        "stakeholder": stakeholder,
        "complaintId": complaint_id,
        "status": "notified",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId": ctx.get("task_id"),
    }
