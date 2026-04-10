# agents/data_anonymizer/runtime/data_anonymizer.py

from core.yoai_agent import YoAiAgent
from core.observability.logging.platform_logger import get_platform_logger
LOG = get_platform_logger("data_anonymizer")

class DataAnonymizer(YoAiAgent):
    """
    Data-Anonymizer: uses a variety of tools and techniques for anonymizing
    and testing datasets of personal attributes.

    This agent is profile-aware: anonymization decisions may depend on
    subject profile, caller identity, or governance labels.
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
    async def identifiability_assess(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .identifiability_assess import run
        return await run(payload, agent_ctx, capability_ctx)

    async def deidentification_techniques_apply(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .deidentification_techniques_apply import run
        return await run(payload, agent_ctx, capability_ctx)

    async def k_anonymity_compute(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .k_anonymity_compute import run
        return await run(payload, agent_ctx, capability_ctx)


    async def safe_release_recommend(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .safe_release_recommend import run
        return await run(payload, agent_ctx, capability_ctx)
    

    async def deidentification_report_generate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .deidentification_report_generate import run
        return await run(payload, agent_ctx, capability_ctx)


    async def auxiliary_data_risk_evaluate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .auxiliary_data_risk_evaluate import run
        return await run(payload, agent_ctx, capability_ctx)


    async def data_for_purpose_minimize(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .data_for_purpose_minimize import run
        return await run(payload, agent_ctx, capability_ctx)
    

    async def reidentification_attack_simulate(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .reidentification_attack_simulate import run
        return await run(payload, agent_ctx, capability_ctx)


    async def deidentification_standard_map(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .deidentification_standard_map import run
        return await run(payload, agent_ctx, capability_ctx)


    async def deidentification_guidance_publish(
        self, payload: dict, agent_ctx, capability_ctx: CapabilityContext | None
    ) -> dict:
        from .deidentification_guidance_publish import run
        return await run(payload, agent_ctx, capability_ctx)
