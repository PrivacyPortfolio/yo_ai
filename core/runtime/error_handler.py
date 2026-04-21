# /core/runtime/error_handler.py

from __future__ import annotations
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Canonical Error Codes
# ---------------------------------------------------------------------------

class A2AErrorCodes:
    """
    JSON-RPC + A2A-specific error codes.

    JSON-RPC Standard:
      -32600  Invalid Request
      -32601  Method not found
      -32602  Invalid params
      -32603  Internal error

    A2A-Specific (Section 5.4):
      -32001 to -32099 reserved for A2A platform errors.
    """

    METHOD_NOT_FOUND = -32601
    INTERNAL_ERROR = -32603

    # A2A-specific examples
    TASK_NOT_FOUND = -32001
    AGENT_NOT_AVAILABLE = -32002
    CAPABILITY_NOT_FOUND = -32003
    SCHEMA_VALIDATION_FAILED = -32004
    TOOL_EXECUTION_FAILED = -32005
    PROVIDER_ADAPTER_ERROR = -32006

    # Default for ANY unhandled exception
    UNHANDLED_EXCEPTION = -32050


# ---------------------------------------------------------------------------
# Canonical AnyException Wrapper
# ---------------------------------------------------------------------------

class AnyException(Exception):
    """
    The platform's canonical safe exception type.

    Every exception—Python, agent, adapter, tool, or runtime—is converted
    into an AnyException before being wrapped in a JSON-RPC error envelope.

    Attributes:
        code: A2A or JSON-RPC error code
        message: Human-readable message
        data: Optional structured diagnostic context
    """

    def __init__(self, code: int, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Universal Error Handler
# ---------------------------------------------------------------------------

class ErrorHandler:
    """
    Universal exception normalizer for YoAiAgents and PlatformAgents.

    Responsibilities:
      - Convert ANY EXCEPTION into a canonical AnyException.
      - Wrap that exception in a JSON-RPC 2.0 error envelope.
      - Capture ANY ERROR CODES as structured diagnostic context in `error.data`.
      - Never raise; always return a safe error response.
    """

    # -------------------------------------------------------------------
    # 1. Coerce ANY exception into AnyException
    # -------------------------------------------------------------------
    @staticmethod
    def coerce_exception(exc: Exception) -> AnyException:
        """
        Convert any Python exception into a canonical AnyException.

        Rules:
          - If it's already an AnyException, return as-is.
          - If it has an attribute `a2a_code`, use it.
          - Otherwise, assign UNHANDLED_EXCEPTION.
        """

        if isinstance(exc, AnyException):
            return exc

        # If the exception defines a custom A2A code
        code = getattr(exc, "a2a_code", A2AErrorCodes.UNHANDLED_EXCEPTION)

        # Preserve the original message
        message = str(exc) or exc.__class__.__name__

        # Capture raw exception metadata
        data = {
            "originalExceptionType": exc.__class__.__name__,
            "originalMessage": str(exc),
        }

        return AnyException(code=code, message=message, data=data)

    # -------------------------------------------------------------------
    # 2. Build JSON-RPC error envelope
    # -------------------------------------------------------------------
    @staticmethod
    def build_error_response(
        *,
        code: int,
        message: str,
        request_id: Optional[Any],
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Construct a JSON-RPC 2.0 error response.
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
                "data": data or {},
            },
        }

    # -------------------------------------------------------------------
    # 3. Normalize exception into JSON-RPC envelope
    # -------------------------------------------------------------------
    @staticmethod
    def normalize_exception(
        exc: Exception,
        *,
        request_id: Optional[Any],
        agent_name: Optional[str] = None,
        capability: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert ANY exception into a structured JSON-RPC error envelope.

        This is the universal entrypoint used by:
        - global error middleware
        - Solicitor-General runtime
        - A2ATransport (JSON-RPC envelope parsing)
        - agent execution wrappers
        """

        # Step 1: Coerce into canonical AnyException
        safe_exc = ErrorHandler.coerce_exception(exc)

        # Step 2: Build diagnostic data
        error_data = {
            "timestamp": utc_now_iso(),
            "correlationId": str(uuid.uuid4()),

            # Exception metadata
            "exceptionType": safe_exc.__class__.__name__,
            "exceptionMessage": safe_exc.message,
            "exceptionCode": safe_exc.code,

            # Raw Python exception metadata
            "stack": traceback.format_exc(),
            "agent": agent_name,
            "capability": capability,
        }

        # Merge AnyException.data
        error_data.update(safe_exc.data or {})

        # Merge optional context
        if context:
            error_data.update(context)

        # Step 3: Build JSON-RPC envelope
        return ErrorHandler.build_error_response(
            code=safe_exc.code,
            message=safe_exc.message,
            request_id=request_id,
            data=error_data,
        )

    # -------------------------------------------------------------------
    # 4. Build known-error responses without raising
    # -------------------------------------------------------------------
    @staticmethod
    def from_known_error(
        *,
        code: int,
        message: str,
        request_id: Optional[Any],
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build an error response for known A2A or JSON-RPC errors
        without raising an exception.
        """
        data = {
            "timestamp": utc_now_iso(),
            "correlationId": str(uuid.uuid4()),
        }
        if extra:
            data.update(extra)

        return ErrorHandler.build_error_response(
            code=code,
            message=message,
            request_id=request_id,
            data=data,
        )