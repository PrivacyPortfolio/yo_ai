# agents/purchasing_agent/capabilities/purchase_receipt_generate.py

"""
Capability: Purchase-Receipt.Generate
Stub — returns hardcoded receipt. Next: generate real receipt from transaction record.
"""


async def run(payload: dict, agent_ctx, capability_ctx) -> dict:
    """
    Args:
      payload       — capability-specific input fields
      agent_ctx     — AgentContext | None  (governance, startup_mode, caller)
      capability_ctx — CapabilityContext | None  (slim, dry_run, trace, workflow state)
    """
    item = payload.get("item")
    price = payload.get("price")

    profile = None
    correlation_id = None
    task_id = None
    dry_run = False

    if capability_ctx is not None:
        profile = capability_ctx.resolve("profile", agent_ctx)
        correlation_id = capability_ctx.resolve("correlation_id", agent_ctx)
        task_id = capability_ctx.resolve("task_id", agent_ctx) or correlation_id
        dry_run = capability_ctx.dry_run

    return {
        "capability": "Purchase-Receipt.Generate",
        "status": "stub",
        "message": "Stub Purchase-Receipt.Generate response.",
        "receipt": None if dry_run else {
            "item": item,
            "price": price,
            "vendor": "StubVendor",
            "timestamp": "2026-02-19T00:00:00Z",
        },

        "subjectProfile": profile,
        "correlationId": correlation_id,
        "taskId": task_id,
    }
