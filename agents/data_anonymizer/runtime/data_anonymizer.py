# agents/data_anonymizer/runtime/data_anonymizer.py

from core.yoai_agent import YoAiAgent
from core.yoai_context import YoAiContext
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
    async def identifiability_assess(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.identifiability_assess import run
        return await run(payload, ctx)

    async def deidentification_techniques_apply(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.deidentification_techniques_apply import run
        return await run(payload, ctx)

    async def k_anonymity_compute(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.k_anonymity_compute import run
        return await run(payload, ctx)


    async def safe_release_recommend(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.safe_release_recommend import run
        return await run(payload, ctx)
    

    async def deidentification_report_generate(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.deidentification_report_generate import run
        return await run(payload, ctx)


    async def auxiliary_data_risk_evaluate(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.auxiliary_data_risk_evaluate import run
        return await run(payload, ctx)


    async def data_for_purpose_minimize(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.data_for_purpose_minimize import run
        return await run(payload, ctx)
    

    async def reidentification_attack_simulate(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.reidentification_attack_simulate import run
        return await run(payload, ctx)


    async def deidentification_standard_map(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.deidentification_standard_map import run
        return await run(payload, ctx)


    async def deidentification_guidance_publish(
        self, payload: dict, ctx: YoAiContext) -> dict:
        from agents.data_anonymizer.capabilities.deidentification_guidance_publish import run
        return await run(payload, ctx)
