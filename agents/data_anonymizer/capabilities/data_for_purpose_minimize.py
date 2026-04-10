# agents/data_anonymizer/capabilities/data_for_purpose_minimize.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    purpose = payload.get("purpose")
    fields = payload.get("fields", [])

    return {
        "message": "Stub data minimization.",
        "purpose": purpose,
        "requiredFields": fields[:2],
        "unnecessaryFields": fields[2:],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
    }
