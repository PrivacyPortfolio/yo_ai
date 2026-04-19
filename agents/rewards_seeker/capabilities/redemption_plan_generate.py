# agents/rewards_seeker/capabilities/redemption_plan_generate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("rewards_seeker")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    goals = payload.get("goals", [])

    LOG.write(
        event_type="redemption_plan_generate.Request",
        payload={
            "goals": goals
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub redemption plan generation.",
        "goals": goals,
        "plan": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
    }
