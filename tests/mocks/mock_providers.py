"""
Mock LLM providers for testing.

Provides mock implementations of all 8 supported LLM provider types
with configurable responses, streaming, and error simulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Optional
import asyncio


class ProviderType(Enum):
    """All supported LLM provider types."""
    COPILOT = "copilot"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class ModelCapability(Enum):
    """Model capabilities."""
    COMPLETION = "completion"
    CHAT = "chat"
    EMBEDDING = "embedding"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"


@dataclass
class ProviderConfig:
    """Provider configuration."""
    provider_type: ProviderType
    model: str
    api_key: str = "mock-key"
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class TokenUsage:
    """Token usage tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ProviderResponse:
    """Response from a provider."""
    content: str
    model: str
    provider: ProviderType
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: str = "stop"
    tool_calls: list[dict] = field(default_factory=list)
    latency_ms: float = 0.0


class MockLLMProvider:
    """Base mock LLM provider."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.provider_type = config.provider_type
        self.model = config.model
        self._responses: list[str] = []
        self._response_index = 0
        self._error_mode = False
        self._error: Optional[Exception] = None
        self._latency_ms = 0.0
        self.call_history: list[dict] = []
        self.capabilities: set[ModelCapability] = {
            ModelCapability.CHAT,
            ModelCapability.COMPLETION
        }

    def add_response(self, response: str) -> None:
        """Add a canned response."""
        self._responses.append(response)

    def set_responses(self, responses: list[str]) -> None:
        """Set multiple canned responses."""
        self._responses = responses
        self._response_index = 0

    def set_error(self, error: Exception) -> None:
        """Configure error mode."""
        self._error_mode = True
        self._error = error

    def clear_error(self) -> None:
        """Clear error mode."""
        self._error_mode = False
        self._error = None

    def set_latency(self, latency_ms: float) -> None:
        """Set simulated latency."""
        self._latency_ms = latency_ms

    def _get_next_response(self) -> str:
        """Get next canned response."""
        if not self._responses:
            return f"Mock response from {self.provider_type.value}"
        response = self._responses[self._response_index % len(self._responses)]
        self._response_index += 1
        return response

    async def complete(
        self,
        messages: list[dict],
        **kwargs
    ) -> ProviderResponse:
        """Complete a chat conversation."""
        self.call_history.append({
            "method": "complete",
            "messages": messages,
            "kwargs": kwargs,
            "timestamp": datetime.now().isoformat()
        })

        if self._latency_ms > 0:
            await asyncio.sleep(self._latency_ms / 1000)

        if self._error_mode and self._error:
            raise self._error

        content = self._get_next_response()
        prompt_tokens = sum(len(str(m.get("content", "")).split()) for m in messages) * 4
        completion_tokens = len(content.split()) * 4

        return ProviderResponse(
            content=content,
            model=self.model,
            provider=self.provider_type,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            ),
            latency_ms=self._latency_ms
        )

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings."""
        self.call_history.append({
            "method": "embed",
            "text": text,
            "timestamp": datetime.now().isoformat()
        })

        if self._error_mode and self._error:
            raise self._error

        # Generate deterministic mock embedding
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        return [(b / 255.0) * 2 - 1 for b in hash_bytes[:384]]


class MockStreamingProvider(MockLLMProvider):
    """Mock provider with streaming support."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._stream_chunks: list[str] = []
        self._chunk_delay_ms = 50.0

    def set_stream_chunks(self, chunks: list[str]) -> None:
        """Set streaming chunks."""
        self._stream_chunks = chunks

    def set_chunk_delay(self, delay_ms: float) -> None:
        """Set delay between chunks."""
        self._chunk_delay_ms = delay_ms

    async def stream(
        self,
        messages: list[dict],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream a response."""
        self.call_history.append({
            "method": "stream",
            "messages": messages,
            "kwargs": kwargs,
            "timestamp": datetime.now().isoformat()
        })

        if self._error_mode and self._error:
            raise self._error

        chunks = self._stream_chunks or [self._get_next_response()]
        for chunk in chunks:
            if self._chunk_delay_ms > 0:
                await asyncio.sleep(self._chunk_delay_ms / 1000)
            yield chunk


class MockProviderFactory:
    """Factory for creating mock providers."""

    _default_models = {
        ProviderType.COPILOT: "copilot-4",
        ProviderType.OPENROUTER: "openrouter/auto",
        ProviderType.OLLAMA: "llama3",
        ProviderType.LMSTUDIO: "local-model",
        ProviderType.GEMINI: "gemini-pro",
        ProviderType.OPENAI: "gpt-4",
        ProviderType.ANTHROPIC: "claude-3-opus",
        ProviderType.AZURE: "gpt-4-azure",
    }

    @classmethod
    def create(
        cls,
        provider_type: ProviderType,
        model: str = None,
        streaming: bool = False,
        **config_kwargs
    ) -> MockLLMProvider:
        """Create a mock provider."""
        if model is None:
            model = cls._default_models.get(provider_type, "default-model")

        config = ProviderConfig(
            provider_type=provider_type,
            model=model,
            **config_kwargs
        )

        if streaming:
            return MockStreamingProvider(config)
        return MockLLMProvider(config)

    @classmethod
    def create_all(cls, streaming: bool = False) -> dict[ProviderType, MockLLMProvider]:
        """Create all 8 providers."""
        return {
            ptype: cls.create(ptype, streaming=streaming)
            for ptype in ProviderType
        }


class MockProviderRegistry:
    """Registry for mock providers."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._default_provider = None
        return cls._instance

    def register(
        self,
        provider_type: ProviderType,
        provider: MockLLMProvider,
        is_default: bool = False
    ) -> None:
        """Register a provider."""
        self._providers[provider_type] = provider
        if is_default:
            self._default_provider = provider_type

    def get(self, provider_type: ProviderType) -> Optional[MockLLMProvider]:
        """Get a provider by type."""
        return self._providers.get(provider_type)

    def get_default(self) -> Optional[MockLLMProvider]:
        """Get the default provider."""
        if self._default_provider:
            return self._providers.get(self._default_provider)
        return None

    def list_available(self) -> list[ProviderType]:
        """List available provider types."""
        return list(self._providers.keys())

    def clear(self) -> None:
        """Clear all providers."""
        self._providers.clear()
        self._default_provider = None

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance for testing."""
        cls._instance = None
