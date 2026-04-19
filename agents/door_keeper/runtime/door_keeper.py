# agents/door_keeper/runtime/door_keeper.py

from core.platform_agent import PlatformAgent, PlatformEventBus
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("door_keeper")


class DoorKeeperAgent(PlatformAgent):
    # ── Door-Keeper ────────────────────────────────────────────────────────
    # Profiles guests, registers subscribers/agents, authenticates visitors,
    # assigns trust, and manages access rights.
    #
    # Event Bus:
    #   PlatformEventBus must be injected at construction (event_bus=).
    #   Listens for:  Platform.ConfigurationChanged (inherited, auto-registered)
    #   Emits:        VisitorTrustTierAssigned (via trust_assign run())

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

    # ── Capability: Visitor.Identify ───────────────────────────────────────

    async def visitor_identify(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.visitor_identify import run
        return await run(payload, ctx)

    # ── Capability: Subscriber.Register ───────────────────────────────────

    async def subscriber_register(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.subscriber_register import run
        return await run(payload, ctx)

    # ── Capability: Credentials.Generate ──────────────────────────────────

    async def credentials_generate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.credentials_generate import run
        return await run(payload, ctx)

    # ── Capability: Subscriber.Authenticate ───────────────────────────────

    async def subscriber_authenticate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.subscriber_authenticate import run
        return await run(payload, ctx)

    # ── Capability: Agent.Register ─────────────────────────────────────────

    async def agent_register(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.agent_register import run
        return await run(payload, ctx)

    # ── Capability: Trust.Assign ───────────────────────────────────────────

    async def trust_assign(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.trust_assign import run
        return await run(payload, ctx)

    # ── Capability: AccessRights.Manage ───────────────────────────────────

    async def accessrights_manage(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.accessrights_manage import run
        return await run(payload, ctx)

    # ── Capability: Agent.Authenticate ────────────────────────────────────

    async def agent_authenticate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.door_keeper.capabilities.agent_authenticate import run
        return await run(payload, ctx)

    # ── Mode 2: handle_a2a — A2A Direct dispatch ───────────────────────────

    async def handle_a2a(
        self,
        capability_id: str,
        payload: dict,
        ctx: YoAiContext,
    ) -> dict:
        dispatch = {
            "Visitor.Identify":        self.visitor_identify,
            "Subscriber.Register":     self.subscriber_register,
            "Credentials.Generate":    self.credentials_generate,
            "Subscriber.Authenticate": self.subscriber_authenticate,
            "Agent.Register":          self.agent_register,
            "Trust.Assign":            self.trust_assign,
            "AccessRights.Manage":     self.accessrights_manage,
            "Agent.Authenticate":      self.agent_authenticate,
        }
        handler = dispatch.get(capability_id)
        if handler is None:
            raise NotImplementedError(
                f"Capability '{capability_id}' not found on DoorKeeperAgent."
            )
        return await handler(payload, ctx)
