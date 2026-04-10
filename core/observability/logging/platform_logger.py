# core/observability/logging/platform_logger.py
#
# PlatformLogger — unified structured logger for all Yo-ai platform modules.
#
# Wraps LogBootstrapper (sink model, error isolation, singleton registry).
# Exposes both a write(dict) interface (for structured callers) and
# .info() / .error() / .warning() / .debug() convenience methods
# (for infrastructure modules without context objects).
#
# Every record is enriched with the semantic platform envelope before writing.
# Missing attributes in YoAiContext are ignored — a helper method 
# extracts the canonical minimal context footprint essential for correlation.
#
# Usage:
#
#   from core.observability.logging.platform_logger import get_platform_logger
#
#   LOG = get_platform_logger("solicitor_general")
#
#   # Modules with full context (capability handlers, agents):
#   LOG.write(
#       event_type="Handler.Complete",
#       payload={"duration_ms": 42},
#       context=ctx,
#       include=["actor", "profile"],
#   )
#
#   # Infrastructure modules without context objects:
#   LOG = get_platform_logger("openai_client")
#   LOG.error("openai_client.error", payload={"detail": str(exc)})
#

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from .log_bootstrapper import LogBootstrapper, get_logger as _get_bootstrapper

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _extract_context_fields(ctx: Any) -> Dict[str, Any]:
    """
    Extract the canonical minimal context footprint.
    These fields are safe, stable, and essential for correlation.
    Missing attributes are ignored.
    """
    canonical_fields = [
        "correlation_id",
        "task_id",
        "actor_kind",
        "capability_id",
        "instance_id",
        "startup_mode",
        "step",
    ]

    out = {}
    for field in canonical_fields:
        if hasattr(ctx, field):
            out[field] = getattr(ctx, field)
    return out


def _serialize_context(ctx: Any, include: Optional[Union[List[str], str]]) -> Dict[str, Any]:
    """
    Serialize context according to the enrichment rules.

    include=None      → only canonical fields
    include=[...]     → canonical + selected fields
    include="*"       → full ctx.to_dict() if available, else vars(ctx)
    """
    if ctx is None:
        return {}

    # Canonical minimal footprint
    base = _extract_context_fields(ctx)

    # Full dump
    if include == "*" or (isinstance(include, list) and "*" in include):
        if hasattr(ctx, "to_dict"):
            return ctx.to_dict()
        if isinstance(ctx, dict):
            return ctx
        try:
            return vars(ctx)
        except Exception:
            return {"context": str(ctx)}

    # Selective enrichment
    if isinstance(include, list):
        for key in include:
            if hasattr(ctx, key):
                base[key] = getattr(ctx, key)
        return base

    # Default: canonical only
    return base


class PlatformLogger:
    """
    Unified platform logger.

    Thin enrichment layer over LogBootstrapper. Builds a structured record
    with event_time, payload, and optional context enrichment, then delegates
    to the bootstrapper's write-safe sink pipeline.

    Never raises.
    """

    def __init__(self, bootstrapper: LogBootstrapper) -> None:
        self._log = bootstrapper

    # ------------------------------------------------------------------
    # Primary interface
    # ------------------------------------------------------------------
    def write(
        self,
        *,
        event_type: str,
        payload: Optional[Dict] = None,
        context: Any = None,
        include: Optional[Union[List[str], str]] = None,
        event_time: Optional[str] = None,
        level: str = "INFO",
    ) -> None:
        """
        Write a structured log record.

        Args:
            event_type: Semantic identifier for the event.
            payload: Structured data (dict).
            context: Optional context object (YoAiContext or any object).
            include: None → canonical fields only
                     ["actor", "profile"] → selective enrichment
                     "*" → full context dump
            event_time: Optional event timestamp. If omitted, auto-generated.
            level: Log level ("INFO", "ERROR", etc.).
        """
        record = {
            "event_type": event_type,
            "level": level,
            "payload": payload or {},
            "event_time": event_time or _now_iso(),
            "context": _serialize_context(context, include),
        }

        self._log.write(record)



    # ------------------------------------------------------------------
    # Convenience level methods
    # ------------------------------------------------------------------

    def info(
        self,
        event_type: str,
        *,
        payload: Optional[Dict] = None,
        context: Any = None,
        include: Optional[Union[List[str], str]] = None,
        event_time: Optional[str] = None,
    ) -> None:
        self.write(
            event_type=event_type,
            payload=payload,
            context=context,
            include=include,
            event_time=event_time,
            level="INFO",
        )

    def warning(
        self,
        event_type: str,
        *,
        payload: Optional[Dict] = None,
        context: Any = None,
        include: Optional[Union[List[str], str]] = None,
        event_time: Optional[str] = None,
    ) -> None:
        self.write(
            event_type=event_type,
            payload=payload,
            context=context,
            include=include,
            event_time=event_time,
            level="WARNING",
        )

    def error(
        self,
        event_type: str,
        *,
        payload: Optional[Dict] = None,
        context: Any = None,
        include: Optional[Union[List[str], str]] = None,
        event_time: Optional[str] = None,
    ) -> None:
        self.write(
            event_type=event_type,
            payload=payload,
            context=context,
            include=include,
            event_time=event_time,
            level="ERROR",
        )

    def debug(
        self,
        event_type: str,
        *,
        payload: Optional[Dict] = None,
        context: Any = None,
        include: Optional[Union[List[str], str]] = None,
        event_time: Optional[str] = None,
    ) -> None:
        self.write(
            event_type=event_type,
            payload=payload,
            context=context,
            include=include,
            event_time=event_time,
            level="DEBUG",
        )


# ---------------------------------------------------------------------------
# Factory — mirrors LogBootstrapper's singleton registry
# ---------------------------------------------------------------------------

_registry: Dict[str, PlatformLogger] = {}


def get_platform_logger(name: str) -> PlatformLogger:
    """
    Return the singleton PlatformLogger for the given name.

    Backed by the same LogBootstrapper singleton registry, so the sink
    is loaded exactly once per name regardless of how many modules call this.
    """
    if name not in _registry:
        bootstrapper = _get_bootstrapper(name)
        _registry[name] = PlatformLogger(bootstrapper)
    return _registry[name]
