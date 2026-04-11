# agents/purchasing_agent/capabilities/purchase_options_recommend.py

"""
Capability: Purchase-Options.Recommend
Stub — returns one hardcoded vendor. Next: vendor comparison, price analysis,
      AP2 compatibility checks, risk scoring, AI-native recommendation via call_ai().
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      ctx           — YoAiContext | None  (governance, startup_mode, caller)
    """
    item = payload.get("item")
    budget = payload.get("budget")
    preferences = payload.get("preferences", {})

    LOG.write(
        event_type="purchase_options_recommend.Request",
        payload={
            "item": item,
            "budget": budget,
            "preferences": preferences
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Purchase-Options.Recommend",
        "status": "stub",
        "message": "Stub Purchase-Options.Recommend response.",
        "item": item,
        "budget": budget,
        "preferences": preferences,
        "recommendations": [] if ctx.dry_run else [
            {"vendor": "ExampleVendor", "price": 42.00, "riskScore": 0.1, "ap2Compatible": True},
        ],
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
