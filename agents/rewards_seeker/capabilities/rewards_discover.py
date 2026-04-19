# agents/rewards_seeker/capabilities/rewards_discover.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("rewards_seeker")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    query = payload.get("query")

    LOG.write(
        event_type="rewards_discover.Request",
        payload={
            "query": query
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub rewards discovery.",
        "query": query,
        "opportunities": [],
        "recommendedActions": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
    }
