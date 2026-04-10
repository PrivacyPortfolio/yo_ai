# agents/compliance_validator/runtime/compliance_validator.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("compliance_validator")


class ComplianceValidatorAgent(YoAiAgent):
    """
    Compliance-Validator: evaluates facts, evidence, and assessments against
    laws, regulations, mandates, policies, and contracts. Produces factual
    compliance rationales suitable for audit, challenge, or testimony.

    This agent is profile-aware: compliance evaluation often depends on
    subject profile, caller identity, and governance labels.
    """

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        capability_ctx: CapabilityContext | None = None,
        profile=None,
        slim: bool | None = None,
        context=None,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            capability_ctx=capability_ctx,
            profile=profile,
            slim=slim,
            context=context,
        )

    # ------------------------------------------------------------------
    # Capability: Compliance-Standard.Get
    # ------------------------------------------------------------------
    async def compliance_standard_get(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.compliance_validator.capabilities.compliance_standard_get import run
        return await run(payload, agent_ctx, capability_ctx)        

    # ------------------------------------------------------------------
    # Capability: Compliance.Validate
    # ------------------------------------------------------------------
    async def compliance_validate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.compliance_validator.capabilities.compliance_validate import run
        return await run(payload, agent_ctx, capability_ctx)        
