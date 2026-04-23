# core/observability/logging/sink_loader.py
#
# Configuration (.venv / environment):
#   LOG_SINK          — sink type: json | s3 | dynamodb | windows
#                       (default: json)
#   LOG_PATH          — path for json sink (default: ./logs/platform.jsonl)
#   LOG_S3_BUCKET     — bucket for s3 sink (required if LOG_SINK=s3)
#   LOG_S3_PREFIX     — key prefix for s3 sink (default: logs)
#   LOG_DDB_TABLE     — table name for dynamodb sink (required if LOG_SINK=dynamodb)
#   WINDOWS_EVENT_SOURCE — source name for windows sink (default: YoAIPlatform)

import os


def load_log_sink():
    """
    Instantiate and return the configured log sink.

    Sink modules are imported lazily — only when that sink type is
    requested. This prevents cold-start import failures for sinks whose
    dependencies (pywin32, boto3) are not available in all environments.

    Returns a LogSink instance. Raises ValueError for unknown or
    explicitly unsupported sink types (kafka).
    """
    sink = os.getenv("LOG_SINK", "json").lower()

    if sink == "json":
        from .json_file_sink import JsonFileSink
        return JsonFileSink(
            path=os.getenv("LOG_PATH", "./logs/platform.jsonl")
        )

    if sink == "s3":
        from .s3_sink import S3Sink
        return S3Sink(
            bucket=os.getenv("LOG_S3_BUCKET"),
            prefix=os.getenv("LOG_S3_PREFIX", "logs"),
        )

    if sink == "dynamodb":
        from .dynamodb_sink import DynamoDBSink
        return DynamoDBSink(
            table_name=os.getenv("LOG_DDB_TABLE")
        )

    if sink == "windows":
        # pywin32 is not available on Linux/Lambda — the lazy import here
        # means importing sink_loader is always safe. The failure happens
        # only when LOG_SINK=windows is explicitly requested in a non-Windows
        # environment, which produces a clear ImportError.
        try:
            from .windows_event_sink import WindowsEventSink
            return WindowsEventSink(
                source=os.getenv("WINDOWS_EVENT_SOURCE", "YoAIPlatform")
            )
        except ImportError as exc:
            raise ImportError(
                "LOG_SINK=windows requires pywin32, which is not available "
                "in this environment. Install pywin32 on Windows, or use a "
                "different LOG_SINK for Lambda/Linux deployments."
            ) from exc

    if sink == "kafka":
        raise ValueError(
            "LOG_SINK=kafka is not supported. "
            "Kafka is the Observability Layer, not a log sink. "
            "Use KafkaPublisher (Gap Registry \U0001f7ab) for Kafka event publishing. "
            "For structured logging, use LOG_SINK=dynamodb or LOG_SINK=s3."
        )

    raise ValueError(
        f"Unknown LOG_SINK: '{sink}'. "
        f"Valid values: json, s3, dynamodb, windows."
    )
