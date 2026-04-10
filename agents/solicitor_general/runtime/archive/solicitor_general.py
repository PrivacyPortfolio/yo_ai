# agents/solicitor_general/solicitor_general.py

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from core.platform_agent import PlatformAgent, PlatformEventBus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Agent Registry
#
# Maps agent names to their dispatch strategy.
# SolicitorGeneral consults this in route_a2a() to decide:
#   local  → call the held Python instance directly (zero network overhead)
#   lambda → invoke via boto3 (isolated, auto-scaling)
#
# Populated at platform startup via register_local_agent() or
# register_lambda_agent(). Not hardcoded — agents register themselves.
#
# No other agent code is modified to support Mode 2.
# Calling agents construct the same A2A envelope they always would.
# Called agents receive (payload, agent_ctx, capability_ctx) as always.
# Only SolicitorGeneral knows this registry exists.
# ---------------------------------------------------------------------------

_AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_local_agent(agent_id: str, instance: Any) -> None:
    """
    Register a local in-process agent instance.

    Call at platform startup for agents on the critical path
    (e.g. Door-Keeper during authentication, SolicitorGeneral itself).

    Args:
        agent_id : Canonical agent identifier (e.g. "door-keeper")
        instance : Instantiated agent object with handle_a2a() method
    """
    _AGENT_REGISTRY[agent_id] = {
        "type":    "local",
        "handler": instance,
    }
    logger.info("AgentRegistry: registered local agent '%s'.", agent_id)


def register_lambda_agent(agent_id: str, function_name: str) -> None:
    """
    Register a Lambda-backed agent.

    Call at platform startup for agents doing heavy AI work or external I/O
    (e.g. Data-Steward, Purchasing-Agent, Incident-Responder).

    Args:
        agent_id      : Canonical agent identifier (e.g. "data-steward")
        function_name : Lambda function name or ARN
    """
    _AGENT_REGISTRY[agent_id] = {
        "type":          "lambda",
        "function_name": function_name,
    }
    logger.info(
        "AgentRegistry: registered Lambda agent '%s' → function '%s'.",
        agent_id, function_name
    )


def get_agent_registry() -> Dict[str, Dict[str, Any]]:
    """Return the current agent registry. Read-only."""
    return dict(_AGENT_REGISTRY)


# ---------------------------------------------------------------------------
# SolicitorGeneralAgent
# ---------------------------------------------------------------------------

