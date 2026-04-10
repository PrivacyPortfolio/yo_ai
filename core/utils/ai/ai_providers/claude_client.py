# core/utils/ai/ai_providers/claude_client.py
#
# ClaudeClient — Anthropic Claude via official SDK.
#

import logging
import os
from typing import Optional

from .base_ai_client import BaseAIClient

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "claude-sonnet-4-6"
_API_KEY_ENV   = "ANTHROPIC_API_KEY"


class ClaudeClient(BaseAIClient):
    """
    Anthropic Claude client using the official anthropic SDK.

    Constructed by provider_loader.py — not directly by agent code.

    API key is read from the ANTHROPIC_API_KEY environment variable.
    Never passed through config or agent cards (API_KEYS.docx ruling).
    """

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
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
        Execute a Claude message completion.
        Returns raw text. Never raises — returns error string on failure.
        """
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ[_API_KEY_ENV])
            msg = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            # Claude returns content as a list of typed blocks
            text_blocks = [
                block.text
                for block in msg.content
                if hasattr(block, "type") and block.type == "text"
            ]
            return "\n".join(text_blocks) if text_blocks else str(msg.content)

        except KeyError:
            err = f"ClaudeClient: {_API_KEY_ENV} environment variable not set."
            logger.error(err)
            return f'{{"error": "{err}"}}'
        except Exception as exc:
            err = f"ClaudeClient: {self.model} failed — {exc}"
            logger.error(err)
            return f'{{"error": "{err}"}}'
