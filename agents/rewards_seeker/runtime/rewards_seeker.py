# agents/rewards_seeker/runtime/rewards_seeker.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("rewards_seeker")

class RewardsSeekerAgent(YoAiAgent):
    """
    Rewards-Seeker: manages loyalty programs, rewards, cashback, promotional
    eligibility, and reward redemption. Integrates with SocialMedia-Checker
    for promotional verification and with Data-Steward for loyalty profile requests.
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
    async def rewards_discover(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:            
        from agents.rewards_seeker.capabilities.rewards_discover import run
        return await run(payload, agent_ctx, capability_ctx)

    async def promo_eligibility_verify(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.rewards_seeker.capabilities.promo_eligibility_verify import run
        return await run(payload, agent_ctx, capability_ctx)


    async def reward_redeem(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.rewards_seeker.capabilities.reward_redeem import run
        return await run(payload, agent_ctx, capability_ctx)


    async def rewards_profile_request(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.rewards_seeker.capabilities.rewards_profile_request import run
        return await run(payload, agent_ctx, capability_ctx)


    async def redemption_plan_generate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.rewards_seeker.capabilities.redemption_plan_generate import run
        return await run(payload, agent_ctx, capability_ctx)
