# agents/ip_inspector/capabilities/ip_assets_discover.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    org = payload.get("organization")

    return {
        "message": "Stub IP asset discovery.",
        "organization": org,
        "assets": [],
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
