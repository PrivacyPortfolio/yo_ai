# core/platform_event_bus.py
#
# Internal platform event bus for synchronous, in-process agent communication.
#
# Purpose:
#   PlatformEventBus is the internal publish/subscribe mechanism for platform-level
#   events that need to be communicated between agents or components within the same
#   execution environment. It is distinct from:
#
#     Kafka (KafkaPublisher, Gap Registry 🔲)
#       — external, durable, async, cross-service event streaming
#       — used for agent-auth, agent-registrations, subscriber topics
#       — the observability and persistence layer
#
#     LogBootstrapper
#       — structured logging to CloudWatch / DynamoDB / S3 sinks
#       — audit and compliance records
#
#   PlatformEventBus is:
#       — synchronous, in-process, ephemeral
#       — used for agents/components to signal each other within a Lambda invocation
#       — for example: SolicitorGeneral notifying Door-Keeper of a routing decision,
#         or The-Sentinel reacting to a budget breach event mid-invocation
#
# Usage:
#   BUS = PlatformEventBus()                    # one per Lambda execution environment
#   BUS.subscribe("Trust.Assign", handler_fn)   # register a listener
#   BUS.publish("Trust.Assign", data)           # emit an event to all listeners
#   BUS.publish_async("Trust.Assign", data)     # emit without waiting for listeners
#
# Injection:
#   Passed as event_bus= to SolicitorGeneralAgent constructor (Gap Registry v2).
#   Instantiated once per handler module alongside AGENT and LOG.
#
# Current state:
#   Handlers instantiate BUS = PlatformEventBus() but do not yet call BUS.publish().
#   This is intentional — the bus is ready for use when SG routing, Trust-Assessor,
#   and Sentinel monitoring patterns require in-process signaling.
#
# Thread safety:
#   Lambda execution environments are single-threaded per invocation.
#   The bus is not thread-safe by design — use Kafka for cross-invocation events.

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class PlatformEventBus:
    """
    Synchronous in-process publish/subscribe event bus.

    Listeners are registered per event_type and called synchronously
    in registration order when an event is published.

    Async listeners are supported via publish_async() which runs them
    on the current event loop.
    """

    def __init__(self) -> None:
        # event_type → list of (listener_fn, owner_name)
        self._listeners: Dict[str, List[tuple]] = defaultdict(list)
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 100   # keep last N events for debugging

    # ------------------------------------------------------------------
    # Subscribe
    # ------------------------------------------------------------------

    def subscribe(
        self,
        event_type: str,
        listener: Callable,
        owner: str = "unknown",
    ) -> None:
        """
        Register a listener for a specific event type.

        Args:
            event_type : The event type string to listen for
                         (e.g. "Trust.Assign", "Handler.Error", "Budget.Exceeded")
            listener   : Callable invoked with (event_type, data) when event fires
            owner      : Name of the subscribing agent/component for audit
        """
        self._listeners[event_type].append((listener, owner))
        logger.debug(
            "PlatformEventBus: %s subscribed to '%s'", owner, event_type
        )

    def subscribe_all(self, listener: Callable, owner: str = "unknown") -> None:
        """
        Register a listener for ALL event types.
        Uses the wildcard key "*".
        """
        self.subscribe("*", listener, owner)

    def unsubscribe(self, event_type: str, listener: Callable) -> None:
        """Remove a specific listener from an event type."""
        self._listeners[event_type] = [
            (fn, owner) for fn, owner in self._listeners[event_type]
            if fn is not listener
        ]

    # ------------------------------------------------------------------
    # Publish (synchronous)
    # ------------------------------------------------------------------

    def publish(
        self,
        event_type: str,
        data: Any = None,
        source: Optional[str] = None,
    ) -> int:
        """
        Publish an event synchronously to all registered listeners.

        Listeners for the specific event_type are called first,
        then wildcard ("*") listeners.

        Listener exceptions are caught and logged — a failing listener
        must never crash the publishing agent.

        Args:
            event_type : Event type string
            data       : Event payload (any JSON-serializable value)
            source     : Name of the publishing agent/component

        Returns:
            Number of listeners successfully notified.
        """
        event = {
            "event_type": event_type,
            "data":        data,
            "source":      source,
        }

        self._record(event)

        notified = 0
        targets = (
            list(self._listeners.get(event_type, []))
            + list(self._listeners.get("*", []))
        )

        for listener_fn, owner in targets:
            try:
                listener_fn(event_type, data)
                notified += 1
            except Exception as exc:
                logger.warning(
                    "PlatformEventBus: listener '%s' raised on '%s' — %s",
                    owner, event_type, exc
                )

        if targets:
            logger.debug(
                "PlatformEventBus: published '%s' from '%s' → %d listener(s)",
                event_type, source, notified
            )

        return notified

    # ------------------------------------------------------------------
    # Publish (async)
    # ------------------------------------------------------------------

    async def publish_async(
        self,
        event_type: str,
        data: Any = None,
        source: Optional[str] = None,
    ) -> int:
        """
        Publish an event to all registered listeners asynchronously.
        Async listeners are awaited; sync listeners are called directly.

        Use this when the publishing context is already async (e.g. inside
        an async run() capability module).
        """
        event = {
            "event_type": event_type,
            "data":        data,
            "source":      source,
        }

        self._record(event)

        notified = 0
        targets = (
            list(self._listeners.get(event_type, []))
            + list(self._listeners.get("*", []))
        )

        for listener_fn, owner in targets:
            try:
                if asyncio.iscoroutinefunction(listener_fn):
                    await listener_fn(event_type, data)
                else:
                    listener_fn(event_type, data)
                notified += 1
            except Exception as exc:
                logger.warning(
                    "PlatformEventBus: async listener '%s' raised on '%s' — %s",
                    owner, event_type, exc
                )

        return notified

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def listener_count(self, event_type: Optional[str] = None) -> int:
        """Return number of listeners for an event type, or total if None."""
        if event_type:
            return len(self._listeners.get(event_type, []))
        return sum(len(v) for v in self._listeners.values())

    def recent_events(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return the last n published events (for debugging/testing)."""
        return self._event_history[-n:]

    def clear_listeners(self) -> None:
        """Remove all listeners. Useful in tests."""
        self._listeners.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _record(self, event: Dict[str, Any]) -> None:
        """Keep a rolling window of recent events for debugging."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
