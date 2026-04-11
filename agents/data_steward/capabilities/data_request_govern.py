# agents/data_steward/capabilities/data_request_govern.py

"""
Capability: Data-Request.Govern
Evaluates intended use of personal data before granting vault access.
The governance gate for all data access requests.

Stage: Stub — always approves. Policy evaluation deferred to Decision-Master.
Next:  Route to Decision-Master for policy evaluation when available.
       Integrate with VaultAdapter for actual data governance enforcement.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_steward")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    intended_use = payload.get("intendedUse")
    requested_fields = payload.get("requestedFields", [])

    LOG.write(
        event_type="Data-Request.Govern.Request",
        payload={
            "intendedUse": intended_use,
            "requestedFields": requested_fields,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Data-Request.Govern",
        "status": "stub",
        "message": "Stub data request governance decision.",
        "intendedUse": intended_use,
        "requestedFields": requested_fields,
        "approved": not ctx.dry_run,    # dry_run always returns unapproved
        "reason": "dry_run: approval withheld" if ctx.dry_run else "Stub policy approval.",
        "subjectProfile": ctx.subject_profile,
        "caller": ctx.caller,
        "taskId": ctx.task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id
    }
