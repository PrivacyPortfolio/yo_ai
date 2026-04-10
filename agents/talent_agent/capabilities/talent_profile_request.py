# agents/talent_agent/capabilities/talent_profile_request.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Talent-Profile.Request

    Stub: requests minimized resume, skills, and professional profile
    from Data-Steward.

    Real implementation would:
      - call Data-Steward → Data-Request.Govern
      - request specific fields
      - return minimized professional profile
    """

    fields = payload.get("requested_fields", [])

    return {
        "message": "Stub talent profile request.",
        "requestedFields": fields,
        "profile": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
