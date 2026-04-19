# agents/complaint_manager/complaint_manager.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("complaint_manager")


class ComplaintManagerAgent(YoAiAgent):
    # ── Complaint-Manager ──────────────────────────────────────────────────
    # Represents a person or org in the complaints process.
    # Loads skills, tools, schemas, fingerprints, and knowledge from YoAiAgent.

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        profile: dict | None = None,
        slim: bool = False,
    ):
        # ── No ctx param — YoAiAgent no longer accepts one ─────────────────
        # profile is passed explicitly; YoAiAgent normalizes it.
        # agent_id and name come from the card via BaseAgent — not overridden.
        super().__init__(
            card=card,
            extended_card=extended_card,
            profile=profile,
            slim=slim,
        )

    # ── Capability: Liability.Discover ────────────────────────────────────

    async def liability_discover(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.liability_discover import run
        return await run(payload, ctx)

    # ── Capability: EnforcementAgency.Get ─────────────────────────────────

    async def enforcementagency_get(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.enforcementagency_get import run
        return await run(payload, ctx)

    # ── Capability: Stakeholders.Get ──────────────────────────────────────

    async def stakeholders_get(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.stakeholders_get import run
        return await run(payload, ctx)

    # ── Capability: Complaint.Generate ────────────────────────────────────

    async def complaint_generate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.complaint_generate import run
        return await run(payload, ctx)

    # ── Capability: Complaint.Submit ──────────────────────────────────────

    async def complaint_submit(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.complaint_submit import run
        return await run(payload, ctx)

    # ── Capability: Complaint.Publish ─────────────────────────────────────

    async def complaint_publish(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.complaint_publish import run
        return await run(payload, ctx)

    # ── Capability: Stakeholder.Notify ────────────────────────────────────

    async def stakeholder_notify(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.complaint_manager.capabilities.stakeholder_notify import run
        return await run(payload, ctx)
