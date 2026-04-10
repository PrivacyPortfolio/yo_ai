# agents/rewards_seeker/capabilities/rewards_discover.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    query = payload.get("query")

    return {
        "message": "Stub rewards discovery.",
        "query": query,
        "opportunities": [],
        "recommendedActions": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
