# core/utils/ai/ai_providers/openai_client.py
#
# OpenAIClient — OpenAI-compatible API via official SDK.
#
# Merge changes from original:
#   - requests.post() replaced with openai SDK
#   - api_key and endpoint constructor args removed — api_key read
#     from OPENAI_API_KEY env var by convention
#   - capability_id added to chat_completion() per BaseAIClient contract
#   - temperature and max_tokens passed through to SDK call
#   - Never raises — error string returned on failure

import logging
import os
from typing import Optional

from .base_ai_client import BaseAIClient

logger = logging.getLogger(__name__)

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
            logger.error(err)
            return f'{{"error": "{err}"}}'
        except Exception as exc:
            err = f"OpenAIClient: {self.model} failed — {exc}"
            logger.error(err)
            return f'{{"error": "{err}"}}'
