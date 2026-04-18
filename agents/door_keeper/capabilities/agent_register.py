# agents/door_keeper/capabilities/agent_register.py
#
# Capability: Agent.Register
# Validates an agent card and issues a RegisteredAgent card for qualified agents.
#
# Registration criteria (Yo-ai Agent Registry):
#   - Must submit an A2A-compliant agent card
#   - Provider must have a named RegisteredSubscriber on record
#   - Agent does NOT need A2A interaction capability to register
#     (platform provides the wrapper on registration)
#
# Outcomes: registered | pending-registration | denied-agent

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Agent.Register ────────────────────────────────────────

    agent_card      = payload.get("agentCard", {})
    agent_name      = agent_card.get("name") or payload.get("agentName")
    provider        = agent_card.get("provider", {})
    subscriber_id   = payload.get("subscriberId")
    declared_skills = agent_card.get("skills", [])

    # Stub: real implementation validates A2A compliance and subscriber record.
    registration_status = "registered"
    agent_id            = "stub-agent-456"
    denial_reason       = None

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="agent_register.Request",
        payload={
            "agentId":            agent_id,
            "agentName":          agent_name,
            "provider":           provider,
            "subscriberId":       subscriber_id,
            "declaredSkills":     [s.get("name") for s in declared_skills],
            "registrationStatus": registration_status,
            "denialReason":       denial_reason,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "agentId":            agent_id,
        "agentName":          agent_name,
        "provider":           provider,
        "subscriberId":       subscriber_id,
        "declaredSkills":     [s.get("name") for s in declared_skills],
        "registrationStatus": registration_status,
        "denialReason":       denial_reason,
        "timestamp":          datetime.now(timezone.utc).isoformat(),
        "correlationId":      ctx.get("correlation_id"),
        "taskId":             ctx.get("task_id"),
        "dryRun":             ctx.get("dry_run"),
        "status":             "stub",
    }

    return result
