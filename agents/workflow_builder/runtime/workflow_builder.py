# agents/workflow_builder/workflow_builder.py

from core.platform_agent import PlatformAgent


class WorkflowBuilderAgent(PlatformAgent):
    """
    Workflow-Builder: constructs and manages complex multi-step workflows
    across platform agents.

    Note: Workflow-Builder message/data flows are deferred pending
    capability handler walkthrough (Gap Registry 🔲 — extends basic
    A2A task management).
    """

    def __init__(self, *, card=None, extended_card=None, slim=False):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
        )

    # ------------------------------------------------------------------
    # Capability: Workflow.Build
    # ------------------------------------------------------------------
    async def workflow_build(self, payload, agent_ctx, capability_ctx):
        from .workflow_build import run
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
