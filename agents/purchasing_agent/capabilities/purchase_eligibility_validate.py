# agents/purchasing_agent/capabilities/purchase_eligibility_validate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Purchase-Eligibility.Validate
    Stub — always eligible. Next: evaluate budget, profile, and vendor rules.
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    item = payload.get("item")
    amount = payload.get("amount")

    LOG.write(
        event_type="purchase_eligibility_validate.Request",
        payload={
            "item": item,
            "amount": amount
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Purchase-Eligibility.Validate",
        "status": "stub",
        "message": "Stub Purchase-Eligibility.Validate response.",
        "item": item,
        "amount": amount,
        "eligible": not ctx.get("dry_run"),
        "reason": "dry_run: eligibility withheld" if ctx.get("dry_run") else "Stub approval.",
        "subjectProfile": ctx.get("profile"),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
    }
