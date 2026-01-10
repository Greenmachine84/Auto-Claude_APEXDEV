"""Azure OpenAI provider.

Part of Phase 2: LLM Architecture
"""

import json
import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime

import aiohttp

from ..types import (
    FinishReason,
    LLMResponse,
    LLMUsage,
    ProviderConfig,
    StreamChunk,
    ToolCall,
)
from .base import BaseLLMProvider, ProviderCapabilities

logger = logging.getLogger(__name__)


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI Service provider."""

    API_VERSION = "2024-02-15-preview"

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._base_url = config.base_url  # Required: Azure endpoint
        self._api_version = config.api_version or self.API_VERSION

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_tools=True,
            supports_vision=True,
            supports_json_mode=True,
            max_context_length=128000,
            default_model="gpt-4o",
            available_models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        )

    def _build_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "api-key": self._config.api_key or "",
        }

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> LLMResponse:
        start = datetime.utcnow()
        deployment = model or self.capabilities.default_model

        payload = {
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 4096,
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]

        try:
            url = f"{self._base_url}/openai/deployments/{deployment}/chat/completions?api-version={self._api_version}"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=self._build_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds),
                ) as resp:
                    data = await resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = data.get("usage", {})

            tool_calls = []
            if message.get("tool_calls"):
                for tc in message["tool_calls"]:
                    tool_calls.append(ToolCall.from_dict(tc))

            response = LLMResponse(
                id=data.get("id", str(uuid.uuid4())),
                model=deployment,
                provider="azure",
                content=message.get("content", "") or "",
                finish_reason=FinishReason(choice.get("finish_reason", "stop")),
                tool_calls=tool_calls,
                usage=LLMUsage(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000,
            )
            self._track_request(success=True)
            return response

        except Exception as e:
            self._track_request(success=False)
            logger.error("Azure OpenAI request failed: %s", e)
            raise

    async def stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        deployment = model or self.capabilities.default_model

        payload = {
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 4096,
            "stream": True,
        }

        url = f"{self._base_url}/openai/deployments/{deployment}/chat/completions?api-version={self._api_version}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self._build_headers(), json=payload
            ) as resp:
                async for line in resp.content:
                    line = line.decode().strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = json.loads(line[6:])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        finish = data.get("choices", [{}])[0].get("finish_reason")
                        yield StreamChunk(
                            delta=delta.get("content", ""),
                            content=delta.get("content", ""),
                            finish_reason=FinishReason(finish) if finish else None,
                        )
