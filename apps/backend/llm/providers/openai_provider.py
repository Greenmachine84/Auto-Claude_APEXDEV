"""OpenAI provider.

Part of Phase 2: LLM Architecture
"""

import logging
import aiohttp
from typing import Any, AsyncIterator, Dict, List, Optional
from datetime import datetime
import json
import uuid

from .base import BaseLLMProvider, ProviderCapabilities
from ..types import ProviderConfig, LLMResponse, StreamChunk, LLMUsage, FinishReason, ToolCall

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
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
            max_context_length=128000,
            default_model="gpt-4o",
            available_models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview", "o1-mini"]
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> LLMResponse:
        start = datetime.utcnow()
        
        payload = {
            "model": model or self.capabilities.default_model,
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 4096
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._build_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
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
                provider="openai",
                content=message.get("content", "") or "",
                finish_reason=FinishReason(choice.get("finish_reason", "stop")),
                tool_calls=tool_calls,
                usage=LLMUsage(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0)
                ),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            self._track_request(success=True)
            return response
            
        except Exception as e:
            self._track_request(success=False)
            logger.error("OpenAI request failed: %s", e)
            raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        payload = {
            "model": model or self.capabilities.default_model,
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 4096,
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload
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
                            finish_reason=FinishReason(finish) if finish else None
                        )
