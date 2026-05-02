# agents/the_sentinel/runtime/the_sentinel.py
#
# The-Sentinel: listens for dangerous incidents, anomalies, and trends,
# and issues alerts or escalations.

from core.platform_agent import PlatformAgent
from core.platform_event_bus import PlatformEventBus
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("the_sentinel")


class TheSentinelAgent(PlatformAgent):

    def __init__(
        self,
        *,
        card=None,
        extended_card=None,
        slim=False,
        event_bus: PlatformEventBus,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
            event_bus=event_bus,
        )

    # -- Capability: Platform.Monitor -------------------------------------

    async def platform_monitor(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.the_sentinel.capabilities.platform_monitor import run
        return await run(payload, ctx)
