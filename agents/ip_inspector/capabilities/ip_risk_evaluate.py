# agents/ip_inspector/capabilities/ip_risk_evaluate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    ip_asset = payload.get("ipAsset")

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
