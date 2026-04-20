# tests/test_platform_event_bus.py
#
# Standalone test for PlatformEventBus.
# No test framework required — run directly:
#
#   python tests/test_platform_event_bus.py
#
# Every test prints the platform events it expects to see in production,
# giving you a logged trace of every event the bus emits. A summary of
# pass / fail is printed at the end.
#
# Scenarios covered:
#   1. subscribe + publish (synchronous, single listener)
#   2. Multiple listeners on same event type, called in registration order
#   3. Wildcard listener ("*") receives all event types
#   4. unsubscribe removes exactly the target listener
#   5. Failing listener does not crash the bus or other listeners
#   6. publish_async with async and sync listeners mixed
#   7. listener_count() — per event type and total
#   8. recent_events() rolling window
#   9. clear_listeners() resets state
#  10. publish returns correct notified count
#  11. Event shape: event_type, data, source all present in history
#  12. No listeners: publish returns 0 silently

import asyncio
import sys
import traceback
from collections import defaultdict
from typing import Any, List

sys.path.insert(0, ".")  # run from repo root

from core.platform_event_bus import PlatformEventBus


# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------

RESULTS: List[dict] = []
EMITTED_EVENTS: List[dict] = []   # accumulated log of every platform event seen


def _log_event(label: str, event_type: str, data: Any, source: str = None) -> None:
    record = {
        "test":       label,
        "event_type": event_type,
        "data":       data,
        "source":     source,
    }
    EMITTED_EVENTS.append(record)
    print(f"  [EVENT] {event_type} | source={source!r} | data={data!r}")


def _pass(name: str) -> None:
    RESULTS.append({"name": name, "status": "PASS"})
    print(f"  [PASS]  {name}")


def _fail(name: str, reason: str) -> None:
    RESULTS.append({"name": name, "status": "FAIL", "reason": reason})
    print(f"  [FAIL]  {name} — {reason}")


def _section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def _assert(condition: bool, test_name: str, reason: str = "") -> None:
    if condition:
        _pass(test_name)
    else:
        _fail(test_name, reason or "assertion failed")


# ---------------------------------------------------------------------------
# 1. subscribe + publish (synchronous, single listener)
# ---------------------------------------------------------------------------

def test_subscribe_and_publish():
    _section("1. subscribe + publish — single listener")
    bus = PlatformEventBus()
    received = []

    def listener(event_type, data):
        _log_event("1", event_type, data, source="test-agent")
        received.append((event_type, data))

    bus.subscribe("Trust.Assign", listener, owner="test-agent")
    count = bus.publish("Trust.Assign", {"tier": "tier-1"}, source="door-keeper")

    _assert(count == 1, "publish returns 1 notified", f"got {count}")
    _assert(len(received) == 1, "listener called once", f"got {len(received)}")
    _assert(received[0] == ("Trust.Assign", {"tier": "tier-1"}),
            "listener receives correct args",
            f"got {received[0]}")


# ---------------------------------------------------------------------------
# 2. Multiple listeners — called in registration order
# ---------------------------------------------------------------------------

def test_multiple_listeners_order():
    _section("2. Multiple listeners — registration order preserved")
    bus = PlatformEventBus()
    order = []

    def first(event_type, data):
        _log_event("2", event_type, data, source="agent-a")
        order.append("first")

    def second(event_type, data):
        _log_event("2", event_type, data, source="agent-b")
        order.append("second")

    bus.subscribe("Handler.Error", first,  owner="agent-a")
    bus.subscribe("Handler.Error", second, owner="agent-b")
    bus.publish("Handler.Error", {"error": "timeout"}, source="solicitor-general")

    _assert(order == ["first", "second"],
            "listeners called in registration order",
            f"got {order}")


# ---------------------------------------------------------------------------
# 3. Wildcard listener receives all event types
# ---------------------------------------------------------------------------

def test_wildcard_listener():
    _section("3. Wildcard listener ('*') — receives all event types")
    bus = PlatformEventBus()
    seen = []

    def wildcard(event_type, data):
        _log_event("3", event_type, data, source="sentinel")
        seen.append(event_type)

    bus.subscribe_all(wildcard, owner="sentinel")
    bus.publish("Trust.Assign",  {"tier": "tier-0"}, source="door-keeper")
    bus.publish("Budget.Exceeded", {"limit": 100},   source="trust-assessor")

    _assert("Trust.Assign"    in seen, "wildcard sees Trust.Assign")
    _assert("Budget.Exceeded" in seen, "wildcard sees Budget.Exceeded")
    _assert(len(seen) == 2,            "wildcard sees exactly 2 events", f"got {seen}")


