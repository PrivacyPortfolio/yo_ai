# core/routing/unified_capability_router.py
#
# Semantic router for A2A messages.
# Owned by the Solicitor-General and called as its internal tool.
#
# Responsibilities:
#   - Validate the message container shape
#   - (Hook) Validate payload schema
#   - Invoke the resolved capability handler
#   - Normalize handler exceptions into JSON-RPC error envelopes
#
# Handler signature contract (all capability methods and run() modules):
#   async def <handler>(self, payload: dict, ctx: YoAiContext) -> dict
#
# ctx is a single YoAiContext dict — built once by the SG via _build_context()
# and passed through unchanged. Handlers access all fields via ctx.get("field").
#
# What the UCR does NOT do:
#   - Resolve agents — the SG resolves agent_instance before calling route()
#   - Re-extract capability names — the SG resolves handler_name
#   - Construct context — the SG constructs it via _build_context()
#   - Touch the envelope beyond confirming message shape

from core.error_handler import ErrorHandler
from core.yoai_context import YoAiContext


class UnifiedCapabilityRouter:

    def __init__(self, logger):
        self._logger = logger

    async def route(
        self,
        *,
        envelope: dict,
        request_id: str,
        ctx: YoAiContext,
        capability_name: str,
        handler_name: str,
        agent_instance,
        payload: dict,
    ) -> dict:
        # ── All arguments pre-resolved by the SG ──────────────────────────
        # The UCR is a pure dispatcher — it does not re-derive any values.

        # ── 1. Confirm message container shape ────────────────────────────
        params            = envelope.get("params", {})
        message_container = params.get("message", {})

        if not isinstance(message_container, dict) or len(message_container) != 1:
            return ErrorHandler.from_known_error(
                code=-32600,
                message="Invalid A2A message: expected exactly one messageType",
                request_id=request_id,
                extra={
                    "source":     "UnifiedCapabilityRouter.route",
                    "capability": capability_name,
                },
            )

        # ── 2. Schema validation hook (no-op until enforcement is ready) ───
        self._validate_message(capability_name, payload)

        # ── 3. Resolve handler on agent instance ──────────────────────────
        handler = getattr(agent_instance, handler_name, None)

        if handler is None or not callable(handler):
            return ErrorHandler.from_known_error(
                code=-32601,
                message=f"Agent does not implement handler '{handler_name}'",
                request_id=request_id,
                extra={
                    "source":     "UnifiedCapabilityRouter.route",
                    "capability": capability_name,
                    "handler":    handler_name,
                    "agent":      agent_instance.name,   # BaseAgent.name — not actor_name
                },
            )

        # ── 4. Execute — single YoAiContext dict passed to handler ─────────
        try:
            result = await handler(payload, ctx)
        except Exception as exc:
            self._logger.write({
                "actor":      "UnifiedCapabilityRouter",
                "event_type": "router.handler_error",
                "payload": {
                    "request_id": request_id,
                    "capability": capability_name,
                    "handler":    handler_name,
                    "agent":      agent_instance.name,
                    "error":      str(exc),
                },
            })
            return ErrorHandler.normalize_exception(
                exc,
                request_id=request_id,
                agent_name=agent_instance.name,
                capability=capability_name,
                context={"source": "UnifiedCapabilityRouter.route"},
            )

        return result

    # ── Schema validation hook ─────────────────────────────────────────────

    def _validate_message(self, capability_name: str, payload: dict) -> None:
        # ── No-op until schema enforcement is ready ────────────────────────
        # capability_name maps to inputSchema in capability_map.yaml.
        # Use input_schema_name(ctx) from yoai_context.py to derive the
        # schema filename when enforcement is implemented.
        return
