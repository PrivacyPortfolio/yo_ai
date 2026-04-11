# agents/data_anonymizer/capabilities/data_for_purpose_minimize.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_anonymizer")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    purpose = payload.get("purpose")
    fields = payload.get("fields", [])

    LOG.write(
        event_type="data-for-purpose-minimize.Request",
        payload={
            "purpose": purpose,
            "fields": fields
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub data minimization.",
        "purpose": purpose,
        "requiredFields": fields[:2],
        "unnecessaryFields": fields[2:],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
    }
