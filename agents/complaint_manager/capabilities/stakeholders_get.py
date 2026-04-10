# agents/complaint_manager/capabilities/stakeholders_get.py

import time
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:

    """
    Capability: Stakeholders.Get

    Stub: retrieves stakeholders relevant to the complaint.
    """

    org = payload.get("organization")

    return {
        "message": "Stub stakeholder retrieval.",
        "organization": org,
        "stakeholders": ["StubStakeholderA", "StubStakeholderB"],
        "timestamp": time.time(),
        "correlationId": ctx.correlation_id,
    }
