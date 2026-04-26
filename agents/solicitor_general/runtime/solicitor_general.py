# agents/solicitor_general/runtime/solicitor_general.py

from __future__ import annotations
from typing import Any, Dict

from core.platform_agent import PlatformAgent
from core.runtime.platform_event_bus import PlatformEventBus
from core.yoai_context import YoAiContext
from core.runtime.envelope import success_envelope, error_envelope, extract
from core.runtime.error_pipeline import ErrorPipeline

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
        request_id: str | None = None,
        task_id: str | None = None,
        runtime: YoAiRuntime | None = None,
        registry: RuntimeAgentRegistry | None = None,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
            event_bus=event_bus,
        )

        # Runtime subsystems
        self.runtime  = runtime  or YoAiRuntime(capability_map=capability_map or {}, tools={})
        self.registry = registry or RuntimeAgentRegistry()

        # Message ids
        if request_id or task_id:
            self.set_correlation(request_id=request_id, task_id=task_id)

        # Error pipeline
        # Inject incident_responder_fn at platform bootstrap once the IR agent
        # instance exists. Forwarding is silently skipped until then.
        # Example:
        #   sg.error_pipeline = ErrorPipeline(
        #       incident_responder_fn=ir_agent.handle_exception
        #   )
        self.error_pipeline: ErrorPipeline = ErrorPipeline(incident_responder_fn=None)

    # Mode 1: A2A HTTP routing
    # Entry point: "a2a"   protocolBinding: JSONRPC_HTTP

    async def route_a2a(self, envelope: dict) -> dict:
        ctx = self._build_context(envelope)
        return await self.runtime.route_a2a(envelope, ctx)

    # Mode 2: A2A Direct (mesh)
    # Entry point: "mesh"   protocolBinding: A2A_DIRECT

    async def handle_a2a(
        self,
        capability_id: str,
        payload: dict,
        ctx: YoAiContext,
    ) -> dict:
        dispatch = {
            "Just-Ask":                   self.just_ask,
            "Event.Log":                  self.event_log,
            "Request-Response.Correlate": self.request_response_correlate,
        }
        handler = dispatch.get(capability_id)
        if handler is None:
            raise NotImplementedError(f"Capability '{capability_id}' not found on SG.")
        return await handler(payload, ctx)

    # Mode 3: OpenAI API
    # Entry point: "api"   protocolBinding: OPENAI_API

    def route(self, envelope: dict, request_id: str, mode: str = "api") -> dict:
        ctx      = self._build_context(envelope)
        decision = self.runtime.route_api(envelope, request_id, ctx)
        LOG.write(
            event_type="SG.Route",
            payload={"capability": decision["capability_id"], "mode": mode},
            context=ctx,
            include=["instance_id", "correlation_id", "task_id"],
        )
        return decision

    # Mode 4: MCP / Starlette  (routed externally)
    # Mode 5: REST Operation   (routed externally)

    # SG capabilities

    async def just_ask(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.solicitor_general.capabilities.just_ask import run
        return await run(payload, ctx)

    async def event_log(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.solicitor_general.capabilities.event_log import run
        return await run(payload, ctx)

    async def resume_processing(self, payload: dict, ctx: YoAiContext) -> dict:
        raise NotImplementedError("resumeProcessing() deferred.")

    # CM-6: react to configuration changes

    async def on_platform_configuration_change(self, event: dict) -> None:
        await super().on_platform_configuration_change(event)
        if event.get("type") in ("capability_map_updated", "route_table_updated"):
            LOG.write(
                event_type="SG.CapabilityMapReload",
                payload=event,
                context=None,
                include=["instance_id"],
            )

    # Envelope builders (delegate to core.envelope)
    # These remain as convenience methods so existing SG call sites work
    # without change. New agents should import from core.envelope directly.

    def _success_envelope(
        self,
        capability_id: str,
        result: dict,
        ctx: YoAiContext,
    ) -> dict:
        return success_envelope(capability_id, result, ctx)

    def _error_envelope(
        self,
        code: int,
        message: str,
        ctx: YoAiContext | None = None,
        data: dict | None = None,
    ) -> dict:
        return error_envelope(code, message, ctx, data)
