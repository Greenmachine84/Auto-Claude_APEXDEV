"""Central LLM Manager singleton.

Part of Phase 2: LLM Architecture
"""

import asyncio
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
import threading

from ..types import LLMConfig, LLMResponse, StreamChunk, ProviderType, ProviderConfig

if TYPE_CHECKING:
    from ..providers import BaseLLMProvider

logger = logging.getLogger(__name__)


@dataclass
class ChatRequest:
    """Request for chat completion."""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    provider: Optional[ProviderType] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict]] = None
    stream: bool = False
    metadata: Dict[str, Any] = None


class LLMManager:
    """Singleton manager for all LLM operations."""
    
    _instance: Optional["LLMManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls, config: Optional[LLMConfig] = None) -> "LLMManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[LLMConfig] = None):
        if self._initialized:
            return
        
        from .provider_registry import ProviderRegistry
        from .router import LLMRouter
        from .fallback import FallbackHandler
        from .metrics import LLMMetrics
        
        self._config = config or LLMConfig()
        self._registry = ProviderRegistry()
        self._router = LLMRouter(self._config.router, self._registry)
        self._fallback = FallbackHandler(self._config.fallback, self._registry)
        self._metrics = LLMMetrics()
        self._initialized = True
        logger.info("LLMManager initialized")
    
    async def chat(self, request: ChatRequest) -> LLMResponse:
        start = datetime.utcnow()
        
        try:
            provider = self._router.route(request)
            response = await provider.chat(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=request.tools
            )
            
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            response.latency_ms = latency
            self._metrics.record_success(provider.provider_type, latency, response.usage)
            
            return response
            
        except Exception as e:
            logger.error("Chat failed: %s", e)
            self._metrics.record_error(request.provider or self._config.default_provider, str(e))
            
            if self._config.router.enable_fallback:
                return await self._fallback.execute(request)
            raise
    
    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        try:
            provider = self._router.route(request)
            async for chunk in provider.stream(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=request.tools
            ):
                yield chunk
                
        except Exception as e:
            logger.error("Stream failed: %s", e)
            raise
    
    def register_provider(self, config: ProviderConfig) -> None:
        self._registry.register(config)
        self._config.add_provider(config)
    
    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.summary()
    
    @property
    def config(self) -> LLMConfig:
        return self._config
