# agents/purchasing_agent/capabilities/purchase_history_generate.py

"""
Capability: Purchase-History.Generate
Stub — returns hardcoded history. Next: fetch from purchase history store.
"""

from datetime import datetime, timezone
from core.yoai_context import YoAiContext

async def run(payload: dict, ctx: YoAiContext) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      agent_ctx     — AgentContext | None  (governance, startup_mode, caller)
      capability_ctx — CapabilityContext | None  (slim, dry_run, trace, workflow state)
    """

    return {
        "capability": "Purchase-History.Generate",
        "status": "stub",
        "message": "Stub Purchase-History.Generate response.",
        "history": [] if ctx.dry_run else [
            {"item": "Example Item A", "price": 19.99, "timestamp": "2026-01-01"},
            {"item": "Example Item B", "price": 42.00, "timestamp": "2026-01-15"},
        ],
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
