# agents/rewards_seeker/capabilities/promo_eligibility_verify.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("rewards_seeker")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    promo = payload.get("promotion")

    LOG.write(
        event_type="promo_eligibility_verify.Request",
        payload={
            "promotion": promo
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub promotional eligibility verification.",
        "promotion": promo,
        "eligible": False,
        "evidence": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
    }
