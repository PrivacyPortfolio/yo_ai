# agents/data_steward/runtime/data_steward.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("data_steward")


class DataSteward(YoAiAgent):
    """
    Data-Steward: governs access to personal data, evaluates intended use,
    and acts on behalf of a specific person.

    Profile-aware: represents one named person per instance.
    Instance identity: "Data-Steward.BillyJo", "Data-Steward.BillyJo-Work", etc.

    Developer contract — see YoAiAgent docstring for full details.
    Key convenience properties available in every run() module:
      self.profile        — subject profile (the person represented)
      self.instance_id    — "Data-Steward.<profile.name>"
      self.correlation_id — request correlation handle
      self.task_id        — A2A task identifier
      self.knowledge      — loaded knowledge base (empty if slim=True)
      self.tools          — tool registry (None if slim=True)
    """

    def __init__(
        self,
        *,
        card: dict | None = None,
        extended_card: dict | None = None,
        capability_ctx: CapabilityContext | None = None,
        profile=None,
        slim: bool | None = None,
        context=None,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            capability_ctx=capability_ctx,
            profile=profile,
            slim=slim,
            context=context,
        )

    # ------------------------------------------------------------------
    # Capability: Phone.Call
    # ------------------------------------------------------------------
    async def phone_call(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.data_steward.capabilities.phone_call import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Phone.Answer
    # ------------------------------------------------------------------
    async def phone_answer(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.data_steward.capabilities.phone_answer import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Data-Request.Govern
    # ------------------------------------------------------------------
    async def data_request_govern(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.data_steward.capabilities.data_request_govern import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Email.Read
    # ------------------------------------------------------------------
    async def email_read(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.data_steward.capabilities.email_read import run
        return await run(payload, agent_ctx, capability_ctx)

    # ------------------------------------------------------------------
    # Capability: Email.Send
    # ------------------------------------------------------------------
    async def email_send(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.data_steward.capabilities.email_send import run
        return await run(payload, agent_ctx, capability_ctx)
