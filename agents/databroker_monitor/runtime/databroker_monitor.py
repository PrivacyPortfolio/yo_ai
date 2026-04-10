# agents/databroker_monitor/runtime/databroker_monitor.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("databroker_monitor")


class DataBrokerMonitor(YoAiAgent):
    """
    DataBroker-Monitor: monitors registered data brokers to detect possession,
    sale, or distribution of personal information and identify downstream purchasers.

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
    # Capability: Broker-Inventory.Scan
    # ------------------------------------------------------------------
    async def broker_inventory_scan(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.databroker_monitor.capabilities.broker_inventory_scan import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Downstream-Vendors.Identify
    # ------------------------------------------------------------------
    async def downstream_vendors_identify(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.databroker_monitor.capabilities.downstream_vendors_identify import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Broker-Evidence.Collect
    # ------------------------------------------------------------------
    async def broker_evidence_collect(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.databroker_monitor.capabilities.broker_evidence_collect import run
        return await run(payload, agent_ctx, capability_ctx)
