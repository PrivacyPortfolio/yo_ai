# agents/vendor_manager/runtime/vendor_manager.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("vendor_manager")

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
    # Capability: Org-Profile.Manage
    # ------------------------------------------------------------------
    async def org_profile_manage(self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.vendor_manager.capabilities.org_profile_manage import run
        return await run(payload, ctx)
