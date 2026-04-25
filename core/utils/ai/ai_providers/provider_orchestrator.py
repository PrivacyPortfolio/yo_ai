# core/utils/ai/ai_providers/provider_orchestrator.py
#
# ProviderOrchestrator — multi-provider coordination for AiClient.
#
# Used by: AiClient (ai_client.py) when strategy != "failover-simple"
# Not instantiated directly by agent code.

import time
from typing import Any, Dict, List, Optional, Tuple

from .provider_loader import load_ai_provider
from .base_ai_client import BaseAIClient
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("provider_orchestrator")


class ProviderOrchestrator:
    """
    Coordinates multiple AI providers for a single agent.

    Reads from the resolved declared_defaults list — the same list
    AiClient._pick_from_defaults() reads. Each entry has:
        { "role": "primary"|"failover", "provider": "...", "model": "..." }

    Supports two strategies:
        failover    — try providers in order, skip unhealthy ones
        round-robin — distribute calls across healthy providers

    Health is tracked in-memory per process/Lambda execution environment.
    Unhealthy providers are re-enabled after health_ttl_seconds.
    """

    def __init__(
        self,
        defaults: List[Dict[str, Any]],
        strategy: str = "failover",
        health_ttl_seconds: int = 300,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        """
        Args:
            defaults           : declared_defaults list from x-ai block.
                                 Each entry: {"role": ..., "provider": ..., "model": ...}
            strategy           : "failover" (default) or "round-robin"
            health_ttl_seconds : Seconds before an unhealthy provider is retried
            temperature        : Passed to all provider clients
            max_tokens         : Passed to all provider clients
        """
        if not defaults:
            raise ValueError("ProviderOrchestrator requires at least one entry in declared_defaults")

        self._defaults          = defaults
        self.strategy           = strategy
        self.health_ttl_seconds = health_ttl_seconds
        self.temperature        = temperature
        self.max_tokens         = max_tokens

        # In-memory health + round-robin state (per Lambda execution environment)
        self._health_cache: Dict[int, Dict[str, Any]] = {}
        self._rr_index: int = 0

    def chat_completion(
        self,
        system: str,
        user: str,
        capability_id: Optional[str] = None,
    ) -> str:
        """
        Execute a chat completion using the configured strategy.
        Never raises — returns error string if all providers fail.
        """
        try:
            if self.strategy == "round-robin":
                return self._round_robin(system, user, capability_id)
            return self._failover(system, user, capability_id)
        except RuntimeError as exc:
            LOG.error("ProviderOrchestrator: all providers exhausted — %s", exc)
            return f'{{"error": "ProviderOrchestrator: {exc}"}}'

    # ------------------------------------------------------------------
    # Strategy: failover
    # ------------------------------------------------------------------

    def _failover(
        self,
        system: str,
        user: str,
        capability_id: Optional[str],
    ) -> str:
        last_error: Optional[Exception] = None

        for idx, entry in enumerate(self._defaults):
            if not self._is_healthy(idx):
                LOG.info(
                    "ProviderOrchestrator: skipping unhealthy provider idx=%d (%s/%s)",
                    idx, entry.get("provider"), entry.get("model")
                )
                continue

            provider, model = entry.get("provider", ""), entry.get("model", "")
            if not provider or not model:
                LOG.warning("ProviderOrchestrator: skipping entry idx=%d — missing provider or model", idx)
                continue

            try:
                client = self._build_client(provider, model)
                LOG.info(
                    "ProviderOrchestrator: [failover] idx=%d %s/%s capability=%s",
                    idx, provider, model, capability_id or "none"
                )
                result = client.chat_completion(system, user, capability_id)
                self._mark_healthy(idx)
                return result

            except Exception as exc:
                LOG.warning(
                    "ProviderOrchestrator: idx=%d %s/%s failed — %s",
                    idx, provider, model, exc
                )
                self._mark_unhealthy(idx)
                last_error = exc

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    # ------------------------------------------------------------------
    # Strategy: round-robin
    # ------------------------------------------------------------------

    def _round_robin(
        self,
        system: str,
        user: str,
        capability_id: Optional[str],
    ) -> str:
        total      = len(self._defaults)
        attempts   = 0
        last_error: Optional[Exception] = None

        while attempts < total:
            idx = self._rr_index % total
            self._rr_index += 1
            attempts += 1

            if not self._is_healthy(idx):
                LOG.info(
                    "ProviderOrchestrator: [rr] skipping unhealthy idx=%d", idx
                )
                continue

            entry = self._defaults[idx]
            provider, model = entry.get("provider", ""), entry.get("model", "")
            if not provider or not model:
                continue

            try:
                client = self._build_client(provider, model)
                LOG.info(
                    "ProviderOrchestrator: [rr] idx=%d %s/%s capability=%s",
                    idx, provider, model, capability_id or "none"
                )
                result = client.chat_completion(system, user, capability_id)
                self._mark_healthy(idx)
                return result

            except Exception as exc:
                LOG.warning(
                    "ProviderOrchestrator: [rr] idx=%d %s/%s failed — %s",
                    idx, provider, model, exc
                )
                self._mark_unhealthy(idx)
                last_error = exc

        raise RuntimeError(f"All providers failed (round-robin). Last error: {last_error}")

    # ------------------------------------------------------------------
    # Health tracking — preserved exactly from original
    # ------------------------------------------------------------------

    def _is_healthy(self, idx: int) -> bool:
        entry = self._health_cache.get(idx)
        if not entry:
            return True                         # no history → assume healthy
        if entry.get("healthy", True):
            return True
        # Unhealthy — check if TTL has expired
        if (time.time() - entry.get("timestamp", 0)) > self.health_ttl_seconds:
            LOG.info(
                "ProviderOrchestrator: health TTL expired for idx=%d — re-enabling", idx
            )
            return True
        return False

    def _mark_unhealthy(self, idx: int) -> None:
        self._health_cache[idx] = {"healthy": False, "timestamp": time.time()}

    def _mark_healthy(self, idx: int) -> None:
        self._health_cache[idx] = {"healthy": True, "timestamp": time.time()}

    # ------------------------------------------------------------------
    # Client construction
    # ------------------------------------------------------------------

    def _build_client(self, provider: str, model: str) -> BaseAIClient:
        """Instantiate a provider client via provider_loader."""
        return load_ai_provider(
            provider=provider,
            model=model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
