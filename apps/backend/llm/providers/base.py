"""Base LLM provider abstraction.

Part of Phase 2: LLM Architecture
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..types import (
    ProviderType, ProviderConfig, ProviderStatus,
    LLMResponse, StreamChunk, LLMCapability, LLMUsage
)

logger = logging.getLogger(__name__)


@dataclass
class ProviderCapabilities:
    """Capabilities of a provider."""
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False
    supports_json_mode: bool = True
    supports_system_prompt: bool = True
    max_context_length: int = 128000
    default_model: str = ""
    available_models: List[str] = field(default_factory=list)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: ProviderConfig):
        self._config = config
        self._status = ProviderStatus.UNKNOWN
        self._last_error: Optional[str] = None
        self._request_count = 0
        self._error_count = 0
    
    @property
    def provider_type(self) -> ProviderType:
        return self._config.provider_type
    
    @property
    def status(self) -> ProviderStatus:
        return self._status
    
    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> LLMResponse:
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        pass
    
    async def health_check(self) -> ProviderStatus:
        try:
            response = await self.chat(
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            self._status = ProviderStatus.HEALTHY
        except Exception as e:
            self._last_error = str(e)
            self._status = ProviderStatus.UNAVAILABLE
            logger.warning("Health check failed for %s: %s", self.provider_type.value, e)
        return self._status
    
    def _build_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        headers.update(self._config.headers)
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        return headers
    
    def _track_request(self, success: bool) -> None:
        self._request_count += 1
        if not success:
            self._error_count += 1
