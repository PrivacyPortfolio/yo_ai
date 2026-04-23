# core/routing/a2a_transport.py
#
# Protocol-only A2A transport.
#
# Responsibilities:
#   - Accept raw JSON-RPC envelope
#   - Run mandatory-but-non-blocking validation
#   - Extract request_id (JSON-RPC id) and task_id (A2A metadata.taskID)
#   - Hand off to the Solicitor-General (semantic boundary)
#   - Wrap the result in a response that is both valid JSON-RPC 2.0
#     AND valid A2A v1.0
#
# ID fields:
#   request_id — the JSON-RPC "id" field. Required for JSON-RPC correlation.
#                Extracted once at the protocol boundary and returned on
#                every response as "id".
#
#   task_id    — the A2A "metadata.taskID" field. Required by A2A v1.0.
#                Extracted from envelope.params.metadata.taskID if present.
#                Falls back to request_id if absent — values can be identical
#                without breaking either spec.
#                Always returned in the response as metadata.taskID.
#
# Neither request_id nor task_id is stored on this instance — they are
# extracted per-request and passed as plain values to the Solicitor-General, 
# which calls generate_message_ids() to produce the authoritative 
# (correlation_id, task_id) pair that seeds YoAiContext for the life of the request.
#
# Response shape (valid JSON-RPC 2.0 AND valid A2A v1.0):
#   {
#     "jsonrpc": "2.0",
#     "id": "<request_id>",
#     "method": "a2a.message",
#     "result": { ... },
#     "metadata": {
#       "taskID": "<task_id>",
#       "status": "completed" | "failed"
#     }
#   }

from datetime import datetime, timezone


class A2ATransport:

    def __init__(self, solicitor_general, logger, validator):
        self._sg        = solicitor_general
        self._logger    = logger
        self._validator = validator

    async def handle_a2a(self, envelope: dict) -> dict:

        # ── 0. Extract protocol identifiers at the boundary ────────────────
        request_id = envelope.get("id")

        params   = envelope.get("params") or {}
        metadata = params.get("metadata") or {}
        task_id  = metadata.get("taskID") or request_id

        # ── 1. Mandatory-but-non-blocking validation ───────────────────────
        validation_info = self._run_validation(envelope)
        self._logger.info("a2a.validation", extra={
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "task_id":    task_id,
            "validation": validation_info,
        })

        # ── 2. Guard: request_id required ─────────────────────────────────
        # Do NOT call SG without a request_id — we have nothing to correlate.
        # Returns a null-id JSON-RPC error; no A2A metadata since we have no
        # task_id to return either.
        if request_id is None:
            self._logger.error("a2a.missing_request_id", extra={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "envelope":  envelope,
            })
            return {
                "jsonrpc": "2.0",
                "id":      None,
                "method":  "a2a.message",
                "error": {
                    "code":    -32603,
                    "message": "Missing request_id (JSON-RPC id)",
                },
                "metadata": {
                    "taskID": None,
                    "status": "failed",
                },
            }

        # ── 3. Hand off to SG (semantic boundary) ─────────────────────────
        # route_a2a() calls _build_context(envelope) internally, which calls
        # generate_message_ids(request_id=request_id) to produce the
        # authoritative (correlation_id, task_id) pair that seeds YoAiContext.
        # The transport does not build or store any context.
        try:
            semantic_result = await self._sg.route_a2a(envelope)
        except Exception as e:
            self._logger.error("a2a.transport_error", extra={
                "timestamp":  datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "task_id":    task_id,
                "error":      str(e),
                "envelope":   envelope,
            })
            return self._build_response(
                request_id=request_id,
                task_id=task_id,
                result=None,
                error={"code": -32603, "message": str(e)},
                status="failed",
            )

        # ── 4. Wrap in valid JSON-RPC 2.0 + A2A v1.0 response ─────────────
        return self._build_response(
            request_id=request_id,
            task_id=task_id,
            result=semantic_result,
            status="completed",
        )

    # ── Response builder ───────────────────────────────────────────────────

    def _build_response(
        self,
        *,
        request_id,
        task_id,
        result: dict | None = None,
        error: dict | None = None,
        status: str = "completed",
    ) -> dict:
        # ── JSON-RPC 2.0 + A2A v1.0 — fields are additive, no conflict ────
        response = {
            "jsonrpc": "2.0",
            "id":      request_id,
            "method":  "a2a.message",
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

    # ── Mandatory-but-non-blocking validation ──────────────────────────────

    def _run_validation(self, envelope: dict) -> dict:
        # ── Never raises — always returns structured info ──────────────────
        # Validation failures are non-blocking: request proceeds regardless,
        # errors captured in info payload for logging.
        info = {"v1_0_valid": False, "errors": []}
        try:
            info["v1_0_valid"] = self._validator.validate_request(envelope)
        except Exception:
            pass
        if not info["v1_0_valid"]:
            try:
                info["errors"] = self._validator.get_validation_errors(envelope, "request")
            except Exception:
                info["errors"] = ["validation failed unexpectedly"]
        return info
