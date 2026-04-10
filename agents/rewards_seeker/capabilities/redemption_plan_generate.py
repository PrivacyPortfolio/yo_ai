# agents/rewards_seeker/capabilities/redemption_plan_generate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    goals = payload.get("goals", [])

    return {
        "message": "Stub redemption plan generation.",
        "goals": goals,
        "plan": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
