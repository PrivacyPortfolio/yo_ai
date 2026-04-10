# agents/socialmedia_checker/runtime/socialmedia_checker.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("socialmedia_checker")

class SocialMediaCheckerAgent(YoAiAgent):
    """
    SocialMedia-Checker: evaluates social media activity to verify promotional
    requirements and detect potential misappropriation of personal data.

    This agent is profile-aware: verification and misappropriation detection
    may depend on subject profile, caller identity, or governance labels.
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
    async def promotional_engagement_verify(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:            
        from agents.socialmedia_checker.capabilities.promotional_engagement_verify import run
        return await run(payload, agent_ctx, capability_ctx)

    async def misappropriation_detect(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.socialmedia_checker.capabilities.misappropriation_detect import run
        return await run(payload, agent_ctx, capability_ctx)


    async def evidence_collect(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.socialmedia_checker.capabilities.evidence_collect import run
        return await run(payload, agent_ctx, capability_ctx)
