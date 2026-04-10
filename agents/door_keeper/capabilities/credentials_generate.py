# agents/door_keeper/capabilities/credentials_generate.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Credentials.Generate
    Generates credentials for RegisteredAgents and RegisteredSubscribers.

    This capability is the long-term replacement for the API Keys stopgap
    (see API_KEYS.docx). Once operational, agents receive Door-Keeper-issued
    credentials instead of manually provisioned API keys.

    Credential types:
      - api-key      : Temporary bridge credential (current stopgap)
      - mtls-cert    : Client certificate signed by platform CA
                       (see ClientCertificates.docx — issue_client_cert() pattern)
      - capability-token : Scoped token for specific capability access

    Subject types:
      - RegisteredAgent
      - RegisteredSubscriber

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    subject_id      = payload.get("subjectId")
    subject_type    = payload.get("subjectType")     # "RegisteredAgent" | "RegisteredSubscriber"
    credential_type = payload.get("credentialType")  # "api-key" | "mtls-cert" | "capability-token"
    scope           = payload.get("scope", [])       # Capability scopes for capability-token

    # Stub: returns placeholder credential.
    # Real implementation:
    #   api-key      → generate + store in FastA2A Storage, attach to usage plan
    #   mtls-cert    → invoke issue_client_cert() against platform CA
    #   capability-token → issue scoped JWT signed by platform
    stub_credential = {
        "api-key":           {"apiKey": "stub-key-xyz"},
        "mtls-cert":         {"certPath": "stub-cert-path", "keyPath": "stub-key-path"},
        "capability-token":  {"token": "stub-token-abc", "scope": scope},
    }.get(credential_type, {"raw": "stub-credential"})

    result = {
        "subjectId":       subject_id,
        "subjectType":     subject_type,
        "credentialType":  credential_type,
        "credential":      stub_credential,
        "scope":           scope,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
        "status":          "stub",
    }

    return result
