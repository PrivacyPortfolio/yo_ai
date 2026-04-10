# agents/purchasing_agent/capabilities/purchase_risk_evaluate.py

"""
Capability: Purchase-Risk.Evaluate
Stub — returns low fixed risk score. Next: real vendor risk, fraud detection,
      pricing anomaly analysis, AP2 compatibility scoring.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    vendor = payload.get("vendor")
    item = payload.get("item")
    price = payload.get("price")

    return {
        "capability": "Purchase-Risk.Evaluate",
        "status": "stub",
        "message": "Stub Purchase-Risk.Evaluate response.",
        "vendor": vendor,
        "item": item,
        "price": price,
        "riskScore": None if ctx.dry_run else 0.25,
        "riskFactors": [] if ctx.dry_run else ["stubbed-risk-factor"],
        "subjectProfile": ctx.profile,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
    }
