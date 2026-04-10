# core/observability/logging/log_sink.py

import abc


class LogSink(abc.ABC):
    """
    Abstract base class for all Yo-ai log sinks.

    Contract (all implementations must honor):
      - write() must never raise — logging must never crash an agent.
        Catch all exceptions internally; log to stderr as last resort.
      - flush() is a no-op for sinks that do not buffer. Sinks that
        buffer (e.g. S3Sink) must flush remaining records.
      - close() releases held resources (file handles, connections).
        Must be safe to call even if the sink was never fully opened,
        and safe to call multiple times.
    """

    @abc.abstractmethod
    def write(self, record: dict) -> None:
        """
        Persist a structured log record.
        Must never raise.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """
        Flush any buffered records to the underlying sink.
        Default is a no-op for sinks that write immediately.
        """

    def close(self) -> None:
        """
        Release any held resources.
        Default is a no-op. Safe to call multiple times.
        """
