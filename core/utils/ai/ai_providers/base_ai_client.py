# core/utils/ai/ai_providers/base_ai_client.py
#
# Abstract base class for all AI provider clients.
# Every concrete client (ClaudeClient, OpenAIClient, AzureOpenAIClient)
# implements this interface.
#
# Merge note:
#   capability_id added to chat_completion() signature so per-skill model
#   selection flows through to the provider if needed. Default is None —
#   existing callers that don't pass it are unaffected.

from abc import ABC, abstractmethod
from typing import Optional


class BaseAIClient(ABC):
    """
    Abstract base class for all Yo-ai AI provider clients.

    All subclasses must implement chat_completion(). The method must:
      - Accept capability_id as an optional kwarg (for per-skill routing)
      - Never raise — return an error string on failure
      - Return raw model output as a string
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        self.model       = model
        self.temperature = temperature
        self.max_tokens  = max_tokens

    @abstractmethod
    def chat_completion(
        self,
        system: str,
        user: str,
        capability_id: Optional[str] = None,
    ) -> str:
        """
        Execute a chat-style completion request.

        Args:
            system        : System prompt string
            user          : User prompt (JSON string from call_ai)
            capability_id : Optional — passed through for audit/logging.
                            Concrete clients may use it for routing decisions.

        Returns:
            Raw model output string. Never raises — return error string on failure.
        """
        raise NotImplementedError("chat_completion() must be implemented by subclasses")
