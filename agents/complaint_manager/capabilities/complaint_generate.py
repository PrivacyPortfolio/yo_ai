# agents/complaint_manager/capabilities/complaint_generate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("complaint_manager")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    """
    Capability: Complaint.Generate

    Stub: generates a structured complaint document.
    """

    findings = payload.get("findings", {})

    LOG.write(
        event_type="complaint-generate.Request",
        payload={
            "findings": findings
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub complaint generation.",
        "findings": findings,
        "complaintDocument": {
            "id": "stub-complaint-123",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "correlationId": ctx.correlation_id,
        "taskId": ctx.task_id,
    }
