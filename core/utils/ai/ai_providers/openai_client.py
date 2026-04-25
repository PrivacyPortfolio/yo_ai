# core/utils/ai/ai_providers/openai_client.py
#
# OpenAIClient — OpenAI-compatible API via official SDK.
#

import os
from typing import Optional

from .base_ai_client import BaseAIClient
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("openai_client")

_API_KEY_ENV = "OPENAI_API_KEY"


class OpenAIClient(BaseAIClient):
    """
    OpenAI-compatible client using the official openai SDK.

    Constructed by provider_loader.py — not directly by agent code.

    API key is read from the OPENAI_API_KEY environment variable.
    Never passed through config or agent cards (API_KEYS.docx ruling).
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
        Execute an OpenAI chat completion.
        Returns raw text. Never raises — returns error string on failure.
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ[_API_KEY_ENV])
            resp = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            return resp.choices[0].message.content

        except KeyError:
            err = f"OpenAIClient: {_API_KEY_ENV} environment variable not set."
            LOG.error(err)
            return f'{{"error": "{err}"}}'
        except Exception as exc:
            err = f"OpenAIClient: {self.model} failed — {exc}"
            LOG.error(err)
            return f'{{"error": "{err}"}}'
