# agents/purchasing_agent/capabilities/budget_check.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Budget.Check
    Stub — always returns 1000. Next: fetch real balance from vault/budget store.
      Returns indeterminate status when profile is None (anonymous caller).
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    amount = payload.get("amount")
    currency = payload.get("currency")

    LOG.write(
        event_type="budget_check.Request",
        payload={
            "amount": amount,
            "currency": currency
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Budget.Check",
        "message": "Stub Budget.Check response.",
        "eligible": ctx.get("profile") is not None,
        "availableBudget": 1000 if ctx.get("profile") is not None else None,
        "amount": amount,
        "currency": currency,
        "status": "available" if ctx.get("profile") is not None else "indeterminate",
        "reason": None if ctx.get("profile") is not None else "No subject profile provided.",
        "required": None if ctx.get("profile") is not None else ["profile"],
        "subjectProfile": ctx.get("profile"),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
    }
