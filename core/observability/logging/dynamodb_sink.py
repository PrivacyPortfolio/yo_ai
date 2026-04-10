# core/observability/logging/dynamodb_sink.py
#
# Fixes applied:
#   - boto3 imported at module level — lazy import inside __init__ instead.
#     Prevents cold-start failure if boto3 is not installed.
#   - No error handling on put_item() — all boto3 calls now wrapped in
#     try/except. Logging must never crash an agent.
#   - No TTL support — added optional TTL via LOG_DDB_TTL_DAYS env var.
#   - Class named DynamoSink — renamed DynamoDBSink for consistency.
#     sink_loader.py updated to match.

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from .log_sink import LogSink

logger = logging.getLogger(__name__)

_TTL_DAYS = int(os.environ.get("LOG_DDB_TTL_DAYS", "90"))


class DynamoDBSink(LogSink):
    """
    Writes structured log records to a DynamoDB table.

    boto3 is imported lazily at construction so importing this module
    is always safe on non-AWS environments.

    write() never raises — all boto3 errors are caught and logged via
    the stdlib logger (which flows to CloudWatch on Lambda).
    """

    def __init__(self, table_name: str) -> None:
        self.table_name  = table_name
        self._table      = None
        self._init_error: str | None = None
        self._connect()

    def _connect(self) -> None:
        """Lazy boto3 import and table connection. Errors stored, not raised."""
        try:
            import boto3
            self._table = boto3.resource("dynamodb").Table(self.table_name)
        except Exception as exc:
            self._init_error = str(exc)
            logger.error(
                "DynamoDBSink: failed to connect to table '%s' — %s",
                self.table_name, exc
            )

    def write(self, record: Dict[str, Any]) -> None:
        """
        Write a log record to DynamoDB.
        Never raises — all errors caught and logged to stdlib logger.
        """
        if self._table is None:
            logger.warning(
                "DynamoDBSink: skipping write — table not available "
                "(init error: %s)", self._init_error
            )
            return

        try:
            item = dict(record)   # shallow copy — don't mutate caller's dict

            # Optional TTL
            if _TTL_DAYS > 0:
                expiry = datetime.now(timezone.utc) + timedelta(days=_TTL_DAYS)
                item["ttl"] = int(expiry.timestamp())

            self._table.put_item(Item=item)

        except Exception as exc:
            # Never propagate — logging must never crash an agent
            logger.error(
                "DynamoDBSink: put_item failed for event '%s' — %s",
                record.get("event_type"), exc
            )
