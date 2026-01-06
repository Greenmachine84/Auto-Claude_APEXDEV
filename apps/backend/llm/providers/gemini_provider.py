"""Google Gemini provider.

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


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
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
            max_context_length=2000000,
            default_model="gemini-1.5-pro",
            available_models=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]
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
        model_name = model or self.capabilities.default_model
        
        contents = self._convert_messages(messages)
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature or 0.7,
                "maxOutputTokens": max_tokens or 4096
            }
        }
        if tools:
            payload["tools"] = [{"functionDeclarations": tools}]
        
        try:
            url = f"{self._base_url}/models/{model_name}:generateContent?key={self._config.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
                ) as resp:
                    data = await resp.json()
            
            candidates = data.get("candidates", [{}])
            content = candidates[0].get("content", {}) if candidates else {}
            parts = content.get("parts", [{}])
            text = parts[0].get("text", "") if parts else ""
            
            usage_meta = data.get("usageMetadata", {})
            
            response = LLMResponse(
                id=str(uuid.uuid4()),
                model=model_name,
                provider="gemini",
                content=text,
                usage=LLMUsage(
                    prompt_tokens=usage_meta.get("promptTokenCount", 0),
                    completion_tokens=usage_meta.get("candidatesTokenCount", 0),
                    total_tokens=usage_meta.get("totalTokenCount", 0)
                ),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            self._track_request(success=True)
            return response
            
        except Exception as e:
            self._track_request(success=False)
            logger.error("Gemini request failed: %s", e)
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
        model_name = model or self.capabilities.default_model
        contents = self._convert_messages(messages)
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature or 0.7,
                "maxOutputTokens": max_tokens or 4096
            }
        }
        
        url = f"{self._base_url}/models/{model_name}:streamGenerateContent?key={self._config.api_key}&alt=sse"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                async for line in resp.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        candidates = data.get("candidates", [{}])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [{}])
                            text = parts[0].get("text", "") if parts else ""
                            yield StreamChunk(delta=text, content=text)
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict]:
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        return contents
