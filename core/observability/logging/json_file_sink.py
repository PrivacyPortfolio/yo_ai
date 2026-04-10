# core/observability/logging/json_file_sink.py
#
# Fixes applied:
#   - File opened and closed on every write() — fixed by opening once
#     at construction in append mode and holding the handle open.
#     flush() called after every write() to ensure records survive
#     process exit without requiring an explicit close().
#   - No error handling — all file I/O now wrapped in try/except.
#     Logging must never crash an agent.
#   - flush() and close() implemented per LogSink contract.

import json
import logging
from pathlib import Path
from typing import Any, Dict

from .log_sink import LogSink

logger = logging.getLogger(__name__)


class JsonFileSink(LogSink):
    """
    Appends structured log records as JSONL to a local file.

    File handle is opened once at construction — not opened/closed per
    write(). flush() is called after every write() to ensure records
    survive process exit.

    write() never raises — all errors caught and logged to stdlib logger.
    """

    def __init__(self, path: str) -> None:
        self._path       = Path(path)
        self._file       = None
        self._init_error: str | None = None
        self._open()

    def _open(self) -> None:
        """Open file in append mode. Errors stored, not raised."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            # buffering=1 = line-buffered; flush() still called explicitly
            self._file = open(self._path, "a", encoding="utf-8", buffering=1)
        except Exception as exc:
            self._init_error = str(exc)
            logger.error(
                "JsonFileSink: failed to open '%s' — %s", self._path, exc
            )

    def write(self, record: Dict[str, Any]) -> None:
        """
        Append one JSON record to the log file.
        Never raises — all errors caught and logged to stdlib logger.
        """
        if self._file is None:
            logger.warning(
                "JsonFileSink: skipping write — file not available "
                "(init error: %s)", self._init_error
            )
            return

        try:
            self._file.write(json.dumps(record, default=str) + "\n")
            self._file.flush()   # ensure record survives process exit
        except Exception as exc:
            logger.error(
                "JsonFileSink: write failed for event '%s' — %s",
                record.get("event_type"), exc
            )

    def flush(self) -> None:
        """Explicit flush — called by LogBootstrapper at handler completion."""
        if self._file is not None:
            try:
                self._file.flush()
            except Exception as exc:
                logger.error("JsonFileSink: flush failed — %s", exc)

    def close(self) -> None:
        """Flush and close the file handle. Safe to call multiple times."""
        if self._file is not None:
            try:
                self._file.flush()
                self._file.close()
                self._file = None
            except Exception as exc:
                logger.error("JsonFileSink: close failed — %s", exc)
