# agents/decision_master/runtime/decision_master.py

from core.platform_agent import PlatformAgent
from core.runtime.platform_event_bus import PlatformEventBus
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("decision_master")


class DecisionMasterAgent(PlatformAgent):
    # ── Decision-Master ────────────────────────────────────────────────────
    # Identifies and analyzes decision-making events, manages decision
    # diaries, and publishes decision outcomes.
    #
    # Profile-aware: decision analysis may depend on subject profile,
    # caller identity, or governance labels — all carried in YoAiContext.
    #
    # AgentCard tags (decision-event, decision-factor, decision-outcome)
    # are hints identifying which platform events carry decision-relevant
    # signals.

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

    # ── Capability: Decision-Diary.Manage ──────────────────────────────────

    async def decision_diary_manage(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.decision_master.capabilities.decision_diary_manage import run
        return await run(payload, ctx)

    # ── Capability: Decision-Events.Identify ───────────────────────────────

    async def decision_events_identify(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.decision_master.capabilities.decision_events_identify import run
        return await run(payload, ctx)

    # ── Capability: Decision-Outcome.Identify ──────────────────────────────

    async def decision_outcome_identify(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.decision_master.capabilities.decision_outcome_identify import run
        return await run(payload, ctx)

    # ── Capability: Decision-Outcome.Analyze ───────────────────────────────

    async def decision_outcome_analyze(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.decision_master.capabilities.decision_outcome_analyze import run
        return await run(payload, ctx)
