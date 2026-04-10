# agents/rewards_seeker/capabilities/reward_redeem.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    reward_id = payload.get("rewardId")

    return {
        "message": "Stub reward redemption.",
        "rewardId": reward_id,
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
