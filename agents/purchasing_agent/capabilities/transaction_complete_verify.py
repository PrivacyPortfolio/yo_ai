# agents/purchasing_agent/capabilities/transaction_complete_verify.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Transaction-Complete.Verify
    Verifies that a transaction has completed successfully end-to-end.

    Stub — always verified. Next: check transaction status from payment
       provider, verify receipt matches order, confirm vendor fulfillment.
    Args:
      payload       — { "transactionId": str, ... }
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    transaction_id = payload.get("transactionId")

    LOG.write(
        event_type="transaction_complete_verify.Request",
        payload={
            "transactionId": transaction_id
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Transaction-Complete.Verify",
        "status": "stub",
        "message": "Stub transaction verification.",
        "transactionId": transaction_id,
        "verified": not ctx.get("dry_run"),
        "subjectProfile": ctx.get("profile"),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
    }
