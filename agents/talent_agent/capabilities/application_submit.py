# agents/talent_agent/capabilities/application_submit.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Application.Submit

    Stub: submits job applications using minimized profile from Data-Steward.

    Real implementation would:
      - request minimized resume bundle
      - generate cover letter
      - submit application to job board or ATS
      - capture submission receipt
    """

    job = payload.get("job")

    return {
        "message": "Stub job application submission.",
        "job": job,
        "status": "submitted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
