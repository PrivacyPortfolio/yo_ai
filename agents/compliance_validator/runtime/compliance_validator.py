# agents/compliance_validator/runtime/compliance_validator.py
#
# Compliance-Validator: evaluates facts, evidence, and assessments against
# laws, regulations, mandates, policies, and contracts. Produces factual
# compliance rationales suitable for audit, challenge, or testimony.
#
# Profile-aware: compliance evaluation depends on subject profile, caller
# identity, and governance labels — all carried in YoAiContext.

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("compliance_validator")


class ComplianceValidatorAgent(YoAiAgent):

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        profile: dict | None = None,
        slim: bool = False,
    ):
        # ── No ctx param — YoAiAgent no longer accepts one ─────────────────
        # agent_id default was "complaint_manager" — copy-paste bug, now
        # removed entirely. agent_id comes from the card via BaseAgent.
        super().__init__(
            card=card,
            extended_card=extended_card,
            profile=profile,
            slim=slim,
        )

    # ── Capability: Compliance-Standard.Get ───────────────────────────────

    async def compliance_standard_get(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.compliance_validator.capabilities.compliance_standard_get import run
        return await run(payload, ctx)

    # ── Capability: Compliance.Validate ───────────────────────────────────

    async def compliance_validate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.compliance_validator.capabilities.compliance_validate import run
        return await run(payload, ctx)
