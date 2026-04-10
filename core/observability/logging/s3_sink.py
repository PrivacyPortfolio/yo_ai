# core/observability/logging/s3_sink.py
#
# Configuration (.venv / environment):
#   LOG_S3_FLUSH_RECORDS — flush after N records (default: 50)
#
# S3 key format: <prefix>/<date>/<uuid>.jsonl
#
# Important: records in the buffer are lost if the execution environment
# terminates before flush() is called. For critical audit records, use
# DynamoDB sink (LOG_SINK=dynamodb) alongside S3.

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from .log_sink import LogSink

logger = logging.getLogger(__name__)

_FLUSH_RECORDS = int(os.environ.get("LOG_S3_FLUSH_RECORDS", "50"))


class S3Sink(LogSink):
    """
    Buffers log records in memory and flushes them as a single JSONL
    PUT to S3. One PUT per flush, not one PUT per record.

    boto3 is imported lazily at construction.
    write() and flush() never raise.
    """

    def __init__(self, bucket: str, prefix: str = "logs") -> None:
        self.bucket      = bucket
        self.prefix      = prefix
        self._buffer:    List[Dict[str, Any]] = []
        self._s3         = None
        self._init_error: str | None = None

        if not bucket:
            self._init_error = "bucket is None or empty"
            logger.warning("S3Sink: bucket not configured — sink disabled.")
        else:
            self._connect()

    def _connect(self) -> None:
        """Lazy boto3 import. Errors stored, not raised."""
        try:
            import boto3
            self._s3 = boto3.client("s3")
        except Exception as exc:
            self._init_error = str(exc)
            logger.error("S3Sink: failed to create S3 client — %s", exc)

    def write(self, record: Dict[str, Any]) -> None:
        """
        Add record to buffer. Flushes automatically at threshold.
        Never raises.
        """
        if self._s3 is None:
            return   # silently skip — init error already logged

        try:
            self._buffer.append(record)
        except Exception as exc:
            logger.error("S3Sink: failed to buffer record — %s", exc)
            return

        if len(self._buffer) >= _FLUSH_RECORDS:
            self.flush()

    def flush(self) -> None:
        """
        Write all buffered records as a single JSONL PUT to S3.
        Buffer is cleared whether the PUT succeeds or fails.
        Never raises.
        """
        if not self._buffer:
            return

        if self._s3 is None:
            logger.warning(
                "S3Sink: flush called but S3 client not available — "
                "%d record(s) discarded (init error: %s)",
                len(self._buffer), self._init_error
            )
            self._buffer.clear()
            return

        records = list(self._buffer)
        self._buffer.clear()   # clear before PUT — don't retry on failure

        try:
            now  = datetime.now(timezone.utc)
            key  = f"{self.prefix}/{now.strftime('%Y/%m/%d')}/{uuid.uuid4()}.jsonl"
            body = "\n".join(
                json.dumps(r, default=str) for r in records
            ) + "\n"

            self._s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/x-ndjson",
            )
        except Exception as exc:
            # Records are already cleared — loss is logged explicitly
            logger.error(
                "S3Sink: PUT failed — %d record(s) lost — %s",
                len(records), exc
            )

    def close(self) -> None:
        """Flush remaining buffer before closing."""
        self.flush()
