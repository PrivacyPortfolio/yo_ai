# agents/solicitor_general/capabilities/just_ask.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Just-Ask
    Default conversational entrypoint for the platform.

    Handles:
      - General questions about platform capabilities
      - Routing users to the right agent
      - Onboarding guidance
      - Any natural language request that doesn't map to a specific capability

    Implementation note:
      This stub returns a placeholder response. Just-Ask is a natural
      call_ai() candidate — it benefits more from LLM reasoning than
      any other SG capability. 

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    question    = payload.get("question", "")
    context_in  = payload.get("context", {})

    # ------------------------------------------------------------------
    # Entry 1 — capability received
    # ------------------------------------------------------------------
    ctx.log(
        event_type=ctx.input_schema_name,
        message="Capability received.",
        data={
            "correlationId": ctx.correlation_id,
            "taskId":        ctx.task_id,
            "dryRun":        ctx.dry_run,
            "caller":        ctx.caller,
            "subjectRef":    ctx.subject_ref,
            # question logged truncated — may contain PII
            "questionLength": len(question),
        }
    )

    result = {
        "message":         "This is the Solicitor-General responding via Just-Ask.",
        "questionReceived": question,
        "caller":          ctx.caller,
        "subjectRef":      ctx.subject_ref,
        "governanceLabels": ctx.governance_labels,
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
        "status":          "stub",
    }

    # ------------------------------------------------------------------
    # Entry 2 — capability completed
    # ------------------------------------------------------------------
    ctx.log(
        event_type=ctx.output_schema_name,
        message="Capability completed.",
        data={
            "correlationId": ctx.correlation_id,
            "taskId":        ctx.task_id,
            "dryRun":        ctx.dry_run,
            "outcome":       "stub-response",
        }
    )

    return result
