# core/utils/ai/ai_providers/provider_loader.py
#
# Provider factory — turns (provider, model) → BaseAIClient instance.
#
# Called by: AiClient._get_client() in ai_client.py
# Not called directly by agent code.

from typing import Optional

from .base_ai_client import BaseAIClient
from .claude_client import ClaudeClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient   # <-- NEW: external Gemini module
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("provider_loader")


def load_ai_provider(
    provider: str,
    model: str,
    temperature: float = 0.2,
    max_tokens: int = 2048,
    deployment: Optional[str] = None,
    api_version: str = "2024-02-01",
) -> BaseAIClient:
    """
    Instantiate a BaseAIClient for the given provider and model.

    API keys are NOT passed through this function — each client reads
    its key from the appropriate environment variable by convention:
        anthropic   → ANTHROPIC_API_KEY
        openai      → OPENAI_API_KEY
        gemini      → GEMINI_API_KEY

    Args:
        provider    : Provider name (case-insensitive).
                      Accepted: "anthropic", "openai", "gemini", "google_gemini"
        model       : Model name (e.g. "claude-sonnet-4-6", "gpt-4o")
        temperature : Sampling temperature (default 0.2)
        max_tokens  : Max response tokens (default 2048)

    Returns:
        Instantiated BaseAIClient subclass.

    Raises:
        ValueError if provider is unknown.
    """
    p = provider.lower().replace("-", "_")

    if p == "anthropic":
        return ClaudeClient(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if p == "openai":
        return OpenAIClient(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if p in ("gemini", "google_gemini"):
        return GeminiClient(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(
        f"Unknown AI provider: '{provider}'. "
        f"Accepted: anthropic, openai, gemini."
    )
