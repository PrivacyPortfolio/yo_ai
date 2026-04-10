# agents/door_keeper/visitor_identify.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Visitor.Identify
    Identifies a platform visitor and returns a basic profile snapshot.

    Decision signals returned here feed downstream capabilities:
      - Trust.Assign  (uses identitySource, priorVisits, riskSignals)
      - Subscriber.Register / Agent.Register (uses identifiedAs, email)

    Args:
        payload       (dict): Pre-extracted capability input.
        agent_ctx     (AgentContext): Governance context — caller, subject_ref,
                          correlation_id, governance_labels, task_id.
        capability_ctx (CapabilityContext): Execution context — dry_run, trace,
                          startup_mode.
    """

    visitor_id      = payload.get("visitorId")
    identity_source = payload.get("identitySource")   # e.g. "api-key", "mtls", "anonymous"
    ip_address      = payload.get("ipAddress")
    user_agent      = payload.get("userAgent")
    prior_visits    = payload.get("priorVisits", 0)
    risk_signals    = payload.get("riskSignals", [])

    result = {
        "visitorId":      visitor_id,
        "identifiedAs":   payload.get("identifiedAs"),
        "identitySource": identity_source,
        "ipAddress":      ip_address,
        "userAgent":      user_agent,
        "priorVisits":    prior_visits,
        "riskSignals":    risk_signals,
        "trustTier":      "unknown",   # Set by Trust.Assign — not determined here
        "identified":     visitor_id is not None,
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
        "status":         "stub",
    }

    return result
