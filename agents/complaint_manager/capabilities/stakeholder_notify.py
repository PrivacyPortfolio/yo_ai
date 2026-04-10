# agents/complaint_manager/capabilities/stakeholder_notify.py

import time
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Stakeholder.Notify

    Stub: sends a notification to a stakeholder.
    """

    stakeholder = payload.get("stakeholder")
    complaint_id = payload.get("complaintId")

    return {
        "message": "Stub stakeholder notification.",
        "stakeholder": stakeholder,
        "complaintId": complaint_id,
        "status": "notified",
        "timestamp": time.time(),
        "correlationId": ctx.correlation_id,
    }
