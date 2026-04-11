# agents/data_steward/capabilities/email_send.py

"""
Capability: Email.Send
Sends outbound email on behalf of the represented subject (self.profile).

Stage: Stub — returns deterministic response.
Next:  Replace with email provider integration (Gmail, SES, Outlook, etc.)
       Add sender verification against self.profile.
       Add outbound governance check (Data-Request.Govern) for sensitive content.

Note: 'subject' renamed to 'email_subject' in payload to avoid collision
      with the reserved 'subject' field in AgentContext / CapabilityContext.
"""

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
        "message": "Stub outbound email sent." if not ctx.dry_run else "Stub dry_run — email not sent.",
        "to": to,
        "email_subject": email_subject,
        "body": body,
        "senderProfile": ctx.profile,
        "sent": not ctx.dry_run,
        "correlationId": ctx.correlation_id,
        "taskId": ctx.task_id,
        "dryRun": ctx.dry_run,
    }
