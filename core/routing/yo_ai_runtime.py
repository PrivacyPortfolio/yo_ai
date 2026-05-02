# core/routing/yo_ai_runtime.py
#
# Yo-ai Platform runtime — semantic routing spine.
#
# Contract:
#   Receive a validated JSON-RPC envelope. Extract the capability_id.
#   Look up the owning agent in capability_map. Dispatch to that agent's
#   Lambda function via the injected RPC adapter. Return the semantic result.
#   Never import agent code. Never raise — all failures return structured
#   JSON-RPC error envelopes.
#
# Dispatch model:
#   handlerType: "internal"  →  Lambda invoke (boto3)
#   handlerType: "external"  →  HTTP call
#
# RPC adapters are injected at construction via the `tools` dict so the
# runtime is testable without AWS credentials. The platform bootstrap
# injects the real boto3-backed adapter at cold start.
#
# Capability map shape (from shared/registries/capability_map.yaml):
#   capabilities:
#     Trust.Assign:
#       agent:        door-keeper
#       handler:      yo-ai-door-keeper     <- Lambda function name
#       handlerType:  internal
#       inputSchema:  trust.assign.input.schema.json
#       outputSchema: trust.assign.output.schema.json
#       dryRun:       false
#       trace:        false
#
# Adding a new agent requires only a new capability_map entry — no code change.

from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, Dict, Optional

from core.runtime.envelope import extract
from core.yoai_context import YoAiContext, ctx_from_envelope, ctx_for_capability
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("yo_ai_runtime")

# RPC adapter types — injected via tools dict, never imported directly.
# This keeps YoAiRuntime testable without AWS credentials.
LambdaInvokeFn = Callable[[str, bytes], Awaitable[bytes]]
HttpCallFn     = Callable[[str, dict],  Awaitable[dict]]


