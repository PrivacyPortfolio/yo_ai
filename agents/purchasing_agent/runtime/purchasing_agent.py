# agents/purchasing_agent/runtime/purchasing_agent.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("purchasing_agent")


class PurchasingAgent(YoAiAgent):
    """
    Purchasing-Agent: thin orchestration layer.
    Each capability method delegates to a capability-handler module.

    Profile-aware: represents one named person per instance.
    Instance identity: "Purchasing-Agent.BillyJo", "Purchasing-Agent.BillyJo-Work", etc.

    Developer contract — see YoAiAgent docstring for full details.
    Key convenience properties available in every run() module:
      self.profile        — subject profile (the buyer represented)
      self.instance_id    — "Purchasing-Agent.<profile.name>"
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
        profile=None,
        slim: bool | None = None,
    ):
        super().__init__(
            card=card,
            extended_card=extended_card,
            profile=profile,
            slim=slim,
        )

    # ------------------------------------------------------------------
    # Capability: Purchase-Options.Recommend
    # ------------------------------------------------------------------
    async def purchase_options_recommend(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_options_recommend import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Purchase-Risk.Evaluate
    # ------------------------------------------------------------------
    async def purchase_risk_evaluate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_risk_evaluate import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Purchase-History.Generate
    # ------------------------------------------------------------------
    async def purchase_history_generate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_history_generate import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Purchase-Receipt.Generate
    # ------------------------------------------------------------------
    async def purchase_receipt_generate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_receipt_generate import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Purchase-Issues.Resolve
    # ------------------------------------------------------------------
    async def purchase_issues_resolve(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_issues_resolve import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Return-Or-Refund.Initiate
    # ------------------------------------------------------------------
    async def return_or_refund_initiate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.return_or_refund_initiate import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Order-Status.Track
    # ------------------------------------------------------------------
    async def order_status_track(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.order_status_track import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Budget-After-Purchase.Update
    # ------------------------------------------------------------------
    async def budget_after_purchase_update(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.budget_after_purchase_update import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Transaction-Complete.Verify
    # ------------------------------------------------------------------
    async def transaction_complete_verify(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.transaction_complete_verify import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Purchase.Initiate
    # ------------------------------------------------------------------
    async def purchase_initiate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_initiate import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Purchase-Eligibility.Validate
    # ------------------------------------------------------------------
    async def purchase_eligibility_validate(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.purchase_eligibility_validate import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Budget.Check
    # ------------------------------------------------------------------
    async def budget_check(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.budget_check import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Payment.Cancel
    # ------------------------------------------------------------------
    async def payment_cancel(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.payment_cancel import run
        return await run(payload, ctx)

    # ------------------------------------------------------------------
    # Capability: Mandate.Manage
    # ------------------------------------------------------------------
    async def mandate_manage(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.purchasing_agent.capabilities.mandate_manage import run
        return await run(payload, ctx)
