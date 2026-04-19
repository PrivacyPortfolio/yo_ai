# agents/incident_responder/runtime/incident_responder.py
#
# Incident-Responder: universal exception handler for the platform.
# Handles uncaught exceptions, normalizes error envelopes, and produces
# structured incident responses.
#
# Note: this agent's handler has a special responsibility — it must never
# itself raise an unhandled exception. Its own error path is maximally
# defensive (see incident_responder_handler.py).

from core.platform_agent import PlatformAgent, PlatformEventBus
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("incident_responder")


class IncidentResponderAgent(PlatformAgent):

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

    # ── Capability: Handle.Exception ───────────────────────────────────────

    async def handle_exception(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.incident_responder.capabilities.handle_exception import run
        return await run(payload, ctx)
