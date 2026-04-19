# core/handlers/yo_ai_handler.py
#
# Universal Lambda / HTTP entrypoint for the Yo-ai Platform.
#
# Module-level singletons constructed once per Lambda execution environment,
# reused across warm invocations. Construction order matters:
#   1. PlatformEventBus          — in-process pub/sub for PlatformAgents
#   2. capability_map             — loaded from shared/artifacts/capability_map.yaml
#   3. SolicitorGeneralAgent      — requires event_bus + capability_map
#   4. YoAiRuntime                — requires capability_map
#   5. A2AValidator               — independent, no dependencies
#   6. A2ATransport               — requires SG + validator + logger
#
# Capability Map:
#   /shared/artifacts/capability_map.yaml is the single source of truth for
#   all platform capabilities and routes. Both this handler and api_handler.py
#   load from the same file — no capability paths are hard-coded in either.
#
# Logging:
#   A2ATransport calls self._logger.info() / self._logger.error() with extra=.
#   LogBootstrapper exposes write(dict) only.
#   _TransportLoggerAdapter bridges the two without modifying either class.

import json
from pathlib import Path

import yaml

from core.routing.a2a_transport import A2ATransport
from core.routing.yo_ai_runtime import YoAiRuntime       # was incorrectly self-importing
from core.messages.a2a_validator import A2AValidator
from core.platform_agent import PlatformEventBus
from core.observability.logging.log_bootstrapper import get_logger
from agents.solicitor_general.runtime.solicitor_general import SolicitorGeneralAgent


# ── Transport logger adapter ───────────────────────────────────────────────
# A2ATransport expects .info() / .error() with extra= kwargs.
# LogBootstrapper exposes write(dict) only.
# This adapter bridges the two without modifying either class.

class _TransportLoggerAdapter:

    def __init__(self, bootstrapper):
        self._log = bootstrapper

    def info(self, event_type: str, extra: dict = None):
        self._log.write({
            "event_type": event_type,
            "level":      "INFO",
            "payload":    extra or {},
        })

    def error(self, event_type: str, extra: dict = None):
        self._log.write({
            "event_type": event_type,
            "level":      "ERROR",
            "payload":    extra or {},
        })


# ── Shared capability map loader ───────────────────────────────────────────

def _load_capability_map() -> dict:
    # ── Loads from shared/artifacts/capability_map.yaml ───────────────────
    # Returns {} on any failure — the SG surfaces Unknown capability errors
    # per request rather than crashing on cold start.
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


# ── Module-level singletons ────────────────────────────────────────────────

# 1. Platform event bus
_event_bus = PlatformEventBus()

# 2. Capability map
_capability_map = _load_capability_map()

# 3. SolicitorGeneralAgent — requires event_bus and capability_map.
#    slim=False: full governance init (tools, fingerprints, knowledge).
#    This is the platform routing path — full governance required.
_sg = SolicitorGeneralAgent(
    event_bus=_event_bus,
    capability_map=_capability_map,
)

# 4. YoAiRuntime — semantic routing spine.
#    tools={}: RPC adapters injected at platform bootstrap (not at handler init).
_runtime = YoAiRuntime(
    capability_map=_capability_map,
    tools={},
)

# 5. Transport logger
_logger_transport_raw = get_logger("transport")
_logger_transport     = _TransportLoggerAdapter(_logger_transport_raw)

# 6. Validator
_validator = A2AValidator()

# 7. Transport — requires SG, not runtime directly.
#    A2ATransport.__init__ signature: (solicitor_general, logger, validator)
_transport = A2ATransport(
    solicitor_general=_sg,
    logger=_logger_transport,
    validator=_validator,
)


# ── Agent directory ────────────────────────────────────────────────────────
# Canonical agent card lives at the PrivacyPortfolio Agent Directory.
# Published on the website — not maintained in this codebase.
# A2A callers fetch it directly from this URL.

AGENT_DIRECTORY_URL = "https://privacyportfolio.com/.well-known/agent.json"

_ROUTES = {
    "/":                            "landing",
    "/.well-known/agent-card.json": "redirect → AGENT_DIRECTORY_URL",
    "/a2a":                         "Mode 1 — A2A envelope → A2ATransport",
    "/agent/extended":              "stub → showCard() for authenticated callers (future)",
}


# ── Envelope extraction ────────────────────────────────────────────────────

def _extract_envelope(event) -> dict | None:
    # ── Handles three inbound shapes ──────────────────────────────────────
    # API Gateway proxy ("a2a" / "api"): dict with "body" key (JSON string)
    # Direct dict invocation (tests, "mesh"): already a well-formed envelope
    # Starlette Request ("app"): has async .json() — returns None as sentinel
    if isinstance(event, dict):
        body = event.get("body")
        if body is not None:
            try:
                return json.loads(body) if isinstance(body, str) else body
            except json.JSONDecodeError as e:
                return {
                    "jsonrpc": "2.0",
                    "id":      None,
                    "error":   {"code": -32700, "message": f"Parse error: {e}"},
                }
        return event   # direct dict — treat as envelope
    return None        # Starlette Request or unknown — signal for async handling


# ── Lambda / HTTP entrypoint ───────────────────────────────────────────────

async def yo_ai_handler(event, context=None):
    # ── Handles startup modes "a2a" and "app" ─────────────────────────────
    # For "api" (API Gateway OpenAPI paths) use api_handler.py, which wraps
    # the request in an A2A-compliant envelope before calling A2ATransport.

    # ── Non-A2A path routing ───────────────────────────────────────────────
    if isinstance(event, dict):
        raw_path = event.get("rawPath", "") or event.get("path", "")

        if raw_path == "/.well-known/agent-card.json":
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

        if raw_path == "/agent/extended":
            return {
                "statusCode": 501,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error":   "not_implemented",
                    "message": f"{raw_path} is not yet wired to a Door-Keeper capability.",
                    "route":   raw_path,
                }),
            }

    # ── Envelope extraction ────────────────────────────────────────────────
    envelope = _extract_envelope(event)

    if envelope is None:
        if hasattr(event, "json"):
            # Starlette Request — async body read required
            try:
                envelope = await event.json()
            except Exception as e:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "jsonrpc": "2.0",
                        "id":      None,
                        "error":   {"code": -32700, "message": f"Parse error: {e}"},
                    }),
                }
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "jsonrpc": "2.0",
                    "id":      None,
                    "error":   {"code": -32600, "message": "Unrecognised request format"},
                }),
            }

    # ── Delegate to transport ──────────────────────────────────────────────
    response = await _transport.handle_a2a(envelope)

    # ── Shape response for Lambda proxy integration ────────────────────────
    # API Gateway proxy expects statusCode + body.
    # Starlette / direct invocation receives the raw response dict.
    if isinstance(event, dict) and "requestContext" in event:
        status_code = 200 if "error" not in response else 400
        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response),
        }

    return response
