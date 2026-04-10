# agents/door_keeper/capabilities/accessrights_manage.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: AccessRights.Manage
    Manages access rights for RegisteredAgents and RegisteredSubscribers.

    Backed by the AccessAdministrator tool in production:
      - Provider: Apache Kafka 3.7.0
      - Config: bootstrapServers=kafka:9092, securityProtocol=SASL_SSL
      - Capabilities: grant, revoke, issue-credentials
      - Path: /access_admin.py
    (See Door-Keeper-ExtendedAgentCard.md — AccessAdministrator tool artifact)

    Actions:
      grant   — grants access to a resource or Kafka topic
      revoke  — revokes existing access
      inspect — returns current access rights for a subject

    Subject types: RegisteredAgent | RegisteredSubscriber | Visitor

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    subject_id    = payload.get("subjectId")
    subject_type  = payload.get("subjectType")    # "RegisteredAgent" | "RegisteredSubscriber" | "Visitor"
    action        = payload.get("action")         # "grant" | "revoke" | "inspect"
    resource      = payload.get("resource")       # e.g. Kafka topic, capability name, endpoint
    permissions   = payload.get("permissions", []) # e.g. ["read", "write", "post"]
    rationale     = payload.get("rationale")

    result = {
        "subjectId":     subject_id,
        "subjectType":   subject_type,
        "action":        action,
        "resource":      resource,
        "permissions":   permissions,
        "rationale":     rationale,
        "outcome":       "updated",   # "updated" | "denied" | "no-change"
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.correlation_id,
        "taskId":        ctx.task_id,
        "dryRun":        ctx.dry_run,
        "status":        "stub",
    }

    return result
