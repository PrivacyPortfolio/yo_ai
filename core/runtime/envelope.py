# core/envelope.py
#
# Shared A2A envelope builders and capability extractor.
# Pure functions — no state, no agent imports, usable by any agent.
#
# Any agent that needs to build or parse A2A envelopes imports from here:
#
#   from core.envelope import success_envelope, error_envelope, extract
#
# The SG's _success_envelope() and _error_envelope() instance methods
# are thin delegations to these functions and can be removed once all
# callers are updated to import directly.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from core.yoai_context import YoAiContext


# ── Response envelope builders ─────────────────────────────────────────────

def success_envelope(
    capability_id: str,
    result: dict,
    ctx: YoAiContext,
) -> dict:
    # ── JSON-RPC 2.0 + A2A v1.0 success response ──────────────────────────
    # correlation_id and task_id come from ctx — the request-scoped values
    # built from the live envelope. Never from agent-level self.* attrs.
    return {
        "jsonrpc": "2.0",
        "id":      ctx.get("correlation_id"),
        "result":  result,
        "metadata": {
            "capability": capability_id,
            "taskId":     ctx.get("task_id"),
            "timestamp":  datetime.now(timezone.utc).isoformat(),
        },
    }


def error_envelope(
    code: int,
    message: str,
    ctx: YoAiContext | None = None,
    data: dict | None = None,
) -> dict:
    # ── JSON-RPC 2.0 error response ────────────────────────────────────────
    # correlation_id from ctx when available, None when ctx not yet built
    # (e.g. transport-level parse errors before any ctx exists).
    # data carries structured diagnostic context from ErrorHandler.
    error_block: dict = {"code": code, "message": message}
    if data:
        error_block["data"] = data
    return {
        "jsonrpc": "2.0",
        "id":      ctx.get("correlation_id") if ctx else None,
        "error":   error_block,
    }


# ── Envelope extractor ─────────────────────────────────────────────────────

def extract(envelope: dict) -> Tuple[str, dict]:
    # ── Extract capability_id and payload from any inbound envelope ─────────
    # Handles both A2A (method="a2a.<capability>") and direct invocation
    # (capability="<capability>") shapes.
    #
    # Returns (capability_id, payload). Never raises — unknown shapes
    # produce capability_id="unknown" and an empty payload so the caller
    # can surface a clean -32601 error rather than an unhandled exception.
    capability_id = (
        envelope.get("capability")
        or envelope.get("method", "").replace("a2a.", "")
        or "unknown"
    )

    raw_payload = (
        envelope.get("payload")
        or envelope.get("params")
        or {}
    )

    payload = raw_payload if isinstance(raw_payload, dict) else {"input": raw_payload}

    return capability_id, payload
