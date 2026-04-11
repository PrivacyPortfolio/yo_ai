# agents/rewards_seeker/capabilities/rewards_profile_request.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("rewards_seeker")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    fields = payload.get("fields", [])

    LOG.write(
        event_type="rewards_profile_request.Request",
        payload={
            "fields": fields
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

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
