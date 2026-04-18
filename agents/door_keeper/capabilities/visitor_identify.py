# agents/door_keeper/visitor_identify.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Visitor.Identify ───────────────────────────────────────
    # Identifies a platform visitor and returns a basic profile snapshot.
    # Decision signals feed downstream capabilities:
    #   Trust.Assign            — uses identitySource, priorVisits, riskSignals
    #   Subscriber/Agent.Register — uses identifiedAs, email

    visitor_id      = payload.get("visitorId")
    identity_source = payload.get("identitySource")   # "api-key" | "mtls" | "anonymous"
    ip_address      = payload.get("ipAddress")
    user_agent      = payload.get("userAgent")
    prior_visits    = payload.get("priorVisits", 0)
    risk_signals    = payload.get("riskSignals", [])

    # ── Entry 1: capability received ───────────────────────────────────────
    LOG.write(
        event_type="visitor_identify.Request",
        payload={
            "visitorId":      visitor_id,
            "identifiedAs":   payload.get("identifiedAs"),
            "identitySource": identity_source,
            "ipAddress":      ip_address,
            "userAgent":      user_agent,
            "priorVisits":    prior_visits,
            "riskSignals":    risk_signals,
            "trustTier":      "unknown",   # set by Trust.Assign — not determined here
            "identified":     visitor_id is not None,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "visitorId":      visitor_id,
        "identifiedAs":   payload.get("identifiedAs"),
        "identitySource": identity_source,
        "ipAddress":      ip_address,
        "userAgent":      user_agent,
        "priorVisits":    prior_visits,
        "riskSignals":    risk_signals,
        "trustTier":      "unknown",   # set by Trust.Assign — not determined here
        "identified":     visitor_id is not None,
        "correlationId":  ctx.get("correlation_id"),
        "taskId":         ctx.get("task_id"),
        "dryRun":         ctx.get("dry_run"),
        "status":         "stub",
    }

    return result
