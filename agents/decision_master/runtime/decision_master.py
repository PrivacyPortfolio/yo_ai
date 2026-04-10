# agents/decision_master/runtime/decision_master.py

from core.platform_agent import PlatformAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("decision_master")


class DecisionMasterAgent(PlatformAgent):
    """
    Decision-Master: identifies and analyzes decision-making events,
    manages decision diaries, and publishes decision outcomes.

    This agent is profile-aware: decision analysis may depend on
    subject profile, caller identity, or governance labels.

    AgentCard tags on capabilities (decision-event, decision-factor,
    decision-outcome) are hints for this agent — they identify which
    platform events carry decision-relevant signals.
    """

    def __init__(self, *, card=None, extended_card=None, slim=False):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
        )

    # ------------------------------------------------------------------
    # Capability: Decision-Diary.Manage
    # ------------------------------------------------------------------
    async def decision_diary_manage(self, payload, agent_ctx, capability_ctx):
        from agents.decision_master.capabilities.decision_diary_manage import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Decision-Events.Identify
    # ------------------------------------------------------------------
    async def decision_events_identify(self, payload, agent_ctx, capability_ctx):
        from agents.decision_master.capabilities.decision_events_identify import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Decision-Outcome.Identify
    # ------------------------------------------------------------------
    async def decision_outcome_identify(self, payload, agent_ctx, capability_ctx):
        from agents.decision_master.capabilities.decision_outcome_identify import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Decision-Outcome.Analyze
    # ------------------------------------------------------------------
    async def decision_outcome_analyze(self, payload, agent_ctx, capability_ctx):
        from agents.decision_master.capabilities.decision_outcome_analyze import run
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
