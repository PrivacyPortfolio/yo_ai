# agents/ip_inspector/runtime/ip_inspector.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("ip_inspector")

class IPInspector(YoAiAgent):
    """
    IP-Inspector: discovers intellectual property, maps IP to products,
    searches for implementation instances, infers use cases, clusters portfolios,
    generates reports, evaluates risk, traces provenance, and discovers related IP.

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
    async def ip_assets_discover(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:            
        from agents.ip_inspector.capabilities.ip_assets_discover import run
        return await run(payload, agent_ctx, capability_ctx)


    async def ip_to_products_map(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.ip_to_products_map import run
        return await run(payload, agent_ctx, capability_ctx)


    async def implementation_instances_search(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.implementation_instances_search import run
        return await run(payload, agent_ctx, capability_ctx)


    async def use_cases_infer(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.use_cases_infer import run
        return await run(payload, agent_ctx, capability_ctx)


    async def ip_portfolio_cluster(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.ip_portfolio_cluster import run
        return await run(payload, agent_ctx, capability_ctx)


    async def ip_report_generate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.ip_report_generate import run
        return await run(payload, agent_ctx, capability_ctx)


    async def ip_risk_evaluate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.ip_risk_evaluate import run
        return await run(payload, agent_ctx, capability_ctx)


    async def ip_provenance_trace(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.ip_provenance_trace import run
        return await run(payload, agent_ctx, capability_ctx)


    async def related_ip_discover(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.ip_inspector.capabilities.related_ip_discover import run
        return await run(payload, agent_ctx, capability_ctx)
