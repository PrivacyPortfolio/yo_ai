# core/platform_agent.py

from __future__ import annotations
from core.yoai_agent import YoAiAgent
from typing import Dict, List, Callable, Any


# ---------------------------------------------------------------------------
# PlatformEventBus
# ---------------------------------------------------------------------------

class PlatformEventBus:
    """
    In-process async pub/sub event bus for PlatformAgents.

    Lifecycle:
      - Instantiated once per Lambda execution environment (in handler).
      - Injected into every PlatformAgent at construction via event_bus=.
      - Each PlatformAgent auto-registers its handler on init.
      - Call shutdown() on teardown to release handler references.

    Usage:
      - Agents subscribe via subscribe(event_type, handler).
      - Agents broadcast via broadcast(event_type, event).
      - Only live, constructed instances are in the registry.

    Thread safety:
      - Designed for single-process asyncio use.
      - Not safe for concurrent modification from multiple threads.

    Scope:
      The PlatformEventBus handles intra-process, intra-invocation
      coordination between PlatformAgents (CM-6 config changes,
      lifecycle events, trust signals, budget alerts).

      Cross-invocation and cross-service events are published to Kafka
      via the Kafka Observability Publisher (Gap Registry 🔲 — not yet built).

      These are two distinct layers — the event bus is NOT a log sink
      and is NOT a replacement for Kafka.

    Canonical location:
      This class lives in core/platform_agent.py alongside PlatformAgent.
      Do NOT import from core/runtime/platform_event_bus.py — that file
      is superseded by this definition.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Register a handler for a given event type.
        Called automatically by PlatformAgent.__init__().
        """
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Remove a handler for a given event type.
        Call during agent teardown to avoid stale references.
        """
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def broadcast(self, event_type: str, event: dict) -> None:
        """
        Fan out event to all handlers subscribed to event_type.
        Handlers are awaited sequentially.
        Exceptions are NOT suppressed — callers should wrap broadcast()
        in a try/except if listener isolation is needed.
        """
        for handler in list(self._subscribers.get(event_type, [])):
            await handler(event)

    @property
    def subscriber_count(self) -> Dict[str, int]:
        """
        Diagnostic: returns a count of registered handlers per event type.
        """
        return {k: len(v) for k, v in self._subscribers.items()}


# ---------------------------------------------------------------------------
# PlatformAgent
# ---------------------------------------------------------------------------

class PlatformAgent(YoAiAgent):
    """
    PlatformAgent: privileged, long-lived, platform-service agent.

    Responsibilities:
      - Inherit all loading behavior from YoAiAgent (skills, tools, schemas,
        fingerprints, knowledge)
      - Enforce platform-level constraints (call graph, trust tiers, etc.)
      - Expose platform services to YoAiAgents and visiting agents
      - Maintain singleton-like lifecycle (managed by the platform)
      - Receive and react to platform configuration changes (CM-6)
      - Emit configuration change events when modifying platform behavior

    PlatformAgents do NOT use profiles — they act on behalf of the Platform
    as brokers and services, never representing a person or organization.

    Card Contract:
      PlatformAgents expose the basic card only — the extended card is
      NEVER exposed externally, even to registered callers.

    Event Bus:
      - A PlatformEventBus MUST be injected at construction (event_bus=).
      - No default — missing event_bus raises TypeError immediately.
      - This agent auto-registers on_platform_configuration_change for the
        "Platform.ConfigurationChanged" event on init.
      - Call shutdown() on teardown to unsubscribe and release references.

    slim= flag:
      When slim=True (used by Lambda execution environment singletons),
      fingerprints/knowledge/tools are skipped at init. The event bus
      is always wired regardless of slim — platform agents must always
      be able to receive configuration change events.
    """

    PLATFORM_CONFIG_EVENT = "Platform.ConfigurationChanged"

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        context=None,
        slim: bool = False,
        event_bus: PlatformEventBus,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            profile=None,       # PlatformAgents never use profiles
            context=context,
            slim=slim,
        )

        if not isinstance(event_bus, PlatformEventBus):
            raise TypeError(
                f"PlatformAgent '{self.actor_name}' requires a PlatformEventBus "
                f"instance. Got: {type(event_bus).__name__}"
            )

        self.event_bus = event_bus

        # Auto-register for configuration change events.
        # Runs even when slim=True — config changes must always be receivable.
        self.event_bus.subscribe(
            self.PLATFORM_CONFIG_EVENT,
            self.on_platform_configuration_change,
        )

        self.log(
            event_type="platform_agent_registered",
            message=f"{self.actor_name} registered on PlatformEventBus.",
            payload={"event_type": self.PLATFORM_CONFIG_EVENT},
        )

    # ------------------------------------------------------------------
    # showCard() — basic card only, always
    # ------------------------------------------------------------------
    def showCard(self, context=None) -> dict:
        """
        Return the basic card only.

        PlatformAgents never expose their extended card externally.
        If no card is available, fires a NO_CARD alert and returns {}.

        Args:
            context: AgentContext, if available. Not used for access
                     decisions — included for API consistency with BaseAgent.
        """
        if not self.card:
            self._fire_no_card_event(context)
            return {}

        return self.card

    # ------------------------------------------------------------------
    # Mode 2: handle_a2a — local dispatch entry point
    # ------------------------------------------------------------------
    async def handle_a2a(
        self,
        capability_id: str,
        payload: dict,
        agent_ctx,
        capability_ctx,
    ) -> dict:
        """
        Entry point for Mode 2 (A2A Direct) local dispatch.

        Called by SolicitorGeneral._dispatch_local() when this agent is
        registered as a local instance in AGENT_REGISTRY. Base implementation
        raises NotImplementedError. Each PlatformAgent subclass overrides this
        to dispatch to its own capability methods.

        Override pattern (e.g. DoorKeeperAgent):

            async def handle_a2a(self, capability_id, payload, agent_ctx, capability_ctx):
                dispatch = {
                    "Trust.Assign":       self.trust_assign,
                    "Agent.Authenticate": self.agent_authenticate,
                    # ... all capabilities this agent exposes via Mode 2
                }
                handler = dispatch.get(capability_id)
                if handler is None:
                    raise NotImplementedError(
                        f"Capability '{capability_id}' not found on "
                        f"{self.__class__.__name__}."
                    )
                return await handler(payload, agent_ctx, capability_ctx)

        No capability run() modules are modified to support Mode 2.
        The called agent's run() modules receive the same
        (payload, agent_ctx, capability_ctx) args they always do.
        startup_mode='a2a' on agent_ctx distinguishes this path for logging.
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

        NIST 800-53 CM-6: Configuration Settings.
        """
        self.log(
            event_type="platform_config_change_received",
            message=f"[CM-6] Configuration change received: {event.get('type')}",
            payload=event,
        )

    # ------------------------------------------------------------------
    # CM-6: Emit configuration change events
    # ------------------------------------------------------------------
    async def emit_configuration_changed(
        self,
        change_type: str,
        details: dict | None = None,
    ) -> None:
        """
        Broadcast a Platform.ConfigurationChanged event to all subscribed
        PlatformAgents via the injected PlatformEventBus.

        In-process only. Cross-agent Kafka publishing is handled by the
        Kafka Observability Publisher (Gap Registry 🔲 — not yet built).

        NIST 800-53 CM-6: Configuration Settings.
        """
        event = {
            "type":    change_type,
            "details": details or {},
            "source":  self.actor_name,
        }

        self.log(
            event_type="platform_config_change_emitted",
            message=f"[CM-6] Broadcasting configuration change: {change_type}",
            payload=event,
        )

        await self.event_bus.broadcast(self.PLATFORM_CONFIG_EVENT, event)

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """
        Unsubscribe this agent from the event bus.
        Call during platform teardown or agent lifecycle end
        to prevent stale handler references.
        """
        self.event_bus.unsubscribe(
            self.PLATFORM_CONFIG_EVENT,
            self.on_platform_configuration_change,
        )

        self.log(
            event_type="platform_agent_unregistered",
            message=f"{self.actor_name} unsubscribed from PlatformEventBus.",
            payload={"event_type": self.PLATFORM_CONFIG_EVENT},
        )
