# agents/door_keeper/capabilities/trust_assign.py

from .score_agreements import score_agreements

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Trust.Assign
    Assigns a trust tier to a visitor and emits VisitorTrustTierAssigned.

    This is Door-Keeper's most consequential capability. The assigned tier
    gates all downstream access: ExtendedCard visibility, Kafka topic ACLs,
    capability bundle (A/B/C), rate limits, and probation period.

    Trust tier values:
        tier-0  Public       — no registration, stateless
        tier-1  Probationary — verified identity, behavioral contract accepted
        tier-2  Trusted      — probation complete, no major violations
        tier-3  Strategic    — deeply trusted vendor/co-processor

    Trust factors evaluated (scored 0.0–1.0 each):
        agreements       — count and validity of signed agreements
                           "0 agreements = 0 promises"
                           Source: score_agreements() → training/artifacts/agreements/
        riskSignals      — caller-supplied risk observations (from Visitor.Identify)
                           e.g. blocked communications, retaliation indicators
        identityVerified — whether identity has been positively verified
        certFingerprint  — mTLS cert fingerprint stability (future: verify_fingerprints)
        behavioralScore  — probationary monitoring loop score (future: Trust-Assessor)

    Final tier assignment:
        Stub: caller supplies trustTier in payload — used as-is.
        Real: weighted composite of all trust factors → tier decision.

    Kafka event emitted: VisitorTrustTierAssigned
        Published to: agent-auth topic (placeholder — KafkaPublisher not yet built)

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    visitor_id       = payload.get("visitorId")
    visitor_agent    = payload.get("agentName")        # agent name of the visiting agent
    assigned_tier    = payload.get("trustTier", "tier-0")
    rationale        = payload.get("rationale", [])
    evidence_refs    = payload.get("evidenceRefs", [])
    probation_ends   = payload.get("probationEndsAt")

    # Caller-supplied trust signals from Visitor.Identify / probationary loop
    risk_signals      = payload.get("riskSignals", [])
    identity_verified = payload.get("identityVerified", False)
    cert_fingerprint  = payload.get("certFingerprint")
    behavioral_score  = payload.get("behavioralScore")  # 0.0–1.0, from Trust-Assessor

    # ------------------------------------------------------------------
    # Trust Factor: Agreements
    # Score the agreements held by:
    #   1. Door-Keeper itself — how trustworthy is the gatekeeper?
    #   2. The visiting agent — how many promises have they made?
    #
    # "0 agreements = 0 promises."
    # Agents with no agreements get no agreement trust contribution.
    # Expired agreements are deducted — a broken promise is worse than none.
    # ------------------------------------------------------------------

    # Door-Keeper's own agreements (how much can Door-Keeper be trusted?)
    door_keeper_agreement_score = score_agreements(
        agent_name="door-keeper",
    )

    # Visiting agent's agreements (how much can the visitor be trusted?)
    visitor_agreement_score = score_agreements(
        agent_name=visitor_agent,
        subject_id=visitor_id,
    ) if visitor_agent else {
        "agreementCount": 0,
        "score":          0.0,
        "scoreRationale": "No agent name supplied — agreement score unavailable.",
        "agreements":     [],
    }

    # Collect all trust factors for rationale and future weighted scoring
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
            "signals":        risk_signals,
            "count":          len(risk_signals),
            # Negative factor — more signals → lower trust
        },
        "identityVerified": {
            "verified":       identity_verified,
        },
        "certFingerprint": {
            "present":        cert_fingerprint is not None,
            "value":          cert_fingerprint,
        },
        "behavioralScore": {
            "score":          behavioral_score,
        },
    }

    result = {
        "visitorId":       visitor_id,
        "visitorAgent":    visitor_agent,
        "trustTier":       assigned_tier,
        "trustFactors":    trust_factors,
        "rationale":       rationale,
        "evidenceRefs":    evidence_refs,
        "probationEndsAt": probation_ends,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
        "status":          "stub",
    }

    return result