# ---------------------------------------------------------------------------
# 4. unsubscribe removes exactly the target listener
# ---------------------------------------------------------------------------

def test_unsubscribe():
    _section("4. unsubscribe — target listener removed, others intact")
    bus = PlatformEventBus()
    removed_calls = []
    kept_calls    = []

    def to_remove(event_type, data):
        _log_event("4-removed", event_type, data)
        removed_calls.append(event_type)

    def to_keep(event_type, data):
        _log_event("4-kept", event_type, data)
        kept_calls.append(event_type)

    bus.subscribe("Platform.ConfigurationChanged", to_remove, owner="old-agent")
    bus.subscribe("Platform.ConfigurationChanged", to_keep,   owner="new-agent")
    bus.unsubscribe("Platform.ConfigurationChanged", to_remove)
    bus.publish("Platform.ConfigurationChanged", {"type": "capability_map_updated"},
                source="solicitor-general")

    _assert(len(removed_calls) == 0, "unsubscribed listener not called")
    _assert(len(kept_calls) == 1,    "remaining listener still called")


# ---------------------------------------------------------------------------
# 5. Failing listener does not crash bus or other listeners
# ---------------------------------------------------------------------------

def test_failing_listener_isolation():
    _section("5. Failing listener — bus continues, other listeners unaffected")
    bus = PlatformEventBus()
    survivor_calls = []

    def crasher(event_type, data):
        _log_event("5-crasher", event_type, data)
        raise RuntimeError("intentional test failure")

    def survivor(event_type, data):
        _log_event("5-survivor", event_type, data)
        survivor_calls.append(event_type)

    bus.subscribe("Handler.Error", crasher,  owner="crasher")
    bus.subscribe("Handler.Error", survivor, owner="survivor")

    # Should not raise
    try:
        count = bus.publish("Handler.Error", {"msg": "boom"}, source="incident-responder")
        _assert(True, "publish does not raise when listener fails")
    except Exception as exc:
        _assert(False, "publish does not raise when listener fails", str(exc))

    _assert(len(survivor_calls) == 1, "survivor listener still called after crasher")
    # notified count reflects only successful calls
    _assert(count == 1, "notified count is 1 (crasher excluded)", f"got {count}")


# ---------------------------------------------------------------------------
# 6. publish_async — async and sync listeners mixed
# ---------------------------------------------------------------------------

async def test_publish_async():
    _section("6. publish_async — async and sync listeners mixed")
    bus = PlatformEventBus()
    received = []

    def sync_listener(event_type, data):
        _log_event("6-sync", event_type, data, source="sync-agent")
        received.append(("sync", event_type))

    async def async_listener(event_type, data):
        _log_event("6-async", event_type, data, source="async-agent")
        received.append(("async", event_type))

    bus.subscribe("SG.CapabilityMapReload", sync_listener,  owner="sync-agent")
    bus.subscribe("SG.CapabilityMapReload", async_listener, owner="async-agent")

    count = await bus.publish_async(
        "SG.CapabilityMapReload",
        {"type": "route_table_updated"},
        source="solicitor-general",
    )

    _assert(count == 2, "both listeners notified", f"got {count}")
    _assert(("sync",  "SG.CapabilityMapReload") in received, "sync listener called")
    _assert(("async", "SG.CapabilityMapReload") in received, "async listener called")


# ---------------------------------------------------------------------------
# 7. listener_count()
# ---------------------------------------------------------------------------

def test_listener_count():
    _section("7. listener_count() — per event type and total")
    bus = PlatformEventBus()

    bus.subscribe("Trust.Assign",  lambda e, d: None, owner="a")
    bus.subscribe("Trust.Assign",  lambda e, d: None, owner="b")
    bus.subscribe("Handler.Error", lambda e, d: None, owner="c")
    bus.subscribe_all(             lambda e, d: None, owner="d")

    _assert(bus.listener_count("Trust.Assign")  == 2, "Trust.Assign has 2 listeners")
    _assert(bus.listener_count("Handler.Error") == 1, "Handler.Error has 1 listener")
    _assert(bus.listener_count("*")             == 1, "wildcard has 1 listener")
    _assert(bus.listener_count()               == 4, "total is 4", f"got {bus.listener_count()}")


# ---------------------------------------------------------------------------
# 8. recent_events() rolling window
# ---------------------------------------------------------------------------

