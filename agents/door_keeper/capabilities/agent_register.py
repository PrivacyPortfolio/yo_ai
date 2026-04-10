# agents/door_keeper/capabilities/agent_register.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Agent.Register
    Validates an agent card and issues a RegisteredAgent card for
    qualified agents.

    Registration criteria (Yo-ai Agent Registry):
      - Must submit an A2A-compliant agent card
      - Provider must have a named RegisteredSubscriber on record
      - Agent does NOT need A2A interaction capability to register
        (platform provides the wrapper on registration)

    Outcomes emitted: registered | pending-registration | denied-agent

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    agent_card       = payload.get("agentCard", {})
    agent_name       = agent_card.get("name") or payload.get("agentName")
    provider         = agent_card.get("provider", {})
    subscriber_id    = payload.get("subscriberId")   # Registering human representative
    declared_skills  = agent_card.get("skills", [])

    # Stub: real implementation validates A2A compliance and subscriber record
    registration_status = "registered"
    agent_id = "stub-agent-456"
    denial_reason = None

    result = {
        "agentId":            agent_id,
        "agentName":          agent_name,
        "provider":           provider,
        "subscriberId":       subscriber_id,
        "declaredSkills":     [s.get("name") for s in declared_skills],
        "registrationStatus": registration_status,   # registered | pending-registration | denied-agent
        "denialReason":       denial_reason,
        "timestamp":          datetime.now(timezone.utc).isoformat(),
        "correlationId":      ctx.correlation_id,
        "taskId":             ctx.task_id,
        "dryRun":             ctx.dry_run,
        "status":             "stub",
    }

    return result
