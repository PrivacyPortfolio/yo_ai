# agents/ip_inspector/related_ip_discover.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    ip_asset = payload.get("ipAsset")

    return {
        "message": "Stub related IP discovery.",
        "ipAsset": ip_asset,
        "related": [],
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
