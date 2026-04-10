# agents/rewards_seeker/capabilities/promo_eligibility_verify.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    promo = payload.get("promotion")

    return {
        "message": "Stub promotional eligibility verification.",
        "promotion": promo,
        "eligible": False,
        "evidence": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
