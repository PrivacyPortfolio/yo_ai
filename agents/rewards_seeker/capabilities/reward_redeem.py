# agents/rewards_seeker/capabilities/reward_redeem.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("rewards_seeker")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    reward_id = payload.get("rewardId")

    LOG.write(
        event_type="reward_redeem.Request",
        payload={
            "rewardId": reward_id
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub reward redemption.",
        "rewardId": reward_id,
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