class YoAiRuntime:
    # -- Semantic routing spine -------------------------------------------
    # One instance per Lambda execution environment (cold start).
    # Shared across all warm invocations via platform_bootstrap.

    def __init__(
        self,
        *,
        capability_map: Dict[str, Any],
        tools: Dict[str, Any],
    ) -> None:
        # capability_map: loaded from shared/registries/capability_map.yaml
        # tools keys consumed here:
        #   "lambda_invoke"  async fn(function_name: str, payload: bytes) -> bytes
        #   "http_call"      async fn(url: str, payload: dict) -> dict
        #   "platform_log"   async fn(event: dict) -> None
        self.capability_map = capability_map
        self.tools          = tools
        self._capabilities  = capability_map.get("capabilities", {})

        # Correlation-scoped state (per request, not per agent)
        self._instance_cache: Dict[str, Any] = {}
        self._task_state:     Dict[str, Any] = {}

    # -- Core entrypoint --------------------------------------------------

    async def route(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        # -- 1. Extract capability_id from envelope -----------------------
        # core.envelope.extract() handles all envelope shapes:
        # A2A (method="a2a.<cap>"), direct (capability="<cap>"), params block.
        capability_id, payload = extract(envelope)

        if not capability_id or capability_id == "unknown":
            return self._error(
                envelope.get("id"),
                -32601,
                "Could not extract capability_id from envelope",
                {"envelope_keys": list(envelope.keys())},
            )

        # -- 2. Capability map lookup -------------------------------------
        entry = self._capabilities.get(capability_id)
        if entry is None:
            LOG.write(
                event_type="runtime.CapabilityNotFound",
                payload={"capability_id": capability_id},
                context=None,
            )
            return self._error(
                envelope.get("id"),
                -32601,
                f"Capability not registered: '{capability_id}'",
                {"capability_id": capability_id},
            )

        function_name = entry.get("handler", "")
        handler_type  = entry.get("handlerType", "internal")

        if not function_name:
            return self._error(
                envelope.get("id"),
                -32603,
                f"No handler configured for capability '{capability_id}'",
                {"entry": entry},
            )

        # -- 3. Build capability-level YoAiContext and stamp into envelope -
        # The receiving agent's lambda_handler calls ctx_from_envelope() and
        # finds capability_id, correlation_id, startup_mode already present.
        # We stamp the enriched ctx here so it travels with the payload.
        raw_ctx = envelope.get("ctx", {}) or {}
        pipeline_ctx: YoAiContext = ctx_from_envelope(
            envelope,
            instance_id=None,   # runtime has no agent identity of its own
            correlation_id=raw_ctx.get("correlation_id"),
            task_id=raw_ctx.get("task_id"),
            profile=raw_ctx.get("profile"),
        )
        capability_ctx: YoAiContext = ctx_for_capability(pipeline_ctx, capability_id)

        # Outbound envelope carries the enriched ctx so the receiving Lambda
        # can reconstruct the full YoAiContext without re-deriving capability_id.
        outbound = {**envelope, "ctx": dict(capability_ctx)}

        LOG.write(
            event_type="runtime.Dispatch",
            payload={
                "capability_id":  capability_id,
                "agent":          entry.get("agent"),
                "function_name":  function_name,
                "handler_type":   handler_type,
                "correlation_id": capability_ctx.get("correlation_id"),
            },
            context=capability_ctx,
        )

        # -- 4. Dispatch via RPC adapter ----------------------------------
        if handler_type == "internal":
            return await self._invoke_lambda(
                function_name=function_name,
                envelope=outbound,
                request_id=envelope.get("id"),
            )

        if handler_type == "external":
            return await self._invoke_http(
                function_name=function_name,
                envelope=outbound,
                request_id=envelope.get("id"),
            )

        return self._error(
            envelope.get("id"),
            -32603,
            f"Unknown handlerType '{handler_type}' for '{capability_id}'",
            {"entry": entry},
        )

    # -- route_a2a (backward-compatible convenience method) ---------------

    async def route_a2a(
        self,
        envelope: Dict[str, Any],
        ctx: Optional[YoAiContext] = None,
    ) -> Dict[str, Any]:
        # ctx accepted for backward compatibility with existing SG call sites
        # but not used — route() rebuilds it from the envelope to ensure
        # capability_id is bound correctly.
        return await self.route(envelope)

    # -- Lambda RPC adapter -----------------------------------------------

    async def _invoke_lambda(
        self,
        function_name: str,
        envelope: dict,
        request_id: Any,
    ) -> dict:
        invoke_fn: LambdaInvokeFn | None = self.tools.get("lambda_invoke")

        if invoke_fn is None:
            return self._error(
                request_id,
                -32603,
                "lambda_invoke adapter not configured in YoAiRuntime.tools",
                {"function_name": function_name},
            )

        try:
            payload_bytes  = json.dumps(envelope).encode("utf-8")
            response_bytes = await invoke_fn(function_name, payload_bytes)
        except Exception as exc:
            LOG.write(
                event_type="runtime.LambdaInvokeError",
                payload={"function_name": function_name, "error": str(exc)},
                context=None,
            )
            return self._error(
                request_id,
                -32603,
                f"Lambda invoke failed for '{function_name}': {exc}",
                {"error": str(exc)},
            )

        # Parse response bytes
        try:
            response_dict = json.loads(response_bytes)
        except (json.JSONDecodeError, TypeError) as exc:
            LOG.write(
                event_type="runtime.LambdaResponseParseError",
                payload={"function_name": function_name, "error": str(exc)},
                context=None,
            )
            return self._error(
                request_id,
                -32603,
                f"Lambda '{function_name}' returned non-JSON response",
                {"error": str(exc)},
            )

        # Agent Lambdas return API Gateway proxy responses:
        # { "statusCode": 200, "body": "{...json...}" }
        # Unwrap body — callers of route() expect a semantic result dict,
        # not a proxy response wrapper.
        if "body" in response_dict and "statusCode" in response_dict:
            body = response_dict["body"]
            try:
                return json.loads(body) if isinstance(body, str) else body
            except (json.JSONDecodeError, TypeError):
                return response_dict

        # Direct dict response (e.g. from a test stub or non-proxy Lambda)
        return response_dict

    # -- HTTP RPC adapter (external handlerType) --------------------------

    async def _invoke_http(
        self,
        function_name: str,
        envelope: dict,
        request_id: Any,
    ) -> dict:
        # function_name is the URL for external handlers
        http_fn: HttpCallFn | None = self.tools.get("http_call")

        if http_fn is None:
            return self._error(
                request_id,
                -32603,
                "http_call adapter not configured in YoAiRuntime.tools",
                {"url": function_name},
            )

        try:
            return await http_fn(function_name, envelope)
        except Exception as exc:
            LOG.write(
                event_type="runtime.HttpCallError",
                payload={"url": function_name, "error": str(exc)},
                context=None,
            )
            return self._error(
                request_id,
                -32603,
                f"HTTP call failed for '{function_name}': {exc}",
                {"error": str(exc)},
            )

    # -- Task + correlation state ------------------------------------------

    def get_or_create_instance(self, correlation_id: str) -> dict:
        return self._instance_cache.setdefault(correlation_id, {})

    def update_task_state(self, task_id: str, state: Dict[str, Any]) -> None:
        self._task_state[task_id] = state

    # -- Platform logging --------------------------------------------------

    async def log_event(self, event: Dict[str, Any]) -> None:
        log_fn = self.tools.get("platform_log")
        if log_fn:
            await log_fn(event)

    # -- Error envelope builder -------------------------------------------

    @staticmethod
    def _error(
        request_id: Any,
        code: int,
        message: str,
        data: dict | None = None,
    ) -> dict:
        return {
            "jsonrpc": "2.0",
            "id":      request_id,
            "error": {
                "code":    code,
                "message": message,
                "data":    data or {},
            },
        }
