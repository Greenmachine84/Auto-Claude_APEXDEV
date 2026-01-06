"""Anthropic Claude provider.

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


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""
    
    DEFAULT_BASE_URL = "https://api.anthropic.com"
    API_VERSION = "2024-01-01"
    
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
            max_context_length=200000,
            default_model="claude-sonnet-4-20250514",
            available_models=["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-5-haiku-20241022"]
        )
    
    def _build_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-api-key": self._config.api_key or "",
            "anthropic-version": self._config.api_version or self.API_VERSION
        }
    
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
        
        system_msg = None
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        payload = {
            "model": model or self.capabilities.default_model,
            "messages": user_messages,
            "max_tokens": max_tokens or 4096
        }
        if system_msg:
            payload["system"] = system_msg
        if temperature is not None:
            payload["temperature"] = temperature
        if tools:
            payload["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/v1/messages",
                    headers=self._build_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
                ) as resp:
                    data = await resp.json()
            
            content_blocks = data.get("content", [])
            text_content = ""
            tool_calls = []
            
            for block in content_blocks:
                if block.get("type") == "text":
                    text_content += block.get("text", "")
                elif block.get("type") == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        arguments=block.get("input", {})
                    ))
            
            usage = data.get("usage", {})
            
            response = LLMResponse(
                id=data.get("id", str(uuid.uuid4())),
                model=data.get("model", payload["model"]),
                provider="anthropic",
                content=text_content,
                finish_reason=FinishReason(data.get("stop_reason", "end_turn").replace("end_turn", "stop")),
                tool_calls=tool_calls,
                usage=LLMUsage(
                    prompt_tokens=usage.get("input_tokens", 0),
                    completion_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                ),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            self._track_request(success=True)
            return response
            
        except Exception as e:
            self._track_request(success=False)
            logger.error("Anthropic request failed: %s", e)
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
        system_msg = None
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        payload = {
            "model": model or self.capabilities.default_model,
            "messages": user_messages,
            "max_tokens": max_tokens or 4096,
            "stream": True
        }
        if system_msg:
            payload["system"] = system_msg
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/v1/messages",
                headers=self._build_headers(),
                json=payload
            ) as resp:
                async for line in resp.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield StreamChunk(
                                    delta=delta.get("text", ""),
                                    content=delta.get("text", "")
                                )
                        elif data.get("type") == "message_stop":
                            yield StreamChunk(finish_reason=FinishReason.STOP)
