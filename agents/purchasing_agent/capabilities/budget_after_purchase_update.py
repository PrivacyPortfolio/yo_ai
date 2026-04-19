# agents/purchasing_agent/capabilities/budget_after_purchase_update.py


from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    """
    Capability: Budget-After-Purchase.Update
    Stub — deterministic budget subtraction. Next: integrate with budget store.
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    amount = payload.get("amount")
    currency = payload.get("currency")

    LOG.write(
        event_type="budget_after_purchase_update.Request",
        payload={
            "amount": amount,
            "currency": currency
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Budget-After-Purchase.Update",
        "status": "stub",
        "message": "Stub Budget-After-Purchase.Update response.",
        "amount": amount,
        "newBudget": (1000 - (amount or 0)),
        "currency": currency,
        "subjectProfile":  ctx.get("profile"),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
    }
