# agents/door_keeper/capabilities/agent_authenticate.py
#
# Capability: Agent.Authenticate
# Authenticates a registered agent and monitors activity.
#
# Two authentication paths:
#   1. RegisteredAgentCard authToken found → trusted directly, bypasses Cognito
#   2. No registered card found → falls back to Cognito validation
#
# Every decision is logged and published to the agent-auth Kafka topic.
#
# WARNING (stub): authenticated is hardcoded True.
# Real implementation must check Cognito before returning.

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Agent.Authenticate ────────────────────────────────────

    agent_id         = payload.get("agentId")
    auth_method      = payload.get("authMethod")     # "registered-card" | "cognito" | "api-key" | "mtls"
    token            = payload.get("token")          # not logged — credential material
    cert_fingerprint = payload.get("certFingerprint")
    ip_address       = payload.get("ipAddress")

    # Stub: always authenticates.
    # Real: check RegisteredAgentCard authToken first, fall back to Cognito.
    authenticated  = True
    auth_path      = "stub"    # "registered-card" | "cognito" | "denied"
    failure_reason = None

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="agent_authenticate.Request",
        payload={
            "agentId":         agent_id,
            "authMethod":      auth_method,
            "certFingerprint": cert_fingerprint,
            "authenticated":   authenticated,
            "authPath":        auth_path,
            "failureReason":   failure_reason,
            "ipAddress":       ip_address,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "agentId":         agent_id,
        "authenticated":   authenticated,
        "authMethod":      auth_method,
        "authPath":        auth_path,
        "certFingerprint": cert_fingerprint,
        "failureReason":   failure_reason,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
        "status":          "stub",
    }

    return result
