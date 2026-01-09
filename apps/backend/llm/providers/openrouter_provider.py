"""OpenRouter provider.

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


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter unified API provider."""

    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_tools=True,
            supports_vision=True,
            supports_json_mode=True,
            default_model="anthropic/claude-3.5-sonnet",
            available_models=[
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3-opus",
                "openai/gpt-4o",
                "openai/gpt-4-turbo",
                "google/gemini-pro-1.5",
                "meta-llama/llama-3.1-405b-instruct",
            ],
        )

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

        payload = {
            "model": model or self.capabilities.default_model,
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 4096,
        }
        if tools:
            payload["tools"] = tools

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/chat/completions",
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
                model=data.get("model", payload["model"]),
                provider="openrouter",
                content=message.get("content", ""),
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
            logger.error("OpenRouter request failed: %s", e)
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
        payload = {
            "model": model or self.capabilities.default_model,
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 4096,
            "stream": True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload,
            ) as resp:
                async for line in resp.content:
                    line = line.decode().strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = json.loads(line[6:])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        yield StreamChunk(
                            delta=delta.get("content", ""),
                            content=delta.get("content", ""),
                        )