class SolicitorGeneralAgent(PlatformAgent):
    """
    Solicitor-General: root governance, routing, and task management agent.

    The SolicitorGeneral is the central authority of the platform. It:
      - Receives all inbound capability requests (Mode 3: API Gateway)
      - Validates envelopes and governance labels
      - Routes capabilities to the correct agent and dispatch mode
      - Manages task lifecycle and workflow continuity
      - Enforces trust vectors and capability-level authorization
      - Generates correlation IDs and task IDs
      - Logs all routing decisions for audit

    SolicitorGeneral is NOT a typical PlatformAgent — it has special duties
    as Broker and TaskManager. Do NOT use it as a pattern for other agents.
    Use door_keeper.py as the reference pattern instead.

    Three dispatch modes:
      Mode 2 — A2A Direct (startup_mode="a2a")
          Internal agent-to-agent calls routed through SG.
          Calling agent constructs a standard A2A envelope addressed to
          targetAgentId. SG consults AGENT_REGISTRY and dispatches either:
            local  → direct Python method call, zero network overhead
            lambda → boto3 invocation, isolated + auto-scaling
          NO OTHER AGENT CODE IS MODIFIED for Mode 2 support.

      Mode 3 — API Gateway (startup_mode="api")
          External HTTP requests through API Gateway → Lambda → SG.
          route() returns a routing decision dict for the handler to execute.

      Mode 1 — Starlette (startup_mode="starlette")
          HTTP requests handled by Starlette middleware (future).

    Event Bus:
      SolicitorGeneral receives Platform.ConfigurationChanged (inherited).
      Emits routing and governance events.

    Known open items (Gap Registry v2 — Priority 1):
      🔲 SG self-routing: Just-Ask, Event.Log, Request-Response.Correlate
      🔲 Agent directory: named instances e.g. DataSteward('BillyJo-Work')
      🔲 resumeProcessing(): deferred — storage location TBD
    """

    PLATFORM_CONFIG_EVENT = "Platform.ConfigurationChanged"

    # Class-level instance registry — keyed by correlation_id
    _instance_registry: dict[str, "SolicitorGeneralAgent"] = {}

    def __init__(
        self,
        *,
        card=None,
        extended_card=None,
        slim=False,
        event_bus: PlatformEventBus,
        capability_map: dict | None = None,
        correlation_id: str | None = None,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
            event_bus=event_bus,
        )

        self.capability_map = capability_map or {}

        if correlation_id:
            self.set_correlation(correlation_id)
            SolicitorGeneralAgent._instance_registry[correlation_id] = self

    # ------------------------------------------------------------------
    # Instance registry — workflow continuity
    # ------------------------------------------------------------------

    @classmethod
    def get_or_create(
        cls,
        *,
        event_bus: PlatformEventBus,
        capability_map: dict | None = None,
        correlation_id: str | None = None,
        **kwargs,
    ) -> "SolicitorGeneralAgent":
        """
        Return an existing SG instance for a correlation_id if one exists,
        otherwise create a new one. Use this instead of the constructor.
        """
        if correlation_id and correlation_id in cls._instance_registry:
            return cls._instance_registry[correlation_id]
        return cls(
            event_bus=event_bus,
            capability_map=capability_map,
            correlation_id=correlation_id,
            **kwargs,
        )

    @classmethod
    def clear_registry(cls) -> None:
        """Clear instance registry. Testing and teardown only."""
        cls._instance_registry.clear()

    # ------------------------------------------------------------------
    # Mode 3 routing — API Gateway path
    # Returns a routing decision dict for the handler to execute.
    # ------------------------------------------------------------------

    def route(
        self,
        envelope: dict,
        request_id: str,
        mode: str = "api",
    ) -> dict:
        """
        Route an inbound capability request (Mode 3 — API Gateway).

        Validates the envelope, strips caller-supplied governance labels,
        builds AgentContext + CapabilityContext, and returns a routing
        decision dict for the handler to execute.

        For internal agent-to-agent calls, use route_a2a() instead.
        """
        capability_id, payload = self._extract_capability(envelope)
        agent_ctx      = self._build_agent_context(envelope, mode=mode)
        capability_ctx = self._build_capability_context(capability_id, envelope)

        self.log(
            event_type="SG.Route",
            message=f"Routing capability: {capability_id}",
            payload={
                "capability":    capability_id,
                "caller":        agent_ctx.caller,
                "correlationId": agent_ctx.correlation_id,
                "taskId":        agent_ctx.task_id,
                "mode":          mode,
                "requestId":     request_id,
            },
        )

        return {
            "capability_id":  capability_id,
            "payload":        payload,
            "agent_ctx":      agent_ctx,
            "capability_ctx": capability_ctx,
            "request_id":     request_id,
        }

    # ------------------------------------------------------------------
    # Mode 2 routing — A2A Direct path
    # Dispatches internally without touching any other agent's code.
    # ------------------------------------------------------------------

    async def route_a2a(self, envelope: dict) -> dict:
        """
        Route an internal agent-to-agent request (Mode 2 — A2A Direct).

        Called by any agent that needs to invoke another agent's capability
        without going through HTTP. The calling agent constructs a standard
        A2A envelope — this method handles everything else.

        Envelope shape:
            {
                "jsonrpc":  "2.0",
                "id":       "<correlationId>",
                "method":   "a2a/request",
                "params": {
                    "targetAgentId": "door-keeper",
                    "capability":    "Trust.Assign",
                    "payload":       { ... },
                    "correlationId": "<id>",
                    "taskId":        "<id>"
                }
            }

        Dispatch:
            local  → agent.handle_a2a(capability_id, payload, agent_ctx, capability_ctx)
            lambda → boto3.invoke(function_name, envelope)

        Returns:
            A2A-compliant response envelope. Never raises — errors returned
            as structured error envelopes.

        No other agent code is modified to support this method.
        """
        params        = envelope.get("params", {})
        target_id     = params.get("targetAgentId", "")
        capability_id = params.get("capability", "")
        correlation_id = (
            envelope.get("id")
            or params.get("correlationId")
        )

        self.log(
            event_type="SG.RouteA2A",
            message=f"A2A Direct routing: {target_id} / {capability_id}",
            payload={
                "targetAgentId": target_id,
                "capability":    capability_id,
                "correlationId": correlation_id,
                "taskId":        params.get("taskId"),
            },
        )

        # Validate: target and capability must be present
        if not target_id or not capability_id:
            return self._error_envelope(
                correlation_id,
                code=-32602,
                message="route_a2a: targetAgentId and capability are required.",
            )

        # Look up the target in AGENT_REGISTRY
        entry = _AGENT_REGISTRY.get(target_id)
        if entry is None:
            self.log(
                event_type="SG.RouteA2A.NotFound",
                message=f"A2A Direct: target agent '{target_id}' not in registry.",
                payload={"targetAgentId": target_id, "correlationId": correlation_id},
            )
            return self._error_envelope(
                correlation_id,
                code=-32601,
                message=f"Target agent not found: '{target_id}'",
            )

        # Build contexts (startup_mode="a2a" distinguishes this path)
        _, payload = self._extract_capability({"capability": capability_id, **params})
        agent_ctx      = self._build_agent_context(params, mode="a2a")
        capability_ctx = self._build_capability_context(capability_id, params)

        # Dispatch based on registry entry type
        if entry["type"] == "local":
            return await self._dispatch_local(
                entry, target_id, capability_id, payload, agent_ctx, capability_ctx,
                correlation_id
            )
        elif entry["type"] == "lambda":
            return await self._dispatch_lambda(
                entry, target_id, envelope, correlation_id
            )
        else:
            return self._error_envelope(
                correlation_id,
                code=-32603,
                message=f"Unknown registry entry type '{entry['type']}' for '{target_id}'",
            )

    async def _dispatch_local(
        self,
        entry: dict,
        target_id: str,
        capability_id: str,
        payload: dict,
        agent_ctx: Any,
        capability_ctx: Any,
        correlation_id: str | None,
    ) -> dict:
        """
        Dispatch to a local in-process agent instance.
        Direct Python method call — zero network overhead.
        The called agent's handle_a2a() receives standard args.
        """
        handler = entry["handler"]

        self.log(
            event_type="SG.RouteA2A.Local",
            message=f"Dispatching locally to '{target_id}' / {capability_id}",
            payload={
                "targetAgentId": target_id,
                "capability":    capability_id,
                "correlationId": correlation_id,
            },
        )

        try:
            result = await handler.handle_a2a(
                capability_id=capability_id,
                payload=payload,
                agent_ctx=agent_ctx,
                capability_ctx=capability_ctx,
            )
            return self._success_envelope(correlation_id, capability_id, result)

        except NotImplementedError:
            return self._error_envelope(
                correlation_id,
                code=-32601,
                message=f"Capability '{capability_id}' not implemented on '{target_id}'",
            )
        except Exception as exc:
            logger.error(
                "SG.route_a2a: local dispatch to '%s' / '%s' failed — %s",
                target_id, capability_id, exc
            )
            return self._error_envelope(
                correlation_id,
                code=-32603,
                message=f"Local dispatch error: {exc}",
            )

    async def _dispatch_lambda(
        self,
        entry: dict,
        target_id: str,
        envelope: dict,
        correlation_id: str | None,
    ) -> dict:
        """
        Dispatch to a Lambda-backed agent via boto3.
        Isolated resources, independent scaling.
        The Lambda receives the full A2A envelope — its handler processes
        it exactly as it would an API Gateway invocation.
        """
        function_name = entry["function_name"]

        self.log(
            event_type="SG.RouteA2A.Lambda",
            message=f"Dispatching to Lambda '{function_name}' for '{target_id}'",
            payload={
                "targetAgentId": target_id,
                "functionName":  function_name,
                "correlationId": correlation_id,
            },
        )

        try:
            import boto3
            client   = boto3.client("lambda")
            response = client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(envelope).encode("utf-8"),
            )

            raw = response["Payload"].read()
            result = json.loads(raw)

            # Lambda handlers return {"statusCode": 200, "body": "..."}
            # Unwrap the body if present
            if "body" in result:
                body = result["body"]
                if isinstance(body, str):
                    body = json.loads(body)
                return body

            return result

        except Exception as exc:
            logger.error(
                "SG.route_a2a: Lambda dispatch to '%s' / '%s' failed — %s",
                target_id, function_name, exc
            )
            return self._error_envelope(
                correlation_id,
                code=-32603,
                message=f"Lambda dispatch error: {exc}",
            )

    # ------------------------------------------------------------------
    # handle_a2a — called by route_a2a() for local dispatch
    # This is what every local agent instance must expose.
    # Base implementation routes to the agent's own capability methods.
    # ------------------------------------------------------------------

    async def handle_a2a(
        self,
        capability_id: str,
        payload: dict,
        agent_ctx: Any,
        capability_ctx: Any,
    ) -> dict:
        """
        Entry point for local Mode 2 dispatch into this agent.

        SG's own capabilities are dispatched here.
        Other PlatformAgents inherit this and override their capability dispatch.

        Base implementation raises NotImplementedError for unknown capabilities
        so SG._dispatch_local() can return a clean error envelope.
        """
        dispatch = {
            "Just-Ask":                   self.just_ask,
            "Event.Log":                  self.event_log,
            "Request-Response.Correlate": self.request_response_correlate,
        }

        handler = dispatch.get(capability_id)
        if handler is None:
            raise NotImplementedError(
                f"Capability '{capability_id}' not found on SolicitorGeneralAgent."
            )

        return await handler(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Envelope builders
    # ------------------------------------------------------------------

    def _success_envelope(
        self,
        correlation_id: str | None,
        capability_id: str,
        result: dict,
    ) -> dict:
        """Wrap a successful result in an A2A-compliant response envelope."""
        from datetime import datetime, timezone
        return {
            "jsonrpc": "2.0",
            "id":      correlation_id,
            "result":  result,
            "metadata": {
                "capability": capability_id,
                "taskId":     correlation_id,
                "timestamp":  datetime.now(timezone.utc).isoformat(),
            },
        }

    def _error_envelope(
        self,
        correlation_id: str | None,
        code: int,
        message: str,
    ) -> dict:
        """Wrap an error in an A2A-compliant JSON-RPC error envelope."""
        return {
            "jsonrpc": "2.0",
            "id":      correlation_id,
            "error":   {"code": code, "message": message},
        }

    # ------------------------------------------------------------------
    # Capability extraction
    # ------------------------------------------------------------------

    def _extract_capability(self, envelope: dict) -> tuple[str, dict]:
        """
        Extract capability_id and payload from an inbound envelope.
        Scalar payloads normalized to {"input": value}.
        """
        capability_id = (
            envelope.get("capability")
            or envelope.get("method", "").replace("a2a.", "")
            or "unknown"
        )

        raw_payload = envelope.get("payload") or envelope.get("params") or {}

        if not isinstance(raw_payload, dict):
            payload = {"input": raw_payload}
        else:
            payload = raw_payload

        return capability_id, payload

    # ------------------------------------------------------------------
    # Context builders
    # ------------------------------------------------------------------

    def _build_agent_context(self, params: dict, mode: str = "api"):
        """
        Build AgentContext. Caller-supplied governance_labels stripped.
        mode= flows to AgentContext.startup_mode.
        """
        return self.context_class()(
            caller=params.get("caller"),
            subject_ref=params.get("subjectRef"),
            profile=None,
            correlation_id=params.get("correlationId"),
            task_id=params.get("taskId"),
            governance_labels=[],
            startup_mode=mode,
        )

    def _build_capability_context(self, capability_id: str, params: dict):
        """
        Build CapabilityContext. Merges caller_ctx > map_ctx > defaults.
        """
        map_entry = self.capability_map.get(capability_id, {})
        return self.capability_context_class()(
            capability_id=capability_id,
            dry_run=params.get("dryRun", map_entry.get("dryRun", False)),
            trace=params.get("trace", map_entry.get("trace", False)),
            task_id=params.get("taskId"),
            startup_mode=params.get("startupMode", "api"),
        )

    # ------------------------------------------------------------------
    # SG own capabilities
    # 🔲 Self-routing deferred (Gap Registry Priority 1)
    # ------------------------------------------------------------------

    async def just_ask(self, payload, agent_ctx, capability_ctx):
        """Capability: Just-Ask. 🔲 Self-routing not yet implemented."""
        from .just_ask import run
        return await run(payload, agent_ctx, capability_ctx)

    async def event_log(self, payload, agent_ctx, capability_ctx):
        """Capability: Event.Log. 🔲 Self-routing not yet implemented."""
        from .event_log import run
        return await run(payload, agent_ctx, capability_ctx)

    async def request_response_correlate(self, payload, agent_ctx, capability_ctx):
        """Capability: Request-Response.Correlate. 🔲 Self-routing not yet implemented."""
        from .request_response_correlate import run
        return await run(payload, agent_ctx, capability_ctx)

    async def resume_processing(self, payload, agent_ctx, capability_ctx):
        """Capability: resumeProcessing. 🔲 Deferred — storage location TBD."""
        raise NotImplementedError(
            "resumeProcessing() deferred — storage location TBD. "
            "Gap Registry: SG resumeProcessing (🔲 Deferred)."
        )

    # ------------------------------------------------------------------
    # CM-6: SG reacts to configuration changes
    # ------------------------------------------------------------------

    async def on_platform_configuration_change(self, event: dict) -> None:
        await super().on_platform_configuration_change(event)
        if event.get("type") in ("capability_map_updated", "route_table_updated"):
            self.log(
                event_type="SG.CapabilityMapReload",
                message="[CM-6] Capability map reload triggered by config change.",
                payload=event,
            )
            # 🔲 Runtime capability_map reload not yet implemented
