# core/utils/ai/ai_client.py
#
# AI client for Yo-ai agents. Constructed by YoAiAgent at init.
# Provides chat_completion(system, user, capability_id=None) for call_ai().
#
# Resolution order (env-first):
#   1. YO_AI_MODEL_<AGENT>_<SKILL>   e.g. YO_AI_MODEL_DOOR_KEEPER_TRUST_ASSIGN
#   2. YO_AI_MODEL_<AGENT>           e.g. YO_AI_MODEL_DOOR_KEEPER
#   3. x-ai.skills.<skill>.declared_defaults[role=primary]   (per-capability)
#   4. x-ai.declared_defaults[role=primary]                  (per-agent)
#   5. Platform fallback: anthropic / claude-sonnet-4-6
#
# Dispatch (merged from ai_providers/):
#   _invoke() → load_ai_provider() → BaseAIClient subclass (SDK-based)
#   Multiple declared_defaults → ProviderOrchestrator (health TTL + round-robin)
#   Single entry → direct dispatch (fast path)
#
# api_key_env / endpoint silently ignored (banned from publishable cards).

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from core.utils.ai.ai_providers.provider_loader import load_ai_provider
from core.utils.ai.ai_providers.provider_orchestrator import ProviderOrchestrator

logger = logging.getLogger(__name__)

_FALLBACK_PROVIDER = "anthropic"
_FALLBACK_MODEL    = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# AiClient
# ---------------------------------------------------------------------------

