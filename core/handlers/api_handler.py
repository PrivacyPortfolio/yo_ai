# core/handlers/api_handler.py

"""
Mode 3: API Gateway entrypoint.

Wraps an API Gateway / OpenAPI request into an A2A-compliant JSON-RPC envelope
before passing it to A2ATransport. This ensures AgentContext is always built
from a well-formed envelope regardless of how the request arrived.

Responsibilities:
  - Load the platform capability map from /shared/artifacts/capability_map.yaml
  - Extract capability name from the API Gateway path, mapped via the shared
    capability map's routes section
  - Extract caller identity from API Gateway authorizer context
  - Extract correlation ID from API Gateway request ID
  - Wrap payload in a JSON-RPC 2.0 / A2A v1.0 envelope
  - Delegate to A2ATransport (full pipeline: validation → SG → UCR)
  - Unwrap the JSON-RPC response back to a plain HTTP response body

This handler does NOT bypass A2ATransport or the Solicitor-General.
All routing, AgentContext construction, and governance flow through
the standard pipeline unchanged.

Capability Map:
  The shared capability map at /shared/artifacts/capability_map.yaml is the
  single source of truth for all platform capabilities and routes. It is
  read/write accessible to all agents. Adding a new capability to the YAML
  automatically makes it available to both this handler and yo_ai_handler.py
  with no code changes needed.

Route convention (API Gateway):
  POST /agents/{agentName}/{capabilityPath}
  e.g. POST /agents/solicitorGeneral/justAsk
       POST /agents/dataSteward/dataRequestGovern

  The capabilityPath segment (camelCase) is mapped to a canonical A2A
  capability name via the routes section of each agent's registered card,
  which is reflected in capability_map.yaml.
"""

import json
import uuid
from pathlib import Path

import yaml

from core.routing.a2a_transport import A2ATransport


# ---------------------------------------------------------------------------
# Shared capability map loader
# ---------------------------------------------------------------------------

def _load_capability_path_map() -> dict[str, str]:
    """
    Load the API Gateway path → A2A capability name mapping from the shared
    capability map at /shared/artifacts/capability_map.yaml.

    The map is built from each agent's declared routes:
      routes:
        - path: /agents/solicitorGeneral/justAsk
          capability: Just-Ask
        - path: /agents/purchasingAgent/budgetCheck
          capability: Budget.Check

    The path segment after the agent name (e.g. 'justAsk', 'budgetCheck')
    is used as the lookup key. The canonical A2A capability name is the value.

    Returns {} on any failure — parse_api_gateway_request() will return a
    clear error for unrecognised paths.
    """
    try:
        map_path = Path(__file__).resolve().parent.parent / "shared" / "artifacts" / "capability_map.yaml"
        if not map_path.exists():
            print(f"[api_handler] WARNING: capability_map.yaml not found at {map_path}")
            return {}

        with map_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        # Build path_segment → capability_name lookup from all agents' routes
        path_map: dict[str, str] = {}

        for agent_routes in raw.get("routes", {}).values():
            for route in agent_routes:
                path = route.get("path", "")
                capability = route.get("capability", "")
                if path and capability:
                    # Extract the last path segment as the lookup key
                    # e.g. "/agents/solicitorGeneral/justAsk" → "justAsk"
                    segment = path.rstrip("/").split("/")[-1]
                    if segment:
                        path_map[segment] = capability

        # Also support a flat path_map section for direct overrides
        path_map.update(raw.get("path_map", {}))

        return path_map

    except Exception as e:
        print(f"[api_handler] WARNING: capability_map.yaml failed to load: {e}")
        return {}


# ---------------------------------------------------------------------------
# Module-level capability path map
# Loaded once per Lambda execution environment.
# ---------------------------------------------------------------------------

_CAPABILITY_PATH_MAP: dict[str, str] = _load_capability_path_map()


# ---------------------------------------------------------------------------
# Envelope builder
# ---------------------------------------------------------------------------

