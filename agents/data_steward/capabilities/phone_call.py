# agents/data_steward/capabilities/phone_call.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_steward")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    to = payload.get("to")
    message = payload.get("message")

    LOG.write(
        event_type="Phone.Call.Request",
        payload={
            "to":               to,
            "message":          message,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Phone.Call",
        "status": "stub",
        "message": "Stub outbound phone call placed.",
        "to": to,
        "content": message,
        "callerProfile": ctx.get("profile"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId": ctx.get("task_id"),
    }
