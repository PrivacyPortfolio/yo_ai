# core/observability/logging/windows_event_sink.py
#
# Fixes applied:
#   - import win32evtlogutil at module level — crashes Lambda on cold start.
#     Fixed: both win32evtlog and win32evtlogutil are imported lazily
#     inside __init__(). Importing this module is now always safe.
#   - EVENTLOG_INFORMATION_TYPE accessed as win32evtlogutil.EVENTLOG_...
#     — that constant lives on win32evtlog, not win32evtlogutil. Fixed.
#   - No error handling on ReportEvent() — wrapped in try/except.
#     Logging must never crash an agent.

import json
import logging
from typing import Any, Dict

from .log_sink import LogSink

logger = logging.getLogger(__name__)


class WindowsEventSink(LogSink):
    """
    Writes structured log records to the Windows Event Log.

    pywin32 (win32evtlog, win32evtlogutil) is imported lazily at
    construction — importing this module is always safe on Linux/Lambda.
    If pywin32 is unavailable, write() silently no-ops.

    write() never raises — all win32evtlogutil calls wrapped in try/except.
    """

    def __init__(self, source: str) -> None:
        self.source           = source
        self._available       = False
        self._win32evtlog     = None
        self._win32evtlogutil = None

        # Lazy import — must be inside __init__, not at module level
        try:
            import win32evtlog
            import win32evtlogutil
            self._win32evtlog     = win32evtlog
            self._win32evtlogutil = win32evtlogutil
            self._available       = True
        except ImportError:
            logger.warning(
                "WindowsEventSink: pywin32 not available — "
                "sink is disabled. Expected on Linux/Lambda."
            )

    def write(self, record: Dict[str, Any]) -> None:
        """
        Write a log record to the Windows Event Log.
        No-op if pywin32 is unavailable. Never raises.
        """
        if not self._available:
            return

        try:
            message = json.dumps(record, default=str)

            # EVENTLOG_INFORMATION_TYPE lives on win32evtlog, not win32evtlogutil
            self._win32evtlogutil.ReportEvent(
                self.source,
                eventID=1,
                eventCategory=0,
                eventType=self._win32evtlog.EVENTLOG_INFORMATION_TYPE,
                strings=[message],
            )
        except Exception as exc:
            # Never propagate — logging must never crash an agent
            logger.error(
                "WindowsEventSink: ReportEvent failed for event '%s' — %s",
                record.get("event_type"), exc
            )
