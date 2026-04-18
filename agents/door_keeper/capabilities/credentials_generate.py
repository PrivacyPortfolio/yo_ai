# agents/door_keeper/capabilities/credentials_generate.py
#
# Capability: Credentials.Generate
# Generates credentials for RegisteredAgents and RegisteredSubscribers.
#
# Long-term replacement for the API Keys stopgap (see API_KEYS.docx).
#
# Credential types:
#   api-key           — temporary bridge credential (current stopgap)
#   mtls-cert         — client certificate signed by platform CA
#   capability-token  — scoped token for specific capability access
#
# Subject types: RegisteredAgent | RegisteredSubscriber

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Credentials.Generate ─────────────────────────────────

    subject_id      = payload.get("subjectId")
    subject_type    = payload.get("subjectType")     # "RegisteredAgent" | "RegisteredSubscriber"
    credential_type = payload.get("credentialType")  # "api-key" | "mtls-cert" | "capability-token"
    scope           = payload.get("scope", [])

    # Stub: returns placeholder credential.
    # Real:
    #   api-key          → generate + store, attach to usage plan
    #   mtls-cert        → invoke issue_client_cert() against platform CA
    #   capability-token → issue scoped JWT signed by platform
    stub_credential = {
        "api-key":          {"apiKey": "stub-key-xyz"},
        "mtls-cert":        {"certPath": "stub-cert-path", "keyPath": "stub-key-path"},
        "capability-token": {"token": "stub-token-abc", "scope": scope},
    }.get(credential_type, {"raw": "stub-credential"})

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="credentials_generate.Request",
        payload={
            "subjectId":      subject_id,
            "subjectType":    subject_type,
            "credentialType": credential_type,
            "scope":          scope,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "subjectId":      subject_id,
        "subjectType":    subject_type,
        "credentialType": credential_type,
        "credential":     stub_credential,
        "scope":          scope,
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "correlationId":  ctx.get("correlation_id"),
        "taskId":         ctx.get("task_id"),
        "dryRun":         ctx.get("dry_run"),
        "status":         "stub",
    }

    return result
