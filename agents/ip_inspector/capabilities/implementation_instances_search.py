# agents/ip_inspector/capabilities/implementation_instances_search.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("ip_inspector")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    ip_asset = payload.get("ipAsset")

    LOG.write(
        event_type="implementation_instances.Request",
        payload={
            "ipAsset": ip_asset,
            "instances": [],
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub implementation instance search.",
        "ipAsset": ip_asset,
        "instances": [],
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
    }
