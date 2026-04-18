# agents/door_keeper/capabilities/subscriber_authenticate.py
#
# Capability: Subscriber.Authenticate
# Authenticates a registered subscriber and monitors activity.
#
# Backed by AWS Cognito (Authenticated User Pool) in production.
# Decision outcome is logged for Door-Keeper's real-time Kafka monitoring.
#
# WARNING (stub): authenticated is hardcoded True.
# Real implementation must validate Cognito token/API key before returning.

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Subscriber.Authenticate ──────────────────────────────

    subscriber_id  = payload.get("subscriberId")
    auth_method    = payload.get("authMethod")   # "cognito-token" | "api-key" | "mtls"
    token          = payload.get("token")        # not logged — credential material
    ip_address     = payload.get("ipAddress")

    # Stub: always authenticates. Real implementation calls Cognito.
    authenticated  = True
    failure_reason = None

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="subscriber_authenticate.Request",
        payload={
            "subscriberId": subscriber_id,
            "authMethod":   auth_method,
            "ipAddress":    ip_address,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "subscriberId":  subscriber_id,
        "authenticated": authenticated,
        "authMethod":    auth_method,
        "failureReason": failure_reason,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
        "status":        "stub",
    }

    return result
