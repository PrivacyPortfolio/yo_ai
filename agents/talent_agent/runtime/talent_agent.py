# agents/talent_agent/runtime/talent_agent.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("talent_agent")

class TalentAgent(YoAiAgent):
    """
    Talent-Agent: responds to job postings, pitches consulting services,
    submits applications, and requests minimized professional profiles.

    This agent is profile-aware: job matching, pitch generation, and
    application submission may depend on subject profile, caller identity,
    or governance labels.
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
    async def job_postings_scan(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.talent_agent.capabilities.job_postings_scan import run
        return await run(payload, ctx)


    async def consulting_services_pitch(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.talent_agent.capabilities.consulting_services_pitch import run
        return await run(payload, ctx)


    async def application_submit(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.talent_agent.capabilities.application_submit import run
        return await run(payload, ctx)


    async def talent_profile_request(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.talent_agent.capabilities.talent_profile_request import run
        return await run(payload, ctx)

