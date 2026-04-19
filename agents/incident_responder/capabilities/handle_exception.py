# agents/incident_responder/capabilities/handle_exception.py

from datetime import datetime, timezone
import traceback
from core.yoai_context import YoAiContext
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("incident_responder")

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Capability: Handle.Exception

    Stub: handles uncaught exceptions and produces a structured,
    platform-consistent incident response.

    Real implementation would:
      - capture stack trace
      - classify severity
      - identify failing module
      - generate remediation workflow (Workflow-Builder)
      - notify Sentinel or SG
      - log incident to platform telemetry
    """

    exception = payload.get("exception")
    stack = payload.get("stackTrace")

    # If the caller didn't provide a stack trace, we normalize it.
    normalized_stack = stack or traceback.format_exc()

    LOG.write(
        event_type="handle_exception.Request",
        payload={
          "exception": exception,
          "stackTrace": stack
        },
        context=ctx,
        include=["profile", "actor", "caller"],
    )

    return {
        "message": "Stub incident response.",
        "exceptionType": type(exception).__name__ if exception else "UnknownException",
        "exceptionMessage": str(exception) if exception else "No message provided.",
        "stackTrace": normalized_stack,
        "severity": "critical",
        "remediation": "Stub remediation workflow.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.get("correlation_id"),
        "taskId":          ctx.get("task_id"),
    }