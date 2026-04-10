# agents/the_sentinel/the_sentinel.py

from core.platform_agent import PlatformAgent


class TheSentinelAgent(PlatformAgent):
    """
    The-Sentinel: listens for dangerous incidents, anomalies, and trends,
    and issues alerts or escalations.

    This agent is profile-aware: different roles (developer, security engineer,
    compliance officer) may care about different monitoring perspectives.

    The-Sentinel is a candidate for the Trust-Assessor pattern described in
    the Training Manual — consuming Kafka events continuously and proactively
    triggering alerts without being explicitly asked. The KafkaPublisher
    component (Gap Registry 🔲) is a prerequisite for that behavior.
    """

    def __init__(self, *, card=None, extended_card=None, slim=False):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
        )

    # ------------------------------------------------------------------
    # Capability: Platform.Monitor
    # ------------------------------------------------------------------
    async def platform_monitor(self, payload, agent_ctx, capability_ctx):
        from .platform_monitor import run
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
