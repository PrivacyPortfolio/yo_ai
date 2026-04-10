# agents/darkweb_checker/runtime/darkweb_checker.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("darkweb_checker")


class DarkWebChecker(YoAiAgent):
    """
    DarkWeb-Checker: searches breach forums, marketplaces, and dark web sources
    for stolen PI — and collects evidence to support claims that an organization
    acquired or used stolen data.

    This agent is profile-aware: investigations may depend on subject profile,
    caller identity, or governance labels.
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
    # Capability: Dark-Web.Scan
    # ------------------------------------------------------------------
    async def dark_web_scan(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.darkweb_checker.capabilities.dark_web_scan import run
        return await run(payload, agent_ctx, capability_ctx)        

    # ------------------------------------------------------------------
    # Capability: Data-Origins.Trace
    # ------------------------------------------------------------------
    async def data_origins_trace(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.darkweb_checker.capabilities.data_origins_trace import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Dark-Web-Evidence.Collect
    # ------------------------------------------------------------------
    async def dark_web_evidence_collect(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.darkweb_checker.capabilities.dark_web_evidence_collect import run
        return await run(payload, agent_ctx, capability_ctx)        
