# agents/door_keeper/capabilities/subscriber_register.py
#
# Capability: Subscriber.Register
# Registers a new subscriber and issues a RegisteredSubscriber card.
#
# Registration criteria (Yo-ai Agent Registry):
#   - Named individual — not a group email (e.g. legal@company.com rejected)
#   - Accountable representative of the provider organization
#   - Recommended: corporate officer or legal representative authorized
#     to sign binding agreements

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Subscriber.Register ──────────────────────────────────

    email        = payload.get("email")
    name         = payload.get("name")
    organization = payload.get("organization")
    role         = payload.get("role")           # "corporate-officer" | "legal-rep"
    provider_url = payload.get("providerUrl")

    # Stub validation: real implementation rejects group/anonymous emails
    # and verifies named individual against provider formation documents.
    is_group_email = email and any(
        email.lower().startswith(prefix)
        for prefix in ("legal@", "info@", "admin@", "contact@", "support@")
    )

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="subscriber_register.Request",
        payload={
            "email":        email,
            "name":         name,
            "organization": organization,
            "role":         role,
            "providerUrl":  provider_url,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "subscriberId":  "stub-subscriber-123",
        "email":         email,
        "name":          name,
        "organization":  organization,
        "role":          role,
        "providerUrl":   provider_url,
        "status":        "registered",
        "warning":       "group-email-detected" if is_group_email else None,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
        "stub":          True,
    }

    return result
