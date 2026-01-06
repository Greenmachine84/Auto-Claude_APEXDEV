"""GitHub Copilot provider.

Part of Phase 2: LLM Architecture
"""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional
from datetime import datetime
import uuid

from .base import BaseLLMProvider, ProviderCapabilities
from ..types import ProviderConfig, LLMResponse, StreamChunk, LLMUsage, FinishReason

logger = logging.getLogger(__name__)


class CopilotProvider(BaseLLMProvider):
    """GitHub Copilot LLM provider."""
    
    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_tools=True,
            supports_vision=True,
            supports_json_mode=True,
            default_model="gpt-4o",
            available_models=["gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet", "claude-3.5-haiku"]
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
        # Copilot integration is handled through VS Code extension API
        # This is a placeholder for direct API access
        start = datetime.utcnow()
        
        try:
            # In production, would call Copilot API
            response = LLMResponse(
                id=str(uuid.uuid4()),
                model=model or self.capabilities.default_model,
                provider="copilot",
                content="[Copilot response placeholder]",
                usage=LLMUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                latency_ms=(datetime.utcnow() - start).total_seconds() * 1000
            )
            self._track_request(success=True)
            return response
            
        except Exception as e:
            self._track_request(success=False)
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
        # Placeholder for streaming
        yield StreamChunk(content="[Copilot stream]", delta="[Copilot stream]", finish_reason=FinishReason.STOP)
