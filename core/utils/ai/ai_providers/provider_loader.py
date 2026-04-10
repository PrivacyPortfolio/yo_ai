# core/utils/ai/ai_providers/provider_loader.py
#
# Provider factory — turns (provider, model) → BaseAIClient instance.
#
# Merge changes from original:
#   - api_key_env removed from config requirement. The original required
#     api_key_env in the config dict and raised if absent. This is
#     incompatible with the API_KEYS.docx ruling: api_key_env must NOT
#     appear in publishable agent cards. API keys are read from environment
#     variables by convention — the provider name determines which var.
#   - endpoint removed from config for OpenAI and Claude — SDK clients
#     don't need it; the SDK handles endpoint routing internally.
#   - temperature and max_tokens accepted from config (preserved from original).
#   - Azure deployment read from config (not sensitive — not a secret).
#   - Gemini (Google) added to match ai_client.py provider coverage.
#   - Provider name normalisation: "anthropic", "azure-openai", "azure",
#     "openai", "gemini", "google_gemini" all handled.
#
# Called by: AiClient._get_client() in ai_client.py
# Not called directly by agent code.

import logging
from typing import Optional

from .base_ai_client import BaseAIClient
from .claude_client import ClaudeClient
from .openai_client import OpenAIClient
from .azure_openai_client import AzureOpenAIClient

logger = logging.getLogger(__name__)


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
        azure       → AZURE_OPENAI_KEY + AZURE_OPENAI_ENDPOINT
        gemini      → GEMINI_API_KEY

    Args:
        provider    : Provider name (case-insensitive).
                      Accepted: "anthropic", "openai", "azure-openai",
                      "azure", "gemini", "google_gemini"
        model       : Model name (e.g. "claude-sonnet-4-6", "gpt-4o")
        temperature : Sampling temperature (default 0.2)
        max_tokens  : Max response tokens (default 2048)
        deployment  : Azure deployment name (required for azure providers)
        api_version : Azure API version (default "2024-02-01")

    Returns:
        Instantiated BaseAIClient subclass.

    Raises:
        ValueError if provider is unknown or azure deployment is missing.
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

    if p in ("azure_openai", "azure"):
        if not deployment:
            raise ValueError(
                f"Azure OpenAI provider requires 'deployment' — got none for model '{model}'"
            )
        return AzureOpenAIClient(
            model=model,
            deployment=deployment,
            temperature=temperature,
            max_tokens=max_tokens,
            api_version=api_version,
        )

    if p in ("gemini", "google_gemini"):
        return _GeminiClient(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(
        f"Unknown AI provider: '{provider}'. "
        f"Accepted: anthropic, openai, azure-openai, gemini."
    )


# ---------------------------------------------------------------------------
# GeminiClient — inline, thin wrapper (no separate file needed)
# ---------------------------------------------------------------------------

class _GeminiClient(BaseAIClient):
    """
    Google Gemini client via google-generativeai SDK.
    Inline in provider_loader — no separate file needed for a thin wrapper.
    API key read from GEMINI_API_KEY environment variable.
    """

    def __init__(self, model: str, temperature: float = 0.2, max_tokens: int = 2048):
        super().__init__(model, temperature, max_tokens)

    def chat_completion(
        self,
        system: str,
        user: str,
        capability_id: Optional[str] = None,
    ) -> str:
        import os
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            m = genai.GenerativeModel(
                self.model,
                system_instruction=system,
            )
            response = m.generate_content(
                user,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                ),
            )
            return response.text
        except KeyError:
            err = "GeminiClient: GEMINI_API_KEY environment variable not set."
            logger.error(err)
            return f'{{"error": "{err}"}}'
        except Exception as exc:
            err = f"GeminiClient: {self.model} failed — {exc}"
            logger.error(err)
            return f'{{"error": "{err}"}}'
