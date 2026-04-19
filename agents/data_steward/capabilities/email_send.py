# agents/data_steward/capabilities/email_send.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("data_steward")

async def run(payload: dict, ctx: YoAiContext) -> dict:

    to = payload.get("to")
    email_subject = payload.get("email_subject") or payload.get("subject")
    body = payload.get("body")

    LOG.write(
        event_type="Email.Send.Request",
        payload={
            "to":               to,
            "email_subject":    email_subject,
            "body":             body,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "capability": "Email.Send",
        "status": "stub",
        "message": "Stub outbound email sent." if not ctx.get("dry_run") else "Stub dry_run — email not sent.",
        "to": to,
        "email_subject": email_subject,
        "body": body,
        "senderProfile": ctx.get("profile"),
        "sent": not ctx.get("dry_run"),
        "correlationId": ctx.get("correlation_id"),
        "taskId": ctx.get("task_id"),
        "dryRun": ctx.get("dry_run"),
    }
