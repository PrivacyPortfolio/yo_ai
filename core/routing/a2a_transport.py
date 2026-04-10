# core/routing/a2a_transport.py

from datetime import datetime, timezone


class A2ATransport:
    """
    Protocol-only A2A transport.

    Responsibilities:
      - Accept raw JSON-RPC envelope
      - Run mandatory-but-non-blocking validation
      - Extract request_id (JSON-RPC id) and task_id (A2A metadata.taskID)
      - Hand off to the Solicitor-General (semantic boundary)
      - Wrap the result in a response that is both valid JSON-RPC 2.0
        AND valid A2A v1.0

    ID fields:
      request_id — the JSON-RPC "id" field. Required for JSON-RPC correlation.
                   Extracted once at the protocol boundary and returned on
                   every response as "id".

      task_id    — the A2A "metadata.taskID" field. Required by A2A v1.0.
                   Extracted from envelope.params.metadata.taskID if present.
                   Falls back to request_id if absent or empty — the values
                   can be identical without breaking either spec.
                   Always returned in the response as metadata.taskID so the
                   caller can correlate the response to their task.

    Response shape (valid JSON-RPC 2.0 AND valid A2A v1.0):
      {
        "jsonrpc": "2.0",
        "id": "<request_id>",
        "method": "a2a.message",
        "result": { ... },
        "metadata": {
          "taskID": "<task_id>",
          "status": "completed" | "failed"
        }
      }

    Logging:
      Uses LogBootstrapper.write(dict) via the _TransportLoggerAdapter
      injected from yo_ai_handler.py. Does NOT use stdlib logger directly.
    """

    def __init__(self, solicitor_general, logger, validator):
        self._sg = solicitor_general
        self._logger = logger
        self._validator = validator

    async def handle_a2a(self, envelope: dict) -> dict:

        # ------------------------------------------------------------------
        # 0. Extract protocol identifiers at the boundary
        # ------------------------------------------------------------------
        request_id = envelope.get("id")

        # task_id from A2A metadata — falls back to request_id
        params = envelope.get("params") or {}
        metadata = params.get("metadata") or {}
        task_id = metadata.get("taskID") or request_id

        # ------------------------------------------------------------------
        # 1. Mandatory-but-non-blocking validation
        # ------------------------------------------------------------------
        validation_info = self._run_validation(envelope)
        self._logger.info("a2a.validation", extra={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "task_id": task_id,
            "validation": validation_info,
        })

        # ------------------------------------------------------------------
        # 2. Guard: request_id required — do NOT call SG without it
        #    Returns a null-id JSON-RPC error; no A2A metadata since
        #    we have no task_id to return either.
        # ------------------------------------------------------------------
        if request_id is None:
            self._logger.error("a2a.missing_request_id", extra={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "envelope": envelope,
            })
            return {
                "jsonrpc": "2.0",
                "id": None,
                "method": "a2a.message",
                "error": {
                    "code": -32603,
                    "message": "Missing request_id (JSON-RPC id)",
                },
                "metadata": {
                    "taskID": None,
                    "status": "failed",
                },
            }

        # ------------------------------------------------------------------
        # 3. Hand off to SG (semantic boundary)
        # ------------------------------------------------------------------
        try:
            # semantic_result = await self._sg.route(envelope, request_id)
            semantic_result = await self._runtime.route(envelope)
        except Exception as e:
            self._logger.error("a2a.transport_error", extra={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "task_id": task_id,
                "error": str(e),
                "envelope": envelope,
            })
            return self._build_response(
                request_id=request_id,
                task_id=task_id,
                result=None,
                error={"code": -32603, "message": str(e)},
                status="failed",
            )

        # ------------------------------------------------------------------
        # 4. Wrap in valid JSON-RPC 2.0 + A2A v1.0 response
        # ------------------------------------------------------------------
        return self._build_response(
            request_id=request_id,
            task_id=task_id,
            result=semantic_result,
            status="completed",
        )

    # ------------------------------------------------------------------
    # Response builder
    # ------------------------------------------------------------------
    def _build_response(
        self,
        *,
        request_id,
        task_id,
        result: dict | None = None,
        error: dict | None = None,
        status: str = "completed",
    ) -> dict:
        """
        Build a response envelope that satisfies both JSON-RPC 2.0 and
        A2A v1.0 requirements.

        JSON-RPC 2.0 requires: jsonrpc, id, and either result or error.
        A2A v1.0 requires: method and metadata.taskID on every response.

        Both specs are satisfied simultaneously — the fields are additive
        and do not conflict.
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "a2a.message",
            "metadata": {
                "taskID": task_id,
                "status": status,
            },
        }

        if error:
            response["error"] = error
        else:
            response["result"] = result

        return response

    # ------------------------------------------------------------------
    # Mandatory-but-non-blocking validation
    # ------------------------------------------------------------------
    def _run_validation(self, envelope: dict) -> dict:
        """
        Validate against A2A v1.0 schema.
        Never raises — always returns a structured info object.
        Validation failures are non-blocking: the request proceeds
        regardless, with errors captured in the info payload for logging.
        """
        info = {"v1_0_valid": False, "errors": []}

        try:
            info["v1_0_valid"] = self._validator.validate_request(envelope)
        except Exception:
            pass

        if not info["v1_0_valid"]:
            try:
                info["errors"] = self._validator.get_validation_errors(
                    envelope, "request"
                )
            except Exception:
                info["errors"] = ["validation failed unexpectedly"]

        return info
