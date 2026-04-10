# /core/routing/unified_capability_router.py

from core.error_handler import ErrorHandler


class UnifiedCapabilityRouter:
    """
    Semantic router for A2A messages.
    Owned by the Solicitor-General and called as its internal tool.

    Responsibilities:
      - Validate the message container shape
      - (Hook) Validate payload schema
      - Invoke the resolved capability handler with three arguments:
          handler(payload, agent_context, capability_ctx)
      - Normalize handler exceptions into JSON-RPC error envelopes

    Handler signature contract (all capability methods and run() modules):
      async def <handler>(self, payload: dict,
                          agent_context: AgentContext | None,
                          capability_ctx: CapabilityContext | None) -> dict

    Context resolution inside run():
      Use capability_ctx.resolve(field, agent_context) to get the
      correct value regardless of which context provided it.
      CapabilityContext > AgentContext > default.

    What the UCR does NOT do:
      - Resolve agents — the SG resolves agent_instance before calling route()
      - Re-extract capability names — the SG resolves handler_name
      - Construct either context — the SG constructs both
      - Touch the envelope beyond confirming message shape
    """

    def __init__(self, logger):
        self._logger = logger

    async def route(
        self,
        *,
        envelope: dict,
        request_id: str,
        agent_context,              # AgentContext — platform governance
        capability_context,         # CapabilityContext — execution configuration
        capability_name: str,
        handler_name: str,
        agent_instance,
        payload: dict,
    ) -> dict:
        """
        Invoke a resolved capability handler on a resolved agent instance.

        All arguments are pre-resolved by the Solicitor-General.
        The UCR is a pure dispatcher — it does not re-derive any values.

        Args:
          envelope:            Original A2A envelope (shape validation only)
          request_id:          Correlation ID from the transport layer
          agent_context:       AgentContext from SG — platform governance layer
          capability_context:  CapabilityContext from SG — execution config layer
          capability_name:     Canonical A2A capability name
          handler_name:        Python method name on the agent
          agent_instance:      Live agent instance constructed by the SG
          payload:             Extracted capability payload
        """

        # 1. Confirm message container shape
        params = envelope.get("params", {})
        message_container = params.get("message", {})

        if not isinstance(message_container, dict) or len(message_container) != 1:
            return ErrorHandler.from_known_error(
                code=-32600,
                message="Invalid A2A message: expected exactly one messageType",
                request_id=request_id,
                extra={
                    "source": "UnifiedCapabilityRouter.route",
                    "capability": capability_name,
                },
            )

        # 2. Schema validation hook (no-op until schema enforcement is ready)
        self._validate_message(capability_name, payload)

        # 3. Resolve handler on agent instance
        handler = getattr(agent_instance, handler_name, None)

        if handler is None or not callable(handler):
            return ErrorHandler.from_known_error(
                code=-32601,
                message=f"Agent does not implement handler '{handler_name}'",
                request_id=request_id,
                extra={
                    "source": "UnifiedCapabilityRouter.route",
                    "capability": capability_name,
                    "handler": handler_name,
                    "agent": agent_instance.actor_name,
                },
            )

        # 4. Execute capability handler with both contexts
        #    agent_context:      SG's authoritative governance context
        #    capability_context: SG's execution configuration context
        #    Handlers resolve fields via capability_context.resolve(field, agent_context)
        try:
            result = await handler(payload, agent_context, capability_context)
        except Exception as exc:
            self._logger.write({
                "actor": "UnifiedCapabilityRouter",
                "event_type": "router.handler_error",
                "message": f"Handler '{handler_name}' raised an exception",
                "payload": {
                    "request_id": request_id,
                    "capability": capability_name,
                    "handler": handler_name,
                    "agent": agent_instance.actor_name,
                    "error": str(exc),
                },
            })
            return ErrorHandler.normalize_exception(
                exc,
                request_id=request_id,
                agent_name=agent_instance.actor_name,
                capability=capability_name,
                context={"source": "UnifiedCapabilityRouter.route"},
            )

        return result

    # ------------------------------------------------------------------
    # Schema validation hook
    # ------------------------------------------------------------------
    def _validate_message(self, capability_name: str, payload: dict) -> None:
        """
        Schema validation hook — no-op until schema enforcement is ready.
        capability_name maps to input_schema in capability_map.yaml.
        """
        return
