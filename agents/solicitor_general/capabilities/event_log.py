# agents/solicitor_general/capabilities/event_log.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("solicitor_general")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Event.Log
    Inserts a record into the platform event log on behalf of a caller.

    Callers that do not have direct access to PlatformLogger invoke this
    capability through the Solicitor-General, which acts as governor —
    validating, enriching, and writing the record with full platform context.

    Args:
        payload        (dict): Pre-extracted capability input.
        ctx            (YoAiContext): Governance context.
    """

    event_type_in = payload.get("eventType", "")
    event_data    = payload.get("event", {})
    source        = payload.get("source", ctx.caller)

    # ------------------------------------------------------------------
    # Entry 1 — capability received
    # ------------------------------------------------------------------
    LOG.write(
        event_type="Event.Log.Request",
        payload={
            "eventType":        event_type_in,
            "source":           source,
            "correlationId":    ctx.correlation_id,
            "taskId":           ctx.task_id,
            "governanceLabels": ctx.governance_labels,
        },
        context=ctx,
    )

    result = {
        "message":          "Event logged successfully.",
        "eventType":        event_type_in,
        "event":            event_data,
        "source":           source,
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "correlationId":    ctx.correlation_id,
        "taskId":           ctx.task_id,
        "governanceLabels": ctx.governance_labels,
        "dryRun":           ctx.dry_run,
        "status":           "stub",
    }

    # ------------------------------------------------------------------
    # Entry 2 — capability completed
    # ------------------------------------------------------------------
    LOG.write(
        event_type="Event.Log.Response",
        payload={
            "eventType":        event_type_in,
            "source":           source,
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "outcome":          "logged",
            "correlationId":    ctx.correlation_id,
            "taskId":           ctx.task_id,
            "governanceLabels": ctx.governance_labels,
        },
        context=ctx,
    )

    return result