def build_a2a_envelope(
    *,
    capability_name: str,
    payload: dict,
    caller: dict | None,
    subject: dict | None,
    governance_labels: list[str],
    correlation_id: str,
) -> dict:
    """
    Wrap a plain API payload into an A2A v1.0 JSON-RPC envelope.

    Shape produced:
      {
        "jsonrpc": "2.0",
        "id": "<correlation_id>",
        "method": "a2a.message",
        "params": {
          "caller": { ... },
          "subject": { ... },
          "message": {
            "<capability_name>": { ...payload... }
          }
        }
      }

    Note: governanceLabels are NOT included in the outbound envelope params.
    Governance labels are platform-assigned on responses only — they are
    never set on inbound requests.
    """
    return {
        "jsonrpc": "2.0",
        "id": correlation_id,
        "method": "a2a.message",
        "params": {
            "caller": caller,
            "subject": subject,
            "message": {
                capability_name: payload,
            },
        },
    }


# ---------------------------------------------------------------------------
# API Gateway request parser
# ---------------------------------------------------------------------------

def parse_api_gateway_request(
    event: dict,
) -> tuple[str, dict, dict | None, dict | None, list[str], str]:
    """
    Extract semantic fields from an API Gateway Lambda proxy event.

    Returns:
      (capability_name, payload, caller, subject, governance_labels, correlation_id)

    Raises:
      ValueError if the capability path is unrecognised or body is missing.
    """
    # Capability name from path parameters
    path_params = event.get("pathParameters") or {}
    capability_path = path_params.get("capabilityPath")

    if not capability_path:
        raise ValueError("Missing path parameter: capabilityPath")

    capability_name = _CAPABILITY_PATH_MAP.get(capability_path)
    if not capability_name:
        raise ValueError(
            f"Unrecognised capability path: '{capability_path}'. "
            f"Known paths: {sorted(_CAPABILITY_PATH_MAP.keys())}"
        )

    # Payload from request body
    raw_body = event.get("body") or "{}"
    try:
        payload = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON body: {e}")

    # Caller identity from API Gateway authorizer context
    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}

    caller = {
        "agent_id": authorizer.get("agentId"),
        "subscriber_id": authorizer.get("subscriberId"),
        "principal_id": authorizer.get("principalId"),
    } if authorizer else None

    # Subject from body (optional — caller may equal subject)
    subject = payload.pop("subject", None)

    # Governance labels: empty on inbound — platform-assigned on responses only
    governance_labels: list[str] = []

    # Correlation ID from API Gateway request ID
    correlation_id = (
        request_context.get("requestId")
        or event.get("correlationId")
        or str(uuid.uuid4())
    )

    return capability_name, payload, caller, subject, governance_labels, correlation_id


# ---------------------------------------------------------------------------
# Mode 3 entrypoint
# ---------------------------------------------------------------------------

async def api_handler(event: dict, transport: A2ATransport) -> dict:
    """
    API Gateway / OpenAPI Lambda entrypoint (Mode 3).

    Parses the API Gateway event, wraps it in an A2A-compliant JSON-RPC
    envelope, and delegates to A2ATransport. Returns a plain HTTP response
    dict suitable for API Gateway Lambda proxy integration.

    The capability map is loaded from /shared/artifacts/capability_map.yaml —
    the single platform source of truth for capabilities and routes. No
    capability paths are hard-coded in this file.

    Args:
      event:      API Gateway Lambda proxy event dict
      transport:  Shared A2ATransport singleton (injected by the Lambda handler)

    Returns:
      API Gateway Lambda proxy response:
        { "statusCode": int, "body": str (JSON), "headers": dict }
    """
    try:
        capability_name, payload, caller, subject, governance_labels, correlation_id = \
            parse_api_gateway_request(event)
    except ValueError as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": f"Invalid API request: {e}",
                },
            }),
        }

    envelope = build_a2a_envelope(
        capability_name=capability_name,
        payload=payload,
        caller=caller,
        subject=subject,
        governance_labels=governance_labels,
        correlation_id=correlation_id,
    )

    # Full pipeline: A2ATransport → SG → UCR → agent capability handler
    result = await transport.handle_a2a(envelope)

    status_code = 400 if "error" in result else 200

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }
