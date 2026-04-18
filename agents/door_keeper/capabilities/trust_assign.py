# agents/door_keeper/capabilities/trust_assign.py
#
# Capability: Trust.Assign
# Assigns a trust tier to a visitor and emits VisitorTrustTierAssigned.
#
# Trust tier values:
#   tier-0  Public       — no registration, stateless
#   tier-1  Probationary — verified identity, behavioral contract accepted
#   tier-2  Trusted      — probation complete, no major violations
#   tier-3  Strategic    — deeply trusted vendor/co-processor
#
# Trust factors evaluated (scored 0.0–1.0 each):
#   agreements       — count and validity of signed agreements ("0 agreements = 0 promises")
#   riskSignals      — caller-supplied risk observations from Visitor.Identify
#   identityVerified — whether identity has been positively verified
#   certFingerprint  — mTLS cert fingerprint stability (future: verify_fingerprints)
#   behavioralScore  — probationary monitoring loop score (future: Trust-Assessor)
#
# Stub: caller supplies trustTier in payload — used as-is.
# Real: weighted composite of all trust factors → tier decision.
#
# Kafka event emitted: VisitorTrustTierAssigned
#   Published to: agent-auth topic (placeholder — KafkaPublisher not yet built)

from .score_agreements import score_agreements

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Trust.Assign ──────────────────────────────────────────

    visitor_id     = payload.get("visitorId")
    visitor_agent  = payload.get("agentName")
    assigned_tier  = payload.get("trustTier", "tier-0")
    rationale      = payload.get("rationale", [])
    evidence_refs  = payload.get("evidenceRefs", [])
    probation_ends = payload.get("probationEndsAt")

    risk_signals      = payload.get("riskSignals", [])
    identity_verified = payload.get("identityVerified", False)
    cert_fingerprint  = payload.get("certFingerprint")
    behavioral_score  = payload.get("behavioralScore")   # 0.0–1.0, from Trust-Assessor

    # ── Trust factor: agreements ───────────────────────────────────────────
    # Door-Keeper's own agreements — how trustworthy is the gatekeeper?
    door_keeper_agreement_score = score_agreements(agent_name="door-keeper")

    # Visiting agent's agreements — how many promises have they made?
    visitor_agreement_score = score_agreements(
        agent_name=visitor_agent,
        subject_id=visitor_id,
    ) if visitor_agent else {
        "agreementCount":  0,
        "score":           0.0,
        "scoreRationale":  "No agent name supplied — agreement score unavailable.",
        "agreements":      [],
    }

    trust_factors = {
        "doorKeeperAgreements": {
            "score":          door_keeper_agreement_score["score"],
            "agreementCount": door_keeper_agreement_score["agreementCount"],
            "expiredCount":   door_keeper_agreement_score["expiredCount"],
            "rationale":      door_keeper_agreement_score["scoreRationale"],
        },
        "visitorAgreements": {
            "score":          visitor_agreement_score["score"],
            "agreementCount": visitor_agreement_score["agreementCount"],
            "rationale":      visitor_agreement_score["scoreRationale"],
        },
        "riskSignals": {
            "signals": risk_signals,
            "count":   len(risk_signals),
        },
        "identityVerified": {
            "verified": identity_verified,
        },
        "certFingerprint": {
            "present": cert_fingerprint is not None,
            "value":   cert_fingerprint,
        },
        "behavioralScore": {
            "score": behavioral_score,
        },
    }

    # ── Entry 1: capability received ──────────────────────────────────────
    LOG.write(
        event_type="trust_assign.Request",
        payload={
            "visitorId":       visitor_id,
            "visitorAgent":    visitor_agent,
            "trustTier":       assigned_tier,
            "trustFactors":    trust_factors,
            "rationale":       rationale,
            "evidenceRefs":    evidence_refs,
            "probationEndsAt": probation_ends,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "visitorId":       visitor_id,
        "visitorAgent":    visitor_agent,
        "trustTier":       assigned_tier,
        "trustFactors":    trust_factors,
        "rationale":       rationale,
        "evidenceRefs":    evidence_refs,
        "probationEndsAt": probation_ends,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
        "dryRun":          ctx.get("dry_run"),
        "status":          "stub",
    }

    return result
