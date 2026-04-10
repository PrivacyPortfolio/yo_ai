# agents/data_steward/capabilities/email_read.py

"""
Capability: Email.Read
Reads inbound email, detects spam/phishing, extracts workflow triggers.
Reads on behalf of the represented subject (self.profile).

Stage: Stub — returns deterministic response.
Next:  Replace with email provider integration (Gmail, Outlook, etc.)
       Add real spam/phishing detection.
       Extract workflow triggers for downstream capabilities.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:

    email = payload.get("email")
    folder = payload.get("folder", "inbox")

    return {
        "capability": "Email.Read",
        "status": "stub",
        "message": "Stub email read.",
        "email": email,
        "folder": folder,
        "spam": False,
        "phishing": False,
        "workflowTrigger": None if dry_run else "stubbed-trigger",
        "correlationId": ctx.correlation_id,
        "taskId": ctx.task_id,
    }
