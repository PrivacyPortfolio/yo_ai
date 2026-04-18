# agents/solicitor_general/sg10.py

from __future__ import annotations
from typing import Any, Dict

from core.platform_agent import PlatformAgent
from core.runtime.platform_event_bus import PlatformEventBus
from core.runtime.error_handler import ErrorHandler
from core.yoai_context import YoAiContext

from core.routing.runtime_agent_registry import RuntimeAgentRegistry
from core.routing.yo_ai_runtime import YoAiRuntime

from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("solicitor_general")


class SolicitorGeneralAgent(PlatformAgent):

    def __init__(
        self,
        *,
        card=None,
        extended_card=None,
        slim=False,
        event_bus: PlatformEventBus,
        capability_map=None,
        request_id: str | None = None,     # JSON-RPC id — seeds correlation_id
        task_id: str | None = None,
        runtime: YoAiRuntime | None = None,
        registry: RuntimeAgentRegistry | None = None,
    ):
        # ── PlatformAgent (→ YoAiAgent → BaseAgent) ───────────────────────
        # No ctx param. No correlation_id param — ids are not passed into
        # the chain; they are generated after construction via set_correlation().
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
            event_bus=event_bus,
        )

        # ── Runtime subsystems ─────────────────────────────────────────────
        self.runtime = runtime or YoAiRuntime(
            capability_map=capability_map or {},
            tools={},
        )
        self.registry = registry or RuntimeAgentRegistry()

        # ── Message ids — generated once after construction ────────────────
        # generate_message_ids() lives on BaseAgent — pure, overridable.
        # set_correlation() writes the results to self.correlation_id /
        # self.task_id, which _build_context() will pick up on every request.
        if request_id or task_id:
            self.set_correlation(request_id=request_id, task_id=task_id)

    # ── Mode 1 — A2A HTTP routing ──────────────────────────────────────────
    # Entry point: "a2a"   protocolBinding: JSONRPC_HTTP

    async def route_a2a(self, envelope: dict) -> dict:
        ctx = self._build_context(envelope)
        return await self.runtime.route_a2a(envelope, ctx)

    # ── Mode 2 — A2A Direct (mesh) ────────────────────────────────────────
    # Entry point: "mesh"   protocolBinding: A2A_DIRECT

    async def handle_a2a(
        self,
        capability_id: str,
        payload: dict,
        ctx: YoAiContext,
    ) -> dict:
        # ── SG capability dispatch ─────────────────────────────────────────
        dispatch = {
            "Just-Ask":                   self.just_ask,
            "Event.Log":                  self.event_log,
            "Request-Response.Correlate": self.request_response_correlate,
        }
        handler = dispatch.get(capability_id)
        if handler is None:
            raise NotImplementedError(
                f"Capability '{capability_id}' not found on SG."
            )
        return await handler(payload, ctx)

    # ── Mode 3 — OpenAI API ───────────────────────────────────────────────
    # Entry point: "api"   protocolBinding: OPENAI_API

    def route(self, envelope: dict, request_id: str, mode: str = "api") -> dict:
        ctx = self._build_context(envelope)
        decision = self.runtime.route_api(envelope, request_id, ctx)

        LOG.write(
            event_type="SG.Route",
            payload={
                "capability": decision["capability_id"],
                "mode":       mode,
            },
            context=ctx,
            include=["instance_id", "correlation_id", "task_id"],
        )
        return decision

    # ── Mode 4 — MCP / Starlette ──────────────────────────────────────────
    # Entry point: "app"   protocolBinding: MCP
    # (handler: http/app_mount.py — routed externally, no method here)

    # ── Mode 5 — REST Operation ───────────────────────────────────────────
    # Entry point: "op"   protocolBinding: REST
    # (per-capability handler — routed externally, no method here)

    # ── SG capabilities ───────────────────────────────────────────────────

    async def just_ask(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.solicitor_general.capabilities.just_ask import run
        return await run(payload, ctx)

    async def event_log(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.solicitor_general.capabilities.event_log import run
        return await run(payload, ctx)

    async def resume_processing(self, payload: dict, ctx: YoAiContext) -> dict:
        raise NotImplementedError("resumeProcessing() deferred.")

    # ── CM-6: react to configuration changes ──────────────────────────────

    async def on_platform_configuration_change(self, event: dict) -> None:
        # ── super() logs receipt; SG reacts to specific change types ──────
        await super().on_platform_configuration_change(event)
        if event.get("type") in ("capability_map_updated", "route_table_updated"):
            LOG.write(
                event_type="SG.CapabilityMapReload",
                payload=event,
                context=None,        # platform lifecycle event — not request-scoped
                include=["instance_id"],
            )

    # ── Envelope builders ─────────────────────────────────────────────────

    def _success_envelope(
        self,
        capability_id: str,
        result: dict,
        ctx: YoAiContext,
    ) -> dict:
        # ── correlation_id and task_id come from the request ctx ───────────
        # Never from self.* — the ctx was built from the live envelope
        # and carries the ids that belong to this specific request.
        from datetime import datetime, timezone
        return {
            "jsonrpc": "2.0",
            "id":      ctx.get("correlation_id"),
            "result":  result,
            "metadata": {
                "capability": capability_id,
                "taskId":     ctx.get("task_id"),
                "timestamp":  datetime.now(timezone.utc).isoformat(),
            },
        }

    def _error_envelope(
        self,
        code: int,
        message: str,
        ctx: YoAiContext | None = None,
    ) -> dict:
        # ── correlation_id from ctx when available, None otherwise ─────────
        return {
            "jsonrpc": "2.0",
            "id":      ctx.get("correlation_id") if ctx else None,
            "error":   {"code": code, "message": message},
        }
