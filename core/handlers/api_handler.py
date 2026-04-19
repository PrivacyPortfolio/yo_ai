# core/handlers/api_handler.py
#
# Mode 3: API Gateway entrypoint.
#
# Wraps an API Gateway / OpenAPI request into an A2A-compliant JSON-RPC
# envelope before passing it to A2ATransport. This ensures YoAiContext is
# always built from a well-formed envelope regardless of how the request arrived.
#
# Responsibilities:
#   - Load the platform capability map from /shared/artifacts/capability_map.yaml
#   - Extract capability name from the API Gateway path via the capability map
#   - Extract caller identity from API Gateway authorizer context
#   - Extract correlation ID from API Gateway request ID
#   - Wrap payload in a JSON-RPC 2.0 / A2A v1.0 envelope
#   - Delegate to A2ATransport (full pipeline: validation → SG → UCR)
#   - Unwrap the JSON-RPC response back to a plain HTTP response body
#
# This handler does NOT bypass A2ATransport or the Solicitor-General.
# All routing, YoAiContext construction, and governance flow through the
# standard pipeline unchanged.
#
# Capability Map:
#   /shared/artifacts/capability_map.yaml is the single source of truth for
#   all platform capabilities and routes. Adding a new capability to the YAML
#   automatically makes it available here and in yo_ai_handler.py with no
#   code changes needed.
#
# Route convention (API Gateway):
#   POST /agents/{agentName}/{capabilityPath}
#   e.g. POST /agents/solicitorGeneral/justAsk
#        POST /agents/dataSteward/dataRequestGovern

import json
import uuid
from pathlib import Path

import yaml

from core.routing.a2a_transport import A2ATransport


# ── Shared capability map loader ───────────────────────────────────────────

def _load_capability_path_map() -> dict[str, str]:
    # ── path_segment → canonical capability name ───────────────────────────
    # Returns {} on any failure — parse_api_gateway_request() surfaces a
    # clear error for unrecognised paths rather than crashing on cold start.
    try:
        map_path = (
            Path(__file__).resolve().parent.parent
            / "shared" / "artifacts" / "capability_map.yaml"
        )
        if not map_path.exists():
            print(f"[api_handler] WARNING: capability_map.yaml not found at {map_path}")
            return {}

        with map_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        path_map: dict[str, str] = {}
        for agent_routes in raw.get("routes", {}).values():
            for route in agent_routes:
                path       = route.get("path", "")
                capability = route.get("capability", "")
                if path and capability:
                    segment = path.rstrip("/").split("/")[-1]
                    if segment:
                        path_map[segment] = capability

        path_map.update(raw.get("path_map", {}))
        return path_map

    except Exception as e:
        print(f"[api_handler] WARNING: capability_map.yaml failed to load: {e}")
        return {}


# ── Module-level capability path map ──────────────────────────────────────
# Loaded once per Lambda execution environment.

_CAPABILITY_PATH_MAP: dict[str, str] = _load_capability_path_map()


# ── Envelope builder ───────────────────────────────────────────────────────

def build_a2a_envelope(
    *,
    capability_name: str,
    payload: dict,
    caller: dict | None,
    subject: dict | None,
    correlation_id: str,
) -> dict:
    # ── JSON-RPC 2.0 / A2A v1.0 envelope ──────────────────────────────────
    # correlation_id becomes the JSON-RPC "id" field.
    # A2ATransport extracts it as request_id and passes it to
    # generate_message_ids() to seed YoAiContext.
    #
    # governance_labels are NOT included — they are platform-assigned on
    # responses only and must never appear on inbound requests.
    return {
        "jsonrpc": "2.0",
        "id":      correlation_id,
        "method":  "a2a.message",
        "params": {
            "caller":  caller,
            "subject": subject,
            "message": {
                capability_name: payload,
            },
        },
    }


# ── API Gateway request parser ─────────────────────────────────────────────

def parse_api_gateway_request(
    event: dict,
) -> tuple[str, dict, dict | None, dict | None, str]:
    # ── Returns (capability_name, payload, caller, subject, correlation_id) ─
    # Raises ValueError for unrecognised path or bad body.

    path_params      = event.get("pathParameters") or {}
    capability_path  = path_params.get("capabilityPath")

    if not capability_path:
        raise ValueError("Missing path parameter: capabilityPath")

    capability_name = _CAPABILITY_PATH_MAP.get(capability_path)
    if not capability_name:
        raise ValueError(
            f"Unrecognised capability path: '{capability_path}'. "
            f"Known paths: {sorted(_CAPABILITY_PATH_MAP.keys())}"
        )

    # ── Payload ───────────────────────────────────────────────────────────
    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON body: {e}")

    # ── Subject extracted without mutating body ────────────────────────────
    # payload.pop() mutates the caller's dict in place — use get() instead
    # and rebuild payload without the subject key.
    subject = body.get("subject")
    payload = {k: v for k, v in body.items() if k != "subject"}

    # ── Caller identity from API Gateway authorizer context ────────────────
    request_context = event.get("requestContext") or {}
    authorizer      = request_context.get("authorizer") or {}
    caller = {
        "agent_id":      authorizer.get("agentId"),
        "subscriber_id": authorizer.get("subscriberId"),
        "principal_id":  authorizer.get("principalId"),
    } if authorizer else None

    # ── Correlation ID — seeded from API Gateway request ID ────────────────
    # This becomes the JSON-RPC "id" field in the envelope.
    # A2ATransport extracts it as request_id; the SG calls
    # generate_message_ids(request_id=...) to produce the authoritative pair.
    correlation_id = (
        request_context.get("requestId")
        or event.get("correlationId")
        or str(uuid.uuid4())
    )

    return capability_name, payload, caller, subject, correlation_id


# ── Mode 3 entrypoint ─────────────────────────────────────────────────────

async def api_handler(event: dict, transport: A2ATransport) -> dict:
    # ── API Gateway / OpenAPI Lambda entrypoint (Mode 3) ──────────────────
    # Parses the API Gateway event, wraps it in an A2A-compliant JSON-RPC
    # envelope, and delegates to A2ATransport.

    try:
        capability_name, payload, caller, subject, correlation_id = \
            parse_api_gateway_request(event)
    except ValueError as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id":      None,
                "error": {
                    "code":    -32600,
                    "message": f"Invalid API request: {e}",
                },
            }),
        }

    envelope = build_a2a_envelope(
        capability_name=capability_name,
        payload=payload,
        caller=caller,
        subject=subject,
        correlation_id=correlation_id,
    )

    # ── Full pipeline: A2ATransport → SG → UCR → capability handler ───────
    result = await transport.handle_a2a(envelope)

    status_code = 400 if "error" in result else 200

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }
