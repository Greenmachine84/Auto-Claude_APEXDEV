"""Ollama local provider.

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


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    
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
            default_model="llama3.1:latest",
            available_models=["llama3.1:latest", "codellama:latest", "mistral:latest", "mixtral:latest"]
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
            "stream": False,
            "options": {
                "temperature": temperature or 0.7,
                "num_predict": max_tokens or 4096
            }
        }
        if tools:
            payload["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
                ) as resp:
                    data = await resp.json()
            
            message = data.get("message", {})
            
            response = LLMResponse(
                id=str(uuid.uuid4()),
                model=data.get("model", payload["model"]),
                provider="ollama",
                content=message.get("content", ""),
                usage=LLMUsage(
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                ),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            self._track_request(success=True)
            return response
            
        except Exception as e:
            self._track_request(success=False)
            logger.error("Ollama request failed: %s", e)
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
            "stream": True,
            "options": {
                "temperature": temperature or 0.7,
                "num_predict": max_tokens or 4096
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/api/chat",
                json=payload
            ) as resp:
                async for line in resp.content:
                    if line:
                        data = json.loads(line)
                        message = data.get("message", {})
                        done = data.get("done", False)
                        yield StreamChunk(
                            delta=message.get("content", ""),
                            content=message.get("content", ""),
                            finish_reason=FinishReason.STOP if done else None
                        )
    
    async def list_models(self) -> List[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/api/tags") as resp:
                data = await resp.json()
                return [m["name"] for m in data.get("models", [])]
