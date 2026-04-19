# agents/data_steward/capabilities/email_read.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_steward")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    email = payload.get("email")
    folder = payload.get("folder", "inbox")

    LOG.write(
        event_type="Email.Read.Request",
        payload={
            "email":               email,
            "folder":              folder,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Email.Read",
        "status": "stub",
        "message": "Stub email read.",
        "email": email,
        "folder": folder,
        "spam": False,
        "phishing": False,
        "workflowTrigger": None if ctx.get("dry_run") else "stubbed-trigger",
        "correlationId": ctx.get("correlation_id"),
        "taskId": ctx.get("task_id"),
    }
