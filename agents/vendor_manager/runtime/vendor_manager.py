# agents/vendor_manager/runtime/vendor_manager.py

from core.yoai_agent import YoAiAgent


class VendorManagerAgent(YoAiAgent):
    """
    Vendor-Manager: governs and maintains Org-Profiles for Responsible AI certification.

    Profile-aware: may represent a person or an organization.
    Instance identity: "Vendor-Manager.ABCCorp", "Vendor-Manager.ABCCorp-Legal", etc.

    Developer contract — see YoAiAgent docstring for full details.
    Key convenience properties available in every run() module:
      self.profile        — org or person profile (the entity represented)
      self.instance_id    — "Vendor-Manager.<profile.name>"
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
    # Capability: Org-Profile.Manage
    # ------------------------------------------------------------------
    async def org_profile_manage(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from agents.vendor_manager.capabilities.org_profile_manage import run
        return await run(payload, agent_ctx, capability_ctx)
