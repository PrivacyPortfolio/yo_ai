# agents/door_keeper/capabilities/agent_authenticate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Agent.Authenticate
    Authenticates a registered agent and monitors activity.

    Two authentication paths (per Door-Keeper Training Manual):
      1. RegisteredAgentCard authToken found
         → trusted directly, bypasses Cognito
      2. No registered card found
         → falls back to Cognito validation (AWS Cognito, backend: AgentAuthenticator)

    Every decision is logged and published to the agent-auth Kafka topic.

    WARNING (stub): authenticated is hardcoded True.
    Real implementation must check Cognito before returning.

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    agent_id        = payload.get("agentId")
    auth_method     = payload.get("authMethod")    # "registered-card" | "cognito" | "api-key" | "mtls"
    token           = payload.get("token")         # Not logged — credential material
    cert_fingerprint = payload.get("certFingerprint")
    ip_address      = payload.get("ipAddress")

    # Stub: always authenticates.
    # Real: check for RegisteredAgentCard authToken first,
    # fall back to Cognito if not found.
    authenticated    = True
    auth_path        = "stub"          # "registered-card" | "cognito" | "denied"
    failure_reason   = None

    result = {
        "agentId":         agent_id,
        "authenticated":   authenticated,
        "authMethod":      auth_method,
        "authPath":        auth_path,
        "certFingerprint": cert_fingerprint,
        "failureReason":   failure_reason,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
        "status":          "stub",
    }

    return result