def test_recent_events():
    _section("8. recent_events() — rolling history window")
    bus = PlatformEventBus()

    for i in range(5):
        bus.publish(f"Test.Event.{i}", {"i": i}, source="test")

    recent = bus.recent_events(n=3)
    _assert(len(recent) == 3, "recent_events(3) returns 3", f"got {len(recent)}")
    _assert(recent[-1]["event_type"] == "Test.Event.4",
            "most recent event is last", f"got {recent[-1]['event_type']}")

    print("  [LOG] Recent events (last 3):")
    for ev in recent:
        _log_event("8", ev["event_type"], ev["data"], ev.get("source"))


# ---------------------------------------------------------------------------
# 9. clear_listeners()
# ---------------------------------------------------------------------------

def test_clear_listeners():
    _section("9. clear_listeners() — resets all subscriptions")
    bus = PlatformEventBus()
    received = []

    bus.subscribe("Any.Event", lambda e, d: received.append(e), owner="agent")
    bus.clear_listeners()
    bus.publish("Any.Event", {}, source="test")

    _assert(len(received) == 0, "no listeners called after clear_listeners()")
    _assert(bus.listener_count() == 0, "listener_count() is 0 after clear")


# ---------------------------------------------------------------------------
# 10. publish returns correct notified count
# ---------------------------------------------------------------------------

def test_publish_notified_count():
    _section("10. publish — notified count is accurate")
    bus = PlatformEventBus()

    for i in range(4):
        bus.subscribe("Budget.Exceeded", lambda e, d: None, owner=f"agent-{i}")

    count = bus.publish("Budget.Exceeded", {"limit": 500}, source="trust-assessor")
    _assert(count == 4, "notified count is 4", f"got {count}")

    count_no_listeners = bus.publish("Unknown.Event", {})
    _assert(count_no_listeners == 0, "notified count is 0 with no listeners")


# ---------------------------------------------------------------------------
# 11. Event shape — all fields present in history
# ---------------------------------------------------------------------------

def test_event_shape_in_history():
    _section("11. Event shape — event_type, data, source in history")
    bus = PlatformEventBus()
    bus.publish("Handler.Complete", {"capability": "Trust.Assign"}, source="door-keeper")

    history = bus.recent_events(n=1)
    _assert(len(history) == 1, "event recorded in history")

    ev = history[0]
    _assert("event_type" in ev, "event has event_type field")
    _assert("data"       in ev, "event has data field")
    _assert("source"     in ev, "event has source field")
    _assert(ev["event_type"] == "Handler.Complete",        "event_type matches")
    _assert(ev["source"]     == "door-keeper",             "source matches")
    _assert(ev["data"]["capability"] == "Trust.Assign",    "data payload matches")

    _log_event("11", ev["event_type"], ev["data"], ev.get("source"))


# ---------------------------------------------------------------------------
# 12. No listeners — publish is silent, returns 0
# ---------------------------------------------------------------------------

def test_no_listeners_silent():
    _section("12. No listeners — publish is silent, returns 0")
    bus = PlatformEventBus()

    try:
        count = bus.publish("Unregistered.Event", {"x": 1}, source="anyone")
        _assert(count == 0,  "returns 0 with no listeners", f"got {count}")
        _assert(True, "publish with no listeners does not raise")
    except Exception as exc:
        _assert(False, "publish with no listeners does not raise", str(exc))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def run_all():
    print("\nPlatformEventBus test suite")
    print("=" * 60)

    # Sync tests
    test_subscribe_and_publish()
    test_multiple_listeners_order()
    test_wildcard_listener()
    test_unsubscribe()
    test_failing_listener_isolation()
    test_listener_count()
    test_recent_events()
    test_clear_listeners()
    test_publish_notified_count()
    test_event_shape_in_history()
    test_no_listeners_silent()

    # Async tests
    await test_publish_async()

    # Summary
    print(f"\n{'='*60}")
    print("EMITTED PLATFORM EVENTS (logged during test run):")
    print(f"{'='*60}")
    for i, ev in enumerate(EMITTED_EVENTS, 1):
        print(f"  {i:>3}. [{ev['test']}] {ev['event_type']} | "
              f"source={ev['source']!r} | data={ev['data']!r}")

    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    if failed:
        print("\nFAILED:")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}: {r.get('reason', '')}")
    print("=" * 60)

    return failed


if __name__ == "__main__":
    failed = asyncio.run(run_all())
    sys.exit(1 if failed else 0)
