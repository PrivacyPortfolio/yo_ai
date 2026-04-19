# agents/data_steward/capabilities/data_request_govern.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_steward")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    intended_use = payload.get("intendedUse")
    requested_fields = payload.get("requestedFields", [])

    LOG.write(
        event_type="Data-Request.Govern.Request",
        payload={
            "intendedUse": intended_use,
            "requestedFields": requested_fields,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Data-Request.Govern",
        "status": "stub",
        "message": "Stub data request governance decision.",
        "intendedUse": intended_use,
        "requestedFields": requested_fields,
        "approved": not ctx.get("dry_run"),    # dry_run always returns unapproved
        "reason": "dry_run: approval withheld" if ctx.get("dry_run") else "Stub policy approval.",
        "subjectProfile": ctx.get("subject_profile"),
        "caller": ctx.get("caller"),
        "taskId": ctx.get("task_id"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
    }
