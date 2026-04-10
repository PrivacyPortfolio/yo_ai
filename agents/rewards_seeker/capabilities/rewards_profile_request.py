# agents/rewards_seeker/capabilities/rewards_profile_request.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    fields = payload.get("fields", [])

    return {
        "message": "Stub rewards profile request.",
        "requestedFields": fields,
        "profile": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
