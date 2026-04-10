# agents/incident_responder/runtime/incident_responder.py

from core.platform_agent import PlatformAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("incident_responder")


class IncidentResponderAgent(PlatformAgent):
    """
    Incident-Responder: universal exception handler for the platform.
    Handles uncaught exceptions, normalizes error envelopes, and
    produces structured incident responses.

    Note: this agent's handler has a special responsibility — it must
    never itself raise an unhandled exception. Its own error path must
    be maximally defensive.
    """

    def __init__(self, *, card=None, extended_card=None, slim=False):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
        )

    # ------------------------------------------------------------------
    # Capability: Handle.Exception
    # ------------------------------------------------------------------
    async def handle_exception(self, payload, agent_ctx, capability_ctx):
        from agents.incident_responder.capabilities.handle_exception import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Context builders
    # ------------------------------------------------------------------
    def _build_agent_context(self, params: dict):
        return self.context_class()(
            caller=params.get("caller"),
            subject_ref=params.get("subjectRef"),
            profile=self.profile,
            correlation_id=params.get("correlationId"),
            task_id=params.get("taskId"),
            governance_labels=[],
            startup_mode=params.get("startupMode", "api"),
        )

    def _build_capability_context(self, capability_id: str, params: dict):
        return self.capability_context_class()(
            capability_id=capability_id,
            dry_run=params.get("dryRun", False),
            trace=params.get("trace", False),
            task_id=params.get("taskId"),
            startup_mode=params.get("startupMode", "api"),
        )
