# core/platform_agent.py

from __future__ import annotations
from typing import Dict, List, Callable, Any

from core.yoai_agent import YoAiAgent
from core.platform_event_bus import PlatformEventBus

# ---------------------------------------------------------------------------
# PlatformAgent
# ---------------------------------------------------------------------------

class PlatformAgent(YoAiAgent):
    """
    PlatformAgent: privileged, long-lived, platform-service agent.
    """

    PLATFORM_CONFIG_EVENT = "Platform.ConfigurationChanged"

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        ctx=None,
        slim: bool = False,
        event_bus: PlatformEventBus,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            profile=None,   # PlatformAgents never use profiles
            ctx=ctx,
            slim=slim,
        )

        if not isinstance(event_bus, PlatformEventBus):
            raise TypeError(
                f"PlatformAgent '{self.actor_name}' requires a PlatformEventBus "
                f"instance. Got: {type(event_bus).__name__}"
            )

        self.event_bus = event_bus

        # Auto-subscribe for configuration change events.
        self.event_bus.subscribe(
            self.PLATFORM_CONFIG_EVENT,
            self.on_platform_configuration_change,
        )

        # Optional: structured log of subscription
        self.logger.write(
            event_type="platform_agent_subscribed",
            payload={"event_type": self.PLATFORM_CONFIG_EVENT},
            context=ctx,
            include=["instance_id", "correlation_id", "task_id"],
        )

    # ------------------------------------------------------------------
    # showCard() — basic card only, always
    # ------------------------------------------------------------------
    def showCard(self, ctx=None) -> dict:
        """
        PlatformAgents never expose their extended card externally.
        """
        if not self.card:
            self._fire_no_card_event(ctx)
            return {}
        return self.card

    # ------------------------------------------------------------------
    # Mode 2: handle_a2a — local dispatch entry point
    # ------------------------------------------------------------------
    async def handle_a2a(
        self,
        capability_id: str,
        payload: dict,
        ctx,
    ) -> dict:
        """
        Entry point for Mode 2 (A2A Direct) local dispatch.

        Subclasses override this and dispatch to their own capabilities:

            async def handle_a2a(self, capability_id, payload, ctx):
                dispatch = {
                    "Some.Capability": self.some_capability,
                }
                handler = dispatch.get(capability_id)
                if handler is None:
                    raise NotImplementedError(
                        f"Capability '{capability_id}' not found on "
                        f"{self.__class__.__name__}."
                    )
                return await handler(payload, ctx)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement handle_a2a(). "
            f"Override this method to support Mode 2 (A2A Direct) dispatch."
        )

    # ------------------------------------------------------------------
    # CM-6: Receive configuration change notifications
    # ------------------------------------------------------------------
    async def on_platform_configuration_change(self, event: dict) -> None:
        """
        Called when any PlatformAgent broadcasts a ConfigurationChanged event.
        Base implementation logs only. Override to react.
        """
        self.logger.write(
            event_type="platform_config_change_received",
            payload=event,
            context=None,
            include=["instance_id"],
        )

    # ------------------------------------------------------------------
    # CM-6: Emit configuration change events
    # ------------------------------------------------------------------
    async def emit_configuration_changed(
        self,
        change_type: str,
        details: dict | None = None,
    ) -> None:
        event = {
            "type":    change_type,
            "details": details or {},
            "source":  self.actor_name,
        }

        self.logger.write(
            event_type="platform_config_change_emitted",
            payload=event,
            context=None,
            include=["instance_id"],
        )

        await self.event_bus.broadcast(self.PLATFORM_CONFIG_EVENT, event)

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        self.event_bus.unsubscribe(
            self.PLATFORM_CONFIG_EVENT,
            self.on_platform_configuration_change,
        )

        self.logger.write(
            event_type="platform_agent_unregistered",
            payload={"event_type": self.PLATFORM_CONFIG_EVENT},
            context=None,
            include=["instance_id"],
        )