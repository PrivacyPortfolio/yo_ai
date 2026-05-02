# core/runtime/platform_bootstrap.py
#
# Platform singleton construction — called once per Lambda cold start.
#
# Contract:
#   Construct every stateful platform object in dependency order and expose
#   route_fn — a plain async callable that any mode handler can call with a
#   JSON-RPC envelope and receive a response. No handler imports agent code.
#   No handler knows what route_fn is backed by.
#
# Agent independence:
#   This module does not import any agent class. All agents are independently deployed Lambda functions. 
#   YoAiRuntime dispatches calls to them via Lambda invoke — the platform routing layer never loads agent
#   code in-process.
#
# Dependency order:
#   1. PlatformEventBus        — no dependencies
#   2. capability_map           — loaded from shared/registries/capability_map.yaml
#   3. lambda_invoke adapter    — boto3-backed RPC adapter (testable via stub)
#   4. YoAiRuntime              — requires capability_map + tools
#   5. A2AValidator             — no dependencies
#   6. A2ATransport             — requires runtime + validator
#   7. route_fn                 — A2ATransport.handle_a2a, exposed as callable
#
# mesh_handler bus subscription is registered here after bus + route_fn exist.
#
# Usage:
#   from core.platform_bootstrap import bootstrap
#   _route_fn = bootstrap()   # idempotent — cached after first call

from __future__ import annotations

import os
from pathlib import Path
from typing import Awaitable, Callable

import yaml

from core.runtime.platform_event_bus import PlatformEventBus
from core.routing.yo_ai_runtime import YoAiRuntime
from core.routing.a2a_transport import A2ATransport
from core.routing.lambda_invoke_adapter import (
    make_lambda_invoke_fn,
    make_stub_invoke_fn,
)
from core.messages.a2a_validator import A2AValidator
from core.handlers.mesh_handler import register_on_bus
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("platform_bootstrap")

RouteFn = Callable[[dict], Awaitable[dict]]

_route_fn: RouteFn | None = None


def _load_capability_map() -> dict:
    try:
        map_path = (
            Path(__file__).resolve().parent.parent
            / "shared" / "registries" / "capability_map.yaml"
        )
        if not map_path.exists():
            LOG.write(
                event_type="bootstrap.CapabilityMapMissing",
                payload={"path": str(map_path)},
                context=None,
            )
            return {}
        with map_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as exc:
        LOG.write(
            event_type="bootstrap.CapabilityMapLoadFailed",
            payload={"error": str(exc)},
            context=None,
        )
        return {}


def bootstrap(*, stub_mode: bool = False) -> RouteFn:
    # stub_mode=True: use make_stub_invoke_fn() instead of boto3.
    # Pass stub_mode=True in tests and local development.
    global _route_fn
    if _route_fn is not None:
        return _route_fn

    LOG.write(
        event_type="bootstrap.Start",
        payload={"stub_mode": stub_mode},
        context=None,
    )

    # 1. Platform event bus
    event_bus = PlatformEventBus()

    # 2. Capability map
    capability_map = _load_capability_map()

    # 3. Lambda invoke adapter
    # In production: real boto3 calls to agent Lambda functions.
    # In tests / local dev: stub returns a fixed response without AWS.
    if stub_mode or os.environ.get("YO_AI_STUB_LAMBDA") == "1":
        lambda_invoke = make_stub_invoke_fn()
        LOG.write(
            event_type="bootstrap.StubAdapterActive",
            payload={"reason": "stub_mode or YO_AI_STUB_LAMBDA=1"},
            context=None,
        )
    else:
        lambda_invoke = make_lambda_invoke_fn(
            region_name=os.environ.get("AWS_REGION"),
        )

    # 4. YoAiRuntime
    # tools["lambda_invoke"] is the only RPC adapter needed at this stage.
    # tools["http_call"] can be added here when external handlers are built.
    runtime = YoAiRuntime(
        capability_map=capability_map,
        tools={
            "lambda_invoke": lambda_invoke,
        },
    )

    # 5. Validator
    validator = A2AValidator()

    # 6. Transport
    # A2ATransport now takes (solicitor_general, validator) but the SG
    # is no longer in-process — route_fn goes directly through the runtime.
    # We pass runtime.route as the routing callable via a minimal adapter.
    transport = A2ATransport(
        solicitor_general=_RuntimeAdapter(runtime),
        validator=validator,
    )

    # 7. route_fn
    _route_fn = transport.handle_a2a

    # Register mesh handler on the event bus now that both exist
    register_on_bus(event_bus, _route_fn)

    LOG.write(
        event_type="bootstrap.Complete",
        payload={
            "capability_count": len(capability_map.get("capabilities", {})),
            "stub_mode":        stub_mode,
        },
        context=None,
    )

    return _route_fn


class _RuntimeAdapter:
    # Minimal adapter so A2ATransport can call self._sg.route_a2a(envelope)
    # without any agent import. The SG is no longer in-process — all routing
    # goes through YoAiRuntime.route() which dispatches via Lambda invoke.
    # When YoAiRuntime.route() is fully wired, A2ATransport can be updated
    # to accept route_fn directly and this adapter removed.

    def __init__(self, runtime: YoAiRuntime) -> None:
        self._runtime = runtime

    async def route_a2a(self, envelope: dict) -> dict:
        return await self._runtime.route(envelope)
