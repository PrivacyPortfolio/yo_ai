# agents/workflow_builder/workflow_builder.py
#
# Workflow-Builder: constructs and manages complex multi-step workflows
# across platform agents.
#

from core.platform_agent import PlatformAgent
from core.runtime.platform_event_bus import PlatformEventBus
from core.yoai_context import YoAiContext


class WorkflowBuilderAgent(PlatformAgent):

    def __init__(
        self,
        *,
        card=None,
        extended_card=None,
        slim=False,
        event_bus: PlatformEventBus,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            slim=slim,
            event_bus=event_bus,
        )

    # ── Capability: Workflow.Build ─────────────────────────────────────────

    async def workflow_build(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.workflow_builder.capabilities.workflow_build import run
        return await run(payload, ctx)
