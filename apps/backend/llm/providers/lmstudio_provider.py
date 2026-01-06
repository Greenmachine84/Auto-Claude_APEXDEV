"""LM Studio local provider.

Part of Phase 2: LLM Architecture
"""

import logging
import aiohttp
from typing import Any, AsyncIterator, Dict, List, Optional
from datetime import datetime
import json
import uuid

from .base import BaseLLMProvider, ProviderCapabilities
from ..types import ProviderConfig, LLMResponse, StreamChunk, LLMUsage, FinishReason

logger = logging.getLogger(__name__)


class LMStudioProvider(BaseLLMProvider):
    """LM Studio local LLM provider (OpenAI-compatible API)."""
    
    DEFAULT_BASE_URL = "http://localhost:1234/v1"
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_tools=False,  # Limited tool support
            supports_vision=False,
            supports_json_mode=True,
            default_model="local-model",
            available_models=[]
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
            "max_tokens": max_tokens or 4096,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
                ) as resp:
                    data = await resp.json()
            
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = data.get("usage", {})
            
            response = LLMResponse(
                id=data.get("id", str(uuid.uuid4())),
                model=data.get("model", payload["model"]),
                provider="lmstudio",
                content=message.get("content", ""),
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
            logger.error("LM Studio request failed: %s", e)
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
                headers={"Content-Type": "application/json"},
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
