# agents/socialmedia_checker/runtime/socialmedia_checker.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
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
    async def promotional_engagement_verify(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.socialmedia_checker.capabilities.promotional_engagement_verify import run
        return await run(payload, ctx)

    async def misappropriation_detect(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.socialmedia_checker.capabilities.misappropriation_detect import run
        return await run(payload, ctx)


    async def evidence_collect(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.socialmedia_checker.capabilities.evidence_collect import run
        return await run(payload, ctx)
