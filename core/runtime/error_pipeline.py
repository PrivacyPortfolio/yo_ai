# core/runtime/error_pipeline.py
#
# Centralized error normalization + optional Incident Responder forwarding.
#
# Wraps ErrorHandler for use inside try/except blocks anywhere in the platform.
# Any agent or handler that needs structured error handling imports this:
#
#   from core.runtime.error_pipeline import ErrorPipeline
#
# Two entry points matching the two ErrorHandler use cases:
#
#   handle_exception(exc, ctx, ...)
#     — for try/except catches of unexpected exceptions.
#       Calls ErrorHandler.normalize_exception(), then forwards to IR.
#
#   handle_known_error(code, message, ctx, ...)
#     — for known validation failures, missing agents, bad requests.
#       Calls ErrorHandler.from_known_error(), then forwards to IR.
#
# Both return a JSON-RPC error envelope built by core/runtime/envelope.py.
# The Incident Responder is optional — inject None to skip forwarding
# (useful for test harnesses, non-platform agents, or agents that ARE
# the Incident Responder and must not recurse).
#
# Injection pattern:
#
#   from core.runtime.error_pipeline import ErrorPipeline
#   from agents.incident_responder.runtime.incident_responder import IncidentResponderAgent
#
#   _ir = IncidentResponderAgent(event_bus=_event_bus, slim=True)
#   _pipeline = ErrorPipeline(incident_responder_fn=_ir.handle_exception)
#
# Then in a try/except:
#
#   except Exception as exc:
#       return await _pipeline.handle_exception(exc, ctx=ctx,
#           capability=capability_id, agent_name=self.name)

from __future__ import annotations
from typing import Any, Awaitable, Callable, Dict, Optional

from core.runtime.error_handler import ErrorHandler
from core.yoai_context import YoAiContext
from core.runtime.envelope import error_envelope


# ── Type alias for the IR callable ────────────────────────────────────────
# Accepts the error envelope dict and ctx. Matches handle_exception(payload, ctx).
IncidentResponderFn = Callable[[dict, YoAiContext | None], Awaitable[dict]]


class ErrorPipeline:
    # ── Centralized error normalization + IR forwarding ────────────────────
    # Instantiated once per agent or handler that needs structured errors.
    # incident_responder_fn=None disables forwarding silently.

    def __init__(
        self,
        incident_responder_fn: IncidentResponderFn | None = None,
    ) -> None:
        self._ir = incident_responder_fn

    # ── try/except entry point ─────────────────────────────────────────────

    async def handle_exception(
        self,
        exc: Exception,
        *,
        ctx: YoAiContext | None = None,
        request_id: Any | None = None,
        agent_name: str | None = None,
        capability: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        # ── Normalize → envelope → forward ────────────────────────────────
        # request_id falls back to ctx["correlation_id"] if not supplied —
        # the envelope id should always be the correlation id for the request.
        resolved_request_id = request_id or (ctx.get("correlation_id") if ctx else None)

        normalized = ErrorHandler.normalize_exception(
            exc,
            request_id=resolved_request_id,
            agent_name=agent_name,
            capability=capability,
            context=extra,
        )

        # Rebuild as a proper envelope using core/runtime/envelope.py so the shape
        # is consistent with success_envelope — same id, same metadata slot.
        envelope = error_envelope(
            code=normalized["error"]["code"],
            message=normalized["error"]["message"],
            ctx=ctx,
            data=normalized["error"].get("data"),
        )

        await self._forward(envelope, ctx)
        return envelope

    # ── known-error entry point ────────────────────────────────────────────

    async def handle_known_error(
        self,
        *,
        code: int,
        message: str,
        ctx: YoAiContext | None = None,
        request_id: Any | None = None,
        extra: dict | None = None,
    ) -> dict:
        # ── Build → envelope → forward ─────────────────────────────────────
        resolved_request_id = request_id or (ctx.get("correlation_id") if ctx else None)

        normalized = ErrorHandler.from_known_error(
            code=code,
            message=message,
            request_id=resolved_request_id,
            extra=extra,
        )

        envelope = error_envelope(
            code=normalized["error"]["code"],
            message=normalized["error"]["message"],
            ctx=ctx,
            data=normalized["error"].get("data"),
        )

        await self._forward(envelope, ctx)
        return envelope

    # ── IR forwarding ──────────────────────────────────────────────────────

    async def _forward(
        self,
        error_envelope_dict: dict,
        ctx: YoAiContext | None,
    ) -> None:
        # ── Forward to Incident Responder if injected ──────────────────────
        # Failures in forwarding are suppressed — the original error envelope
        # is always returned to the caller regardless. IR forwarding is
        # best-effort: it enriches the audit trail but must never cause a
        # second failure to propagate.
        if self._ir is None:
            return
        try:
            await self._ir(error_envelope_dict, ctx)
        except Exception:
            pass   # forwarding failure must never mask the original error
