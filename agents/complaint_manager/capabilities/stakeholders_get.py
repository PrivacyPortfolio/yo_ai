# agents/complaint_manager/capabilities/stakeholders_get.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("complaint_manager")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    """
    Capability: Stakeholders.Get

    Stub: retrieves stakeholders relevant to the complaint.
    """

    org = payload.get("organization")

    LOG.write(
        event_type="stakeholders-get.Request",
        payload={
            "organization": org
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub stakeholder retrieval.",
        "organization": org,
        "stakeholders": ["StubStakeholderA", "StubStakeholderB"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId": ctx.get("task_id"),
    }
