# agents/purchasing_agent/capabilities/purchase_eligibility_validate.py

"""
Capability: Purchase-Eligibility.Validate
Stub — always eligible. Next: evaluate budget, profile, and vendor rules.
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
    item = payload.get("item")
    amount = payload.get("amount")

    return {
        "capability": "Purchase-Eligibility.Validate",
        "status": "stub",
        "message": "Stub Purchase-Eligibility.Validate response.",
        "item": item,
        "amount": amount,
        "eligible": not ctx.dry_run,
        "reason": "dry_run: eligibility withheld" if ctx.dry_run else "Stub approval.",
        "subjectProfile": ctx.profile,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "correlationId":   ctx.correlation_id,
        "taskId":          ctx.task_id,
        "dryRun":          ctx.dry_run,
    }
