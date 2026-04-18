# agents/solicitor_general/capabilities/just_ask.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("solicitor_general")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Just-Ask ───────────────────────────────────────────────
    # Default conversational entrypoint for the platform.
    # Handles general questions, routing guidance, onboarding, and any
    # natural language request that doesn't map to a specific capability.
    # Natural call_ai() candidate — benefits more from LLM reasoning than
    # any other SG capability.

    question   = payload.get("question", "")
    context_in = payload.get("context", {})

    # ── Entry 1: capability received ───────────────────────────────────────
    LOG.write(
        event_type="just-ask.Request",
        payload={
            "question": question,
            "context":  context_in,
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    result = {
        "message":          "This is the Solicitor-General responding via Just-Ask.",
        "questionReceived": question,
        "caller":           ctx.get("caller"),
        "subjectRef":       ctx.get("subject_ref"),
        "governanceLabels": ctx.get("governance_labels"),
        "correlationId":    ctx.get("correlation_id"),
        "taskId":           ctx.get("task_id"),
        "dryRun":           ctx.get("dry_run"),
        "status":           "stub",
    }

    return result
