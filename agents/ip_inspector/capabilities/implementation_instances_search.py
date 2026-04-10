# agents/ip_inspector/capabilities/implementation_instances_search.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    ip_asset = payload.get("ipAsset")

    return {
        "message": "Stub implementation instance search.",
        "ipAsset": ip_asset,
        "instances": [],
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
