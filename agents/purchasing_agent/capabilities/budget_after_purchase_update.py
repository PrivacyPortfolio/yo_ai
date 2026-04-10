# agents/purchasing_agent/capabilities/budget_after_purchase_update.py

"""
Capability: Budget-After-Purchase.Update
Stub — deterministic budget subtraction. Next: integrate with budget store.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    amount = payload.get("amount")
    currency = payload.get("currency")

    return {
        "capability": "Budget-After-Purchase.Update",
        "status": "stub",
        "message": "Stub Budget-After-Purchase.Update response.",
        "amount": amount,
        "newBudget": (1000 - (amount or 0)),
        "currency": currency,
        "subjectProfile":  ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
