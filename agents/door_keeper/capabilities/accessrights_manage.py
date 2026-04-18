# agents/door_keeper/capabilities/accessrights_manage.py
#
# Capability: AccessRights.Manage
# Manages access rights for RegisteredAgents and RegisteredSubscribers.
#
# Backed by the AccessAdministrator tool in production:
#   Provider: Apache Kafka 3.7.0
#   Config:   bootstrapServers=kafka:9092, securityProtocol=SASL_SSL
#   Actions:  grant | revoke | inspect
#   Path:     /access_admin.py
#
# Subject types: RegisteredAgent | RegisteredSubscriber | Visitor

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: AccessRights.Manage ───────────────────────────────────

    subject_id  = payload.get("subjectId")
    subject_type = payload.get("subjectType")    # "RegisteredAgent" | "RegisteredSubscriber" | "Visitor"
    action      = payload.get("action")          # "grant" | "revoke" | "inspect"
    resource    = payload.get("resource")
    permissions = payload.get("permissions", [])
    rationale   = payload.get("rationale")

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="accessrights_manage.Request",
        payload={
            "subjectId":   subject_id,
            "subjectType": subject_type,
            "action":      action,
            "resource":    resource,
            "permissions": permissions,
            "rationale":   rationale,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "subjectId":     subject_id,
        "subjectType":   subject_type,
        "action":        action,
        "resource":      resource,
        "permissions":   permissions,
        "rationale":     rationale,
        "outcome":       "updated",   # "updated" | "denied" | "no-change"
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "correlationId": ctx.get("correlation_id"),
        "taskId":        ctx.get("task_id"),
        "dryRun":        ctx.get("dry_run"),
        "status":        "stub",
    }

    return result
