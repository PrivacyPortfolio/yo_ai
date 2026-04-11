# agents/purchasing_agent/capabilities/purchase_receipt_generate.py

"""
Capability: Purchase-Receipt.Generate
Stub — returns hardcoded receipt. Next: generate real receipt from transaction record.
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
    price = payload.get("price")

    LOG.write(
        event_type="purchase_receipt_generate.Request",
        payload={
            "item": item,
            "price": price
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Purchase-Receipt.Generate",
        "status": "stub",
        "message": "Stub Purchase-Receipt.Generate response.",
        "receipt": None if ctx.dry_run else {
            "item": item,
            "price": price,
            "vendor": "StubVendor",
            "timestamp": "2026-02-19T00:00:00Z",
        },
        "subjectProfile": ctx.profile,
        "correlationId": ctx.correlation_id,
        "taskId": ctx.task_id,
    }
