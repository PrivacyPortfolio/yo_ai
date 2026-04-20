# agents/profile_builder/runtime/profile_builder.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("profile_builder")

class ProfileBuilderAgent(YoAiAgent):
    """
    Profile-Builder: builds and maintains organization profiles based on
    discovery from IP-Inspector and Tech-Inspector agents.

    This agent is profile-aware: it may operate with an org profile reference
    or build a new one from scratch.
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
    # Capability: Org-Profile.Build
    # ------------------------------------------------------------------
    async def org_profile_build(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.profile_builder.capabilities.org_profile_build import run
        return await run(payload, ctx)

