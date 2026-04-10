# 2. Full Python implementation (core detection + risk + event creation)
# This is a self-contained sketch with interfaces you can plug into your existing adapters.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal, Protocol, Tuple
from enum import Enum
import datetime as dt
import hashlib
import uuid


Channel = Literal["email", "phone", "network", "portal", "social", "api", "unknown"]
BlockType = Literal["hard", "soft", "rate_limit", "silent_drop", "captcha_loop", "other"]
BlockMechanism = Literal[
    "spam_filter",
    "fraud_detection",
    "bot_detection",
    "ip_reputation",
    "phone_reputation",
    "waf",
    "policy_block",
    "retaliation_suspected",
    "misconfiguration",
    "unknown"
]
RiskBand = Literal["highest", "quantifiable", "lowest"]


@dataclass
class BlockContext:
    organization: str
    channel: Channel
    direction: Literal["inbound", "outbound"]
    block_type: BlockType
    block_mechanism: BlockMechanism
    http_status_code: Optional[int] = None
    smtp_status_code: Optional[str] = None
    telephony_status_code: Optional[str] = None
    twilio_product: Optional[str] = None  # "Voice", "SendGrid", etc.
    thread_id: Optional[str] = None
    related_request_id: Optional[str] = None
    raw_context: Dict[str, Any] = None
    retaliation_indicator: bool = False
    prior_responsiveness_hours: Optional[float] = None


class VaultLike(Protocol):
    async def store_block_context(self, context: Dict[str, Any], content_hash: str) -> str:
        """
        Store the raw technical context and return a URI.
        """
        ...


class EventsRepo(Protocol):
    async def append_block_event(self, event: Dict[str, Any]) -> None:
        ...


def sha256_of_obj(obj: Any) -> str:
    m = hashlib.sha256()
    m.update(repr(obj).encode("utf-8"))
    return m.hexdigest()


def compute_behavioral_risk_for_block(
    block_type: BlockType,
    block_mechanism: BlockMechanism,
    prior_responsiveness_hours: Optional[float],
    retaliation_indicator: bool,
    quantifiable_risk_usd: Optional[float] = None,
) -> Tuple[float, RiskBand]:
    """
    Extension of your behavioral model, tailored to blocks.
    """
    score = 0.5

    # Automated security blocks: small negative (understandable)
    if block_mechanism in ("spam_filter", "fraud_detection", "bot_detection", "ip_reputation", "phone_reputation", "waf"):
        score -= 0.1

    # Silent drops are strongly negative
    if block_type == "silent_drop":
        score -= 0.3

    # Long-standing unresponsiveness
    if prior_responsiveness_hours is None:
        score -= 0.2
    elif prior_responsiveness_hours > 24 * 30:  # > 30 days
        score -= 0.1

    # Retaliation
    if retaliation_indicator:
        score -= 0.4

    # Quantifiable risk preference
    if quantifiable_risk_usd is not None:
        if score < 0.3:
            score = 0.35
        elif score > 0.7:
            score = 0.65

    score = max(0.0, min(1.0, score))

    if score <= 0.3:
        band: RiskBand = "highest"
    elif score < 0.7:
        band = "quantifiable"
    else:
        band = "lowest"

    return score, band


class BlockDetector:
    """
    Centralized helper the Data-Steward can use for turning
    raw block observations into BlockedCommunicationEvent records.
    """

    def __init__(
        self,
        subject_id: str,
        household_id: Optional[str],
        vault: VaultLike,
        events_repo: EventsRepo,
    ) -> None:
        self.subject_id = subject_id
        self.household_id = household_id
        self.vault = vault
        self.events_repo = events_repo

    async def record_block(self, ctx: BlockContext) -> Dict[str, Any]:
        """
        Main entrypoint: given a BlockContext, compute risk, store context,
        and persist a BlockedCommunicationEvent.
        """
        timestamp = dt.datetime.utcnow().isoformat() + "Z"
        raw_context = ctx.raw_context or {}
        content_hash = sha256_of_obj(raw_context)

        raw_location = await self.vault.store_block_context(raw_context, content_hash)

        # TODO: plug in your own quantifiable risk heuristic if desired
        quantifiable_risk_usd: Optional[float] = None

        risk_score, risk_band = compute_behavioral_risk_for_block(
            block_type=ctx.block_type,
            block_mechanism=ctx.block_mechanism,
            prior_responsiveness_hours=ctx.prior_responsiveness_hours,
            retaliation_indicator=ctx.retaliation_indicator,
            quantifiable_risk_usd=quantifiable_risk_usd,
        )

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "subject_id": self.subject_id,
            "household_id": self.household_id,
            "organization": ctx.organization,
            "organization_unit": raw_context.get("organization_unit"),
            "channel": ctx.channel,
            "direction": ctx.direction,
            "block_type": ctx.block_type,
            "block_mechanism": ctx.block_mechanism,
            "http_status_code": ctx.http_status_code,
            "smtp_status_code": ctx.smtp_status_code,
            "telephony_status_code": ctx.telephony_status_code,
            "twilio_product": ctx.twilio_product,
            "thread_id": ctx.thread_id,
            "related_request_id": ctx.related_request_id,
            "risk_score": risk_score,
            "behavioral_risk_band": risk_band,
            "retaliation_indicator": ctx.retaliation_indicator,
            "prior_responsiveness_hours": ctx.prior_responsiveness_hours,
            "content_hash": content_hash,
            "raw_context_location": raw_location,
            "summary": raw_context.get("summary"),
            "metadata": {
                k: v
                for k, v in raw_context.items()
                if k not in ("summary",)
            },
        }

        await self.events_repo.append_block_event(event)
        return event

# You would call BlockDetector.record_block() from channel specific detection code (email/phone/network/Twilio).
