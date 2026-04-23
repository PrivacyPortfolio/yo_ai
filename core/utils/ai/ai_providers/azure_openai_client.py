# core/utils/ai/ai_providers/azure_openai_client.py
#
# AzureOpenAIClient — Azure OpenAI deployment via official SDK.
#
#   - deployment kept as constructor arg — Azure requires it and it is
#     not sensitive (it's the deployment name, not a secret)
#   - capability_id added to chat_completion() per BaseAIClient contract
#   - temperature and max_tokens passed through to SDK call
#   - Never raises — error string returned on failure

import os
from typing import Optional

from .base_ai_client import BaseAIClient
from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("azure_openai_client")

_API_KEY_ENV  = "AZURE_OPENAI_KEY"
_ENDPOINT_ENV = "AZURE_OPENAI_ENDPOINT"
_API_VERSION  = "2024-02-01"


class AzureOpenAIClient(BaseAIClient):
    """
    Azure OpenAI client using the official openai SDK (AzureOpenAI).

    Constructed by provider_loader.py — not directly by agent code.

    API key and endpoint are read from environment variables.
    Never passed through config or agent cards (API_KEYS.docx ruling).

    Args:
        model      : Azure deployment model name
        deployment : Azure deployment name (not a secret — kept as arg)
        temperature: Sampling temperature
        max_tokens : Max response tokens
    """

    def __init__(
        self,
        model: str,
        deployment: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        api_version: str = _API_VERSION,
    ):
        super().__init__(model, temperature, max_tokens)
        self.deployment  = deployment
        self.api_version = api_version

    def chat_completion(
        self,
        system: str,
        user: str,
        capability_id: Optional[str] = None,
    ) -> str:
        """
        Execute an Azure OpenAI chat completion.
        Returns raw text. Never raises — returns error string on failure.
        """
        try:
            from openai import AzureOpenAI
            client = AzureOpenAI(
                api_key=os.environ[_API_KEY_ENV],
                azure_endpoint=os.environ[_ENDPOINT_ENV],
                api_version=self.api_version,
            )
            resp = client.chat.completions.create(
                model=self.deployment,   # Azure uses deployment name here
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            return resp.choices[0].message.content

        except KeyError as exc:
            err = f"AzureOpenAIClient: required environment variable not set — {exc}"
            LOG.error(err)
            return f'{{"error": "{err}"}}'
        except Exception as exc:
            err = f"AzureOpenAIClient: {self.model} failed — {exc}"
            LOG.error(err)
            return f'{{"error": "{err}"}}'