class AiClient:
    """
    AI client for a Yo-ai agent. Constructed once at agent init.

    Reads the agent's x-ai block (if present) for model preferences.
    All missing/partial configurations degrade to the platform fallback
    without raising.

    Usage in YoAiAgent.__init__():
        self.ai_client = AiClient(
            agent_name=self.name,
            xai_block=(self.extended or {}).get("x-ai"),
        )

    chat_completion() signature matches what call_ai() in ai_transform.py
    expects: chat_completion(system, user) → str
    capability_id is accepted as an optional kwarg for per-skill resolution.
    """

    def __init__(
        self,
        agent_name: str,
        xai_block: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.agent_name = agent_name
        # Normalise: always a dict internally, never None
        self._xai = xai_block if isinstance(xai_block, dict) else {}

        self._strategy    = self._xai.get("strategy", "failover")
        self._health_ttl  = int(self._xai.get("health_ttl_seconds", 300))
        self._temperature = float(self._xai.get("temperature", 0.2))
        self._max_tokens  = int(self._xai.get("max_tokens", 1024))

        if not self._xai:
            logger.debug(
                "AiClient(%s): no x-ai block — platform fallback %s/%s.",
                agent_name, _FALLBACK_PROVIDER, _FALLBACK_MODEL
            )
        elif "skills" in self._xai:
            logger.debug(
                "AiClient(%s): per-capability x-ai (%d skill(s)) strategy=%s.",
                agent_name, len(self._xai["skills"]), self._strategy
            )
        else:
            logger.debug(
                "AiClient(%s): per-agent x-ai strategy=%s.", agent_name, self._strategy
            )

    # ------------------------------------------------------------------
    # Public interface — called by call_ai() in ai_transform.py
    # ------------------------------------------------------------------

    def chat_completion(
        self,
        system: str,
        user: str,
        capability_id: Optional[str] = None,
    ) -> str:
        """
        Resolve model, call provider, return raw text response.

        capability_id is optional — when supplied enables per-skill
        model selection (Door-Keeper pattern). When absent falls through
        to per-agent or platform fallback.

        Never raises. Returns an error JSON string on total failure so
        call_ai() can wrap it in {"rawText": ...} cleanly.
        """
        defaults = self._get_defaults_for_capability(capability_id)

        # Single entry — direct dispatch (fast path, no orchestrator overhead)
        if len(defaults) <= 1:
            provider, model = self._resolve(capability_id, role="primary")
            logger.info(
                "AiClient(%s): %s/%s  capability=%s",
                self.agent_name, provider, model, capability_id or "none"
            )
            try:
                return _invoke(
                    provider, model, system, user, capability_id,
                    self._temperature, self._max_tokens,
                )
            except Exception as exc:
                logger.error(
                    "AiClient(%s): %s/%s failed — %s",
                    self.agent_name, provider, model, exc
                )
                return f'{{"error": "AiClient: {exc}"}}'

        # Multiple entries — ProviderOrchestrator (health TTL + strategy)
        orch = ProviderOrchestrator(
            defaults=defaults,
            strategy=self._strategy,
            health_ttl_seconds=self._health_ttl,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return orch.chat_completion(system, user, capability_id)

    # ------------------------------------------------------------------
    # Model resolution
    # ------------------------------------------------------------------

    def _get_defaults_for_capability(
        self, capability_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Return declared_defaults list for capability — per-skill first, per-agent fallback."""
        if capability_id and self._xai:
            skills = self._xai.get("skills")
            if isinstance(skills, dict):
                d = skills.get(capability_id, {}).get("declared_defaults")
                if isinstance(d, list) and d:
                    return d
        if self._xai:
            d = self._xai.get("declared_defaults")
            if isinstance(d, list) and d:
                return d
        return []

    def _resolve(
        self,
        capability_id: Optional[str],
        role: str = "primary",
    ) -> Tuple[str, str]:
        """
        Resolve provider + model for a given role ("primary" or "failover").
        Works through the full resolution chain — never raises.
        Always returns a valid (provider, model) tuple.
        """
        # 1. Per-skill env override
        if capability_id:
            env_key = _env_key(self.agent_name, capability_id)
            if env_key in os.environ:
                return _parse_model_string(os.environ[env_key])

        # 2. Per-agent env override
        agent_env_key = _env_key(self.agent_name)
        if agent_env_key in os.environ:
            return _parse_model_string(os.environ[agent_env_key])

        # 3. x-ai per-capability (x-ai.skills.<capability>.declared_defaults)
        if capability_id and self._xai:
            skills = self._xai.get("skills")
            if isinstance(skills, dict):
                skill_cfg = skills.get(capability_id, {})
                result = _pick_from_defaults(
                    skill_cfg.get("declared_defaults", []), role
                )
                if result:
                    return result

        # 4. x-ai per-agent (x-ai.declared_defaults flat list)
        if self._xai:
            result = _pick_from_defaults(
                self._xai.get("declared_defaults", []), role
            )
            if result:
                return result

        # 5. Platform fallback
        return _FALLBACK_PROVIDER, _FALLBACK_MODEL


# ---------------------------------------------------------------------------
# Helpers — resolution
# ---------------------------------------------------------------------------

def _env_key(*parts: str) -> str:
    """Build a YO_AI_MODEL_... env var key from agent name and optional skill."""
    return "YO_AI_MODEL_" + "_".join(
        re.sub(r"[^A-Z0-9]", "_", p.upper()) for p in parts
    )


def _parse_model_string(value: str) -> Tuple[str, str]:
    """
    Parse "provider/model" env var value.
    "anthropic/claude-opus-4-6" → ("anthropic", "claude-opus-4-6")
    "claude-opus-4-6"           → (_FALLBACK_PROVIDER, "claude-opus-4-6")
    """
    if "/" in value:
        provider, model = value.split("/", 1)
        return provider.strip(), model.strip()
    return _FALLBACK_PROVIDER, value.strip()


def _pick_from_defaults(
    defaults: List[Dict[str, Any]],
    role: str,
) -> Optional[Tuple[str, str]]:
    """
    Pick a provider+model from a declared_defaults list by role.

    Graceful degradation:
      - defaults is None or not a list  → None
      - empty list                       → None
      - no entry with matching role      → first entry (any role)
      - entry missing provider or model  → skipped
      - api_key_env / endpoint present   → silently ignored
    """
    if not defaults or not isinstance(defaults, list):
        return None

    # Try exact role match first
    for entry in defaults:
        if not isinstance(entry, dict):
            continue
        if entry.get("role") == role:
            provider = entry.get("provider", "").strip()
            model    = entry.get("model", "").strip()
            if provider and model:
                # api_key_env and endpoint silently ignored here
                return provider, model

    # Fall back to first valid entry regardless of role
    for entry in defaults:
        if not isinstance(entry, dict):
            continue
        provider = entry.get("provider", "").strip()
        model    = entry.get("model", "").strip()
        if provider and model:
            return provider, model

    return None


# ---------------------------------------------------------------------------
# LLM dispatch — via provider_loader + BaseAIClient subclasses
# (merged from core/runtime/ai_providers/)
# ---------------------------------------------------------------------------

def _invoke(
    provider: str,
    model: str,
    system: str,
    user: str,
    capability_id: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Instantiate the correct BaseAIClient subclass and call chat_completion().
    Raises on failure — callers wrap in try/except.
    """
    client = load_ai_provider(
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return client.chat_completion(system, user, capability_id)
