# agents/tech_inspector/runtime/tech_inspector.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("tech_inspector")

class TechInspectorAgent(YoAiAgent):
    """
    Tech-Inspector: discovers third-party assets, maps integrations, analyzes
    implementation details, searches usage instances, infers technical impact,
    clusters portfolios, evaluates integration risk, traces provenance, detects
    related assets, and generates technical reports.

    This agent is profile-aware: analysis may depend on subject profile,
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
    async def third_party_assets_discover(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.third_party_assets_discover import run
        return await run(payload, agent_ctx, capability_ctx)


    async def asset_integrations_map(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.asset_integrations_map import run
        return await run(payload, agent_ctx, capability_ctx)


    async def implementation_details_analyze(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.implementation_details_analyze import run
        return await run(payload, agent_ctx, capability_ctx)


    async def usage_instances_search(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.usage_instances_search import run
        return await run(payload, agent_ctx, capability_ctx)


    async def technical_impact_infer(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.technical_impact_infer import run
        return await run(payload, agent_ctx, capability_ctx)


    async def asset_portfolio_cluster(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.asset_portfolio_cluster import run
        return await run(payload, agent_ctx, capability_ctx)


    async def integration_risk_evaluate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.integration_risk_evaluate import run
        return await run(payload, agent_ctx, capability_ctx)


    async def integration_provenance_trace(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.integration_provenance_trace import run
        return await run(payload, agent_ctx, capability_ctx)


    async def related_assets_detect(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.related_assets_detect import run
        return await run(payload, agent_ctx, capability_ctx)


    async def tech_report_generate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.tech_inspector.capabilities.tech_report_generate import run
        return await run(payload, agent_ctx, capability_ctx)
