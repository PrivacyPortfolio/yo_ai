# agents/data_steward/capabilities/phone_answer.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_steward")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    caller_id = payload.get("callerId")

    LOG.write(
        event_type="Phone.Answer.Request",
        payload={
            "callerId": caller_id,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Phone.Answer",
        "status": "stub",
        "message": "Stub inbound call answered.",
        "callerId": caller_id,
        "verified": True,
        "purpose": "stubbed-purpose",
        "startupMode": ctx.get("startup_mode"),
        "correlationId": ctx.get("correlation_id"),
        "taskId": ctx.get("task_id"),
    }
