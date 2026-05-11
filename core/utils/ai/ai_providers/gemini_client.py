# core/utils/ai/ai_providers/gemini_client.py
#
# GeminiClient — Google Gemini via official google-generativeai SDK.
#
#   - API key read from environment variable (never from config)
#   - model name kept as constructor arg (e.g., "gemini-pro")
#   - capability_id accepted per BaseAIClient contract
#   - temperature and max_tokens passed through
#   - Never raises — returns error JSON string on failure

import os
from typing import Optional

from .base_ai_client import BaseAIClient
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("gemini_client")

_API_KEY_ENV = "GEMINI_API_KEY"


class GeminiClient(BaseAIClient):
    """
    Google Gemini client using the official google-generativeai SDK.

    Constructed by provider_loader.py — not directly by agent code.

    API key is read from environment variables.
    Never passed through config or agent cards (API_KEYS.docx ruling).

    Args:
        model       : Gemini model name (e.g., "gemini-pro")
        temperature : Sampling temperature
        max_tokens  : Max response tokens
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        super().__init__(model, temperature, max_tokens)

    def chat_completion(
        self,
        system: str,
        user: str,
        capability_id: Optional[str] = None,
    ) -> str:
        """
        Execute a Gemini chat completion.
        Returns raw text. Never raises — returns error string on failure.
        """
        try:
            import google.generativeai as genai

            api_key = os.environ[_API_KEY_ENV]
            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(self.model)

            # Gemini uses a single "contents" list instead of role-based messages
            prompt = [
                {"role": "system", "parts": [{"text": system}]},
                {"role": "user",   "parts": [{"text": user}]},
            ]

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                },
            )

            return response.text

        except KeyError as exc:
            err = f"GeminiClient: required environment variable not set — {exc}"
            LOG.error(err)
            return f'{{"error": "{err}"}}'

        except Exception as exc:
            err = f"GeminiClient: {self.model} failed — {exc}"
            LOG.error(err)
            return f'{{"error": "{err}"}}'
