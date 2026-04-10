# core/handlers/yo_ai_handler.py

"""
Universal Lambda / HTTP entrypoint for the Yo-ai Platform.

This is the recommended front door for ALL agents on the platform.

Module-level singletons are constructed once per Lambda execution environment
and reused across warm invocations. Construction order matters:
  1. PlatformEventBus       — in-process pub/sub for PlatformAgents
  2. capability_map          — loaded from shared/artifacts/capability_map.yaml
  3. SolicitorGeneralAgent   — requires event_bus + capability_map
  4. A2AValidator            — independent, no dependencies
  5. A2ATransport            — requires SG + validator + logger

Capability Map:
  The shared capability map at /shared/artifacts/capability_map.yaml is the
  single source of truth for all platform capabilities and routes. It is
  read/write accessible to all agents. Both this handler and api_handler.py
  load from the same file — no capability paths are hard-coded in either.

Logging:
  A2ATransport uses LogBootstrapper.write(dict) — the platform standard.
  It does NOT use stdlib logger.info() / logger.error().
  The _TransportLoggerAdapter bridges the two interfaces without modifying
  either A2ATransport or LogBootstrapper.
"""

import json
from pathlib import Path

import yaml

from core.routing.a2a_transport import A2ATransport
from core.messages.a2a_validator import A2AValidator
from core.routing import load_capability_map, load_tools
from core.handlers.yo_ai_handler import YoAiRuntime
from core.platform_agent import PlatformEventBus
from core.observability.logging.log_bootstrapper import get_logger


# ---------------------------------------------------------------------------
# Transport logger adapter
# ---------------------------------------------------------------------------
# A2ATransport calls self._logger.info(...) and self._logger.error(...) with
# extra= keyword arguments. LogBootstrapper exposes write(dict) only.
# This adapter bridges the two interfaces without modifying either class.

class _TransportLoggerAdapter:
    """
    Adapts LogBootstrapper.write(dict) to the .info() / .error() interface
    that A2ATransport expects. Translates stdlib-style calls into structured
    platform log records.
    """

    def __init__(self, bootstrapper):
        self._log = bootstrapper

    def info(self, event_type: str, extra: dict = None):
        self._log.write({
            "event_type": event_type,
            "level": "INFO",
            "message": event_type,
            "payload": extra or {},
        })

    def error(self, event_type: str, extra: dict = None):
        self._log.write({
            "event_type": event_type,
            "level": "ERROR",
            "message": event_type,
            "payload": extra or {},
        })


# ---------------------------------------------------------------------------
# Shared capability map loader
# ---------------------------------------------------------------------------

def _load_capability_map() -> dict:
    """
    Load the platform capability map from the shared artifacts location:
      /shared/artifacts/capability_map.yaml

    This is the single source of truth for all platform capabilities,
    routes, and constructors. Both yo_ai_handler.py and api_handler.py
    load from this file.

    Returns {} on any failure — the SG will surface Unknown capability
    errors per request rather than crashing on cold start.
    """
    try:
        map_path = (
            Path(__file__).resolve().parent.parent
            / "shared" / "artifacts" / "capability_map.yaml"
        )
        if not map_path.exists():
            print(f"[yo_ai_handler] WARNING: capability_map.yaml not found at {map_path}")
            return {}

        with map_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    except Exception as e:
        print(f"[yo_ai_handler] WARNING: capability_map.yaml failed to load: {e}")
        return {}


# ---------------------------------------------------------------------------
# Module-level singletons
# One set per Lambda execution environment — reused across warm invocations.
# ---------------------------------------------------------------------------

# 1. Platform event bus — in-process pub/sub for PlatformAgents
_event_bus = PlatformEventBus()

# 2. Capability map — single source of truth from shared/artifacts/
_capability_map = _load_capability_map()

# 3. Loggers
_logger_transport_raw = get_logger("transport")
_logger_transport = _TransportLoggerAdapter(_logger_transport_raw)

# 4. YoAiRuntime
#    tools required for bridging transport modes to agent capabilities
#    capability_map drives all semantic routing decisions.
_runtime = YoAiRuntime(
    capability_map=load_capability_map(),
    tools=load_tools(),
)

# 5. Validator
_validator = A2AValidator()

# 6. Transport
_transport = A2ATransport(
    runtime=_runtime,
    logger=_logger_transport,
    validator=_validator,
)

# ---------------------------------------------------------------------------
# Agent directory
# ---------------------------------------------------------------------------
# The canonical agent card lives at the PrivacyPortfolio Agent Directory.
# It is published on the website and maintained there — not in this codebase.
# Any route that would serve agent card content redirects here instead.
#
# A2A callers that need the card fetch it directly from this URL.
# No local copy is kept — updating the website is the only deployment needed.

