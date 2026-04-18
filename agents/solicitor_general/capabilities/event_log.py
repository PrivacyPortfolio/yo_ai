# agents/solicitor_general/capabilities/event_log.py

from datetime import datetime, timezone
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("solicitor_general")


async def run(payload: dict, ctx: YoAiContext) -> dict:
    # ── Capability: Event.Log ──────────────────────────────────────────────
    # Inserts a record into the platform event log on behalf of a caller.
    # Callers without direct PlatformLogger access invoke this through the SG,
    # which validates, enriches, and writes the record with full platform context.

    event_type_in = payload.get("eventType", "")
    event_data    = payload.get("event", {})
    source        = payload.get("source") or ctx.get("caller")

    # ── Entry 1: capability received ───────────────────────────────────────
    LOG.write(
        event_type="Event.Log.Request",
        payload={
            "eventType":        event_type_in,
            "source":           source,
            "correlationId":    ctx.get("correlation_id"),
            "taskId":           ctx.get("task_id"),
            "governanceLabels": ctx.get("governance_labels"),
        },
        context=ctx,
    )

    result = {
        "message":          "Event logged successfully.",
        "eventType":        event_type_in,
        "event":            event_data,
        "source":           source,
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "correlationId":    ctx.get("correlation_id"),
        "taskId":           ctx.get("task_id"),
        "governanceLabels": ctx.get("governance_labels"),
        "dryRun":           ctx.get("dry_run"),
        "status":           "stub",
    }

    # ── Entry 2: capability completed ─────────────────────────────────────
    LOG.write(
        event_type="Event.Log.Response",
        payload={
            "eventType":        event_type_in,
            "source":           source,
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "outcome":          "logged",
            "correlationId":    ctx.get("correlation_id"),
            "taskId":           ctx.get("task_id"),
            "governanceLabels": ctx.get("governance_labels"),
        },
        context=ctx,
    )

    return result
