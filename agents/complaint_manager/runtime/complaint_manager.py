# agents/complaint_manager/complaint_manager.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("complaint_manager")

class ComplaintManagerAgent(YoAiAgent):
    """
    Complaint-Manager is a YoAiAgent representing a person or org rep.
    It loads skills/tools/schemas/fingerprints/knowledge from YoAiAgent.
    """

    def __init__(self, agent_id="complaint_manager", profile=None,
                 card=None, extended_card=None, context=None):

        super().__init__(card=card, extended_card=extended_card, context=context)

        self.agent_id = agent_id
        self.profile = profile  # profileRef or loaded profile

    # ------------------------------------------------------------------
    # Capability: Liability.Discover
    # ------------------------------------------------------------------
    async def liability_discover(self, envelope):
        from agents.complaint_manager.capabilities.liability_discover import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Capability: EnforcementAgency.Get
    # ------------------------------------------------------------------
    async def enforcementagency_get(self, envelope):
        from agents.complaint_manager.capabilities.enforcementagency_get import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Capability: Stakeholders.Get
    # ------------------------------------------------------------------
    async def stakeholders_get(self, envelope):
        from agents.complaint_manager.capabilities.stakeholders_get import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Capability: Complaint.Generate
    # ------------------------------------------------------------------
    async def complaint_generate(self, envelope):
        from agents.complaint_manager.capabilities.complaint_generate import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Capability: Complaint.Submit
    # ------------------------------------------------------------------
    async def complaint_submit(self, envelope):
        from agents.complaint_manager.capabilities.complaint_submit import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Capability: Complaint.Publish
    # ------------------------------------------------------------------
    async def complaint_publish(self, envelope):
        from agents.complaint_manager.capabilities.complaint_publish import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Capability: Stakeholder.Notify
    # ------------------------------------------------------------------
    async def stakeholder_notify(self, envelope):
        from agents.complaint_manager.capabilities.stakeholder_notify import run
        return await run(envelope, self._build_context(envelope))

    # ------------------------------------------------------------------
    # Context builder
    # ------------------------------------------------------------------
    def _build_context(self, envelope_dict):
        """
        Build AgentContext using:
          - caller
          - subject
          - profile (constructor or envelope)
          - profilePatch
          - governanceLabels
          - correlationId
        """
        return AgentContext(
            caller=envelope_dict.get("caller"),
            subject=envelope_dict.get("subject"),
            profile=self.profile or envelope_dict.get("profile"),
            profile_patch=envelope_dict.get("profilePatch"),
            governance_labels=envelope_dict.get("governanceLabels", []),
            correlation_id=envelope_dict.get("correlationId"),
        )