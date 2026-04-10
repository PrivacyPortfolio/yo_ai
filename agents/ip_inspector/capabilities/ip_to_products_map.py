# agents/ip_inspector/capabilities/ip_to_products_map.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    ip_asset = payload.get("ipAsset")

    return {
        "message": "Stub IP-to-products mapping.",
        "ipAsset": ip_asset,
        "products": [],
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
