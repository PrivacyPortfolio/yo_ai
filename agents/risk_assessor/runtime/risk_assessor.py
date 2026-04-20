# agents/risk_assessor/runtime/risk_assessor.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
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
        profile=None,
        slim: bool | None = None,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            profile=profile,
            slim=slim,
        )

    # ------------------------------------------------------------------
    # Capability: Risks.Assess
    # ------------------------------------------------------------------
    async def risks_assess(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.risk_assessor.capabilities.risks_assess import run
        return await run(payload, ctx)
        