AGENT_DIRECTORY_URL = "https://privacyportfolio.com/.well-known/agent.json"

# Routes served by this handler.
# Entry Point (/a2a) and Entry Point (/app) are the primary paths.
# The remaining routes are thin — they either redirect or stub identity
# endpoints that will eventually route through other agent capabilities.
_ROUTES = {
    "/":                          "landing",
    "/.well-known/agent-card.json": "redirect → AGENT_DIRECTORY_URL",
    "/a2a":                        "Mode 1 — A2A envelope → A2ATransport",
    "/agent/extended":             "stub → showCard() for authenticated callers (future)",
}

# ---------------------------------------------------------------------------
# Envelope extraction
# ---------------------------------------------------------------------------

def _extract_envelope(event) -> dict | None:
    """
    Extract a JSON-RPC envelope from the inbound event regardless of
    how the Lambda was invoked.

    Handles two shapes:
      - API Gateway Lambda proxy event dict ("a2a" / "api"):
        event is a plain dict with a "body" key containing a JSON string.

      - Direct dict invocation (tests, scripts, "mesh"):
        event is already a well-formed envelope dict (no "body" wrapper).

      - Starlette / FastAPI Request object ("app"):
        event has an async .json() method — returns None as sentinel
        for async handling in yo_ai_handler().
    """
    if isinstance(event, dict):
        body = event.get("body")
        if body is not None:
            # API Gateway proxy — body is a JSON string
            try:
                return json.loads(body) if isinstance(body, str) else body
            except json.JSONDecodeError as e:
                return {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
        # Direct dict — treat as envelope already
        return event

    # Starlette Request or unknown — signal for async handling
    return None


# ---------------------------------------------------------------------------
# Lambda / HTTP entrypoint
# ---------------------------------------------------------------------------

async def yo_ai_handler(event, context=None):
    """
    Universal Lambda / HTTP entrypoint for the Yo-ai Platform.

    Handles all startup modes that arrive at this handler:
      "a2a" — API Gateway HTTP proxy event (dict with "body" key)
      "app" — Starlette / FastAPI Request object (has async .json())

    For "api" (API Gateway OpenAPI paths), use api_handler.py which wraps
    the request in an A2A-compliant envelope before calling A2ATransport.

    Args:
        event:   API Gateway Lambda proxy event dict, or a Starlette Request.
        context: Lambda context object (optional — not used directly).

    Returns:
        For Lambda proxy ("a2A"): API Gateway response dict with
            statusCode, headers, and JSON body.
        For Starlette ("app"): raw response dict from A2ATransport.
    """

    # --- Route non-A2A paths ---
    # Handle well-known card redirect and stub identity routes before
    # attempting envelope extraction. Only dict events with rawPath apply.
    if isinstance(event, dict):
        raw_path = event.get("rawPath", "") or event.get("path", "")

        if raw_path == "/.well-known/agent-card.json":
            # Redirect to the canonical Agent Directory — no local copy maintained.
            return {
                "statusCode": 301,
                "headers": {
                    "Location":      AGENT_DIRECTORY_URL,
                    "Cache-Control": "public, max-age=3600",
                },
                "body": "",
            }

        if raw_path == "/":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/plain"},
                "body": (
                    f"Yo-ai Platform — Solicitor-General\n"
                    f"Agent directory: {AGENT_DIRECTORY_URL}\n"
                    f"A2A endpoint:    POST /a2a\n"
                ),
            }

        if raw_path in ("/agent/extended"):
            # These will route through Door-Keeper capabilities when implemented.
            # Returning 501 (not 404) signals: endpoint is known, not yet wired.
            return {
                "statusCode": 501,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error":   "not_implemented",
                    "message": f"{raw_path} is not yet wired to a Door-Keeper capability.",
                    "route":   raw_path,
                }),
            }

    # --- Extract envelope ---
    envelope = _extract_envelope(event)

    if envelope is None:
        # Starlette Request object — async .json() required
        if hasattr(event, "json"):
            try:
                envelope = await event.json()
            except Exception as e:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {e}"},
                    }),
                }
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32600, "message": "Unrecognised request format"},
                }),
            }

    # --- Delegate to transport ---
    response = await _transport.handle_a2a(envelope)

    # --- Shape response for Lambda proxy integration ---
    # API Gateway proxy integration expects statusCode + body.
    # Starlette / direct invocation receives the raw response dict.
    if isinstance(event, dict) and "requestContext" in event:
        status_code = 200 if "error" not in response else 400
        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response),
        }

    # Starlette / direct — return response dict directly
    return response
