"""Central LLM Manager singleton.

Part of Phase 2: LLM Architecture
"""

import logging
import threading
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from ..types import LLMConfig, LLMResponse, ProviderConfig, ProviderType, StreamChunk

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class ChatRequest:
    """Request for chat completion."""

    messages: list[dict[str, str]]
    model: str | None = None
    provider: ProviderType | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    tools: list[dict] | None = None
    stream: bool = False
    metadata: dict[str, Any] = None


class LLMManager:
    """Singleton manager for all LLM operations."""

    _instance: Optional["LLMManager"] = None
    _lock = threading.Lock()

    def __new__(cls, config: LLMConfig | None = None) -> "LLMManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: LLMConfig | None = None):
        if self._initialized:
            return

        from .fallback import FallbackHandler
        from .metrics import LLMMetrics
        from .provider_registry import ProviderRegistry
        from .router import LLMRouter

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
                tools=request.tools,
            )

            latency = (datetime.utcnow() - start).total_seconds() * 1000
            response.latency_ms = latency
            self._metrics.record_success(
                provider.provider_type, latency, response.usage
            )

            return response

        except Exception as e:
            logger.error("Chat failed: %s", e)
            self._metrics.record_error(
                request.provider or self._config.default_provider, str(e)
            )

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
                tools=request.tools,
            ):
                yield chunk

        except Exception as e:
            logger.error("Stream failed: %s", e)
            raise

    def register_provider(self, config: ProviderConfig) -> None:
        self._registry.register(config)
        self._config.add_provider(config)

    def get_metrics(self) -> dict[str, Any]:
        return self._metrics.summary()

    @property
    def config(self) -> LLMConfig:
        return self._config
