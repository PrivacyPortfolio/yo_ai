# agents/ip_inspector/capabilities/ip_risk_evaluate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("ip_inspector")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    ip_asset = payload.get("ipAsset")

    LOG.write(
        event_type="ip_risk_evaluate.Request",
        payload={
            "ipAsset": ip_asset,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub IP risk evaluation.",
        "ipAsset": ip_asset,
        "riskScore": 0.0,
        "factors": [],
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
