# agents/purchasing_agent/capabilities/purchase_risk_evaluate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Purchase-Risk.Evaluate
    Stub — returns low fixed risk score. Next: real vendor risk, fraud detection,
      pricing anomaly analysis, AP2 compatibility scoring.
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    vendor = payload.get("vendor")
    item = payload.get("item")
    price = payload.get("price")

    LOG.write(
        event_type="purchase_risk_evaluate.Request",
        payload={
            "item": item,
            "price": price,
            "vendor": vendor
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Purchase-Risk.Evaluate",
        "status": "stub",
        "message": "Stub Purchase-Risk.Evaluate response.",
        "vendor": vendor,
        "item": item,
        "price": price,
        "riskScore": None if ctx.get("dry_run") else 0.25,
        "riskFactors": [] if ctx.get("dry_run") else ["stubbed-risk-factor"],
        "subjectProfile": ctx.get("profile"),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
    }
