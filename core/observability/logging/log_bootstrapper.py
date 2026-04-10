# core/observability/logging/log_bootstrapper.py


import socket
from datetime import datetime, timezone
from typing import Dict, Optional

from .log_sink import LogSink


class LogBootstrapper:
    """
    Primary platform structured logger for Yo-ai agents.

    Each named instance is a singleton, tracked by the module-level registry.
    Does not use Python's stdlib logging module — uses the platform sink model.

    Usage (in handlers):
        LOG = get_logger(AGENT.name)
        LOG.write(event_type="Handler.Complete", message="...", data={...})

    write() never raises. A failed sink.write() is printed to stderr as a
    last resort so the agent is never interrupted by a logging failure.
    """

    def __init__(self, name: str, sink: LogSink):
        self.name     = name
        self.sink     = sink
        self.hostname = socket.gethostname()
        # Emit init record — uses internal _write_safe to avoid recursion risk
        self._write_safe({
            "event_type": "logger_initialized",
        })

    def _enrich(self, record: Dict) -> Dict:
        """
        Add standard envelope fields to every log record.

        correlation_id defaults to None — never fabricate an ID.
        A missing correlation_id in a log record is auditable;
        a fabricated one silently breaks audit trail joins.
        """
        return {
            "timestamp":      datetime.now(timezone.utc).isoformat(),
            "logger":         self.name,
            "host":           self.hostname,
            "sink_type":      type(self.sink).__name__,
            "correlation_id": record.get("correlation_id"),   # None if absent
            "task_id":        record.get("task_id"),
            "level":          record.get("level", "INFO"),
            "actor":          record.get("actor", self.name),
            "event_type":     record.get("event_type", "log"),
            "payload":        record.get("payload", {}),
        }

    def write(self, record: Dict) -> None:
        """
        Enrich and write a structured log record to the configured sink.
        Never raises — sink failures are caught and printed to stderr.
        """
        self._write_safe(record)

    def _write_safe(self, record: Dict) -> None:
        """Internal write with full error isolation."""
        try:
            enriched = self._enrich(record)
            self.sink.write(enriched)
        except Exception as exc:
            # Absolute last resort — print to stderr so Lambda captures it.
            # Never propagate — logging must never crash an agent.
            import sys
            print(
                f"LogBootstrapper({self.name}): sink write failed "
                f"event='{record.get('event_type')}' — {exc}",
                file=sys.stderr
            )

    def flush(self) -> None:
        """Flush buffered sinks (e.g. S3Sink). Call at end of handler."""
        try:
            self.sink.flush()
        except Exception as exc:
            import sys
            print(f"LogBootstrapper({self.name}): flush failed — {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Named singleton registry — one LogBootstrapper per name per execution env.
# Sink is loaded once per name, not once per instantiation.
# ---------------------------------------------------------------------------

_registry: Dict[str, "LogBootstrapper"] = {}


def get_logger(name: str) -> "LogBootstrapper":
    """
    Return the singleton LogBootstrapper for the given name.

    Creates it on first call (loading the sink once).
    Subsequent calls with the same name return the cached instance —
    no new sink connection is created.

    Args:
        name: Agent or component name (e.g. AGENT.name, "a2a_transport")
    """
    if name not in _registry:
        from .sink_loader import load_log_sink
        sink = load_log_sink()
        _registry[name] = LogBootstrapper(name=name, sink=sink)
    return _registry[name]
