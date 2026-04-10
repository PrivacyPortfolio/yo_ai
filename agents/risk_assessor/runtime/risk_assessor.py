# agents/risk_assessor/runtime/risk_assessor.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("risk_assessor")

class RiskAssessorAgent(YoAiAgent):
    """
    Risk-Assessor: conducts structured, provenance-aware risk assessments using
    specified standards, evidence sources, and assessment models.

    This agent is profile-aware: assessments may depend on subject profile,
    caller identity, org-profile, or governance labels.
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
    # Capability: Risks.Assess
    # ------------------------------------------------------------------
    async def risks_assess(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:            
        from agents.risk_assessor.capabilities.risks_assess import run
        return await run(payload, agent_ctx, capability_ctx)
        
