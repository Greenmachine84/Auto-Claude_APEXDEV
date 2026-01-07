"""
LLM test fixtures.

Provides reusable fixtures for testing LLM provider integrations
including mock providers, responses, and configurations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Optional
from unittest.mock import AsyncMock, MagicMock
import pytest


class ProviderType(Enum):
    """Supported LLM provider types."""
    COPILOT = "copilot"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class MessageRole(Enum):
    """Message roles in conversations."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ResponseFormat(Enum):
    """Response format types."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    CODE = "code"


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    provider_type: ProviderType
    model: str = "gpt-4"
    api_key: str = "test-api-key"
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096
    extra_params: dict = field(default_factory=dict)


@dataclass
class Message:
    """A message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to API format."""
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        """Add token usage."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens
        )


@dataclass
class CompletionResponse:
    """Response from an LLM completion."""
    content: str
    model: str
    provider: ProviderType
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: str = "stop"
    tool_calls: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LLMTestContext:
    """Test context for LLM operations."""
    provider: Any
    config: ProviderConfig
    messages: list[Message] = field(default_factory=list)
    responses: list[CompletionResponse] = field(default_factory=list)
    errors: list[Exception] = field(default_factory=list)
    total_usage: TokenUsage = field(default_factory=TokenUsage)

    def add_response(self, response: CompletionResponse) -> None:
        """Track a response."""
        self.responses.append(response)
        self.total_usage = self.total_usage + response.usage


class MockLLMProvider:
    """Mock LLM provider for testing."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._responses: list[str] = []
        self._response_index = 0
        self._stream_chunks: list[str] = []
        self._should_fail = False
        self._failure_error: Optional[Exception] = None
        self.call_count = 0
        self.last_request: Optional[dict] = None

    def set_responses(self, responses: list[str]) -> None:
        """Set canned responses in order."""
        self._responses = responses
        self._response_index = 0

    def set_stream_chunks(self, chunks: list[str]) -> None:
        """Set streaming chunks."""
        self._stream_chunks = chunks

    def set_failure(self, error: Exception) -> None:
        """Configure provider to fail."""
        self._should_fail = True
        self._failure_error = error

    def reset_failure(self) -> None:
        """Reset failure mode."""
        self._should_fail = False
        self._failure_error = None

    async def complete(
        self,
        messages: list[Message],
        **kwargs
    ) -> CompletionResponse:
        """Complete a conversation."""
        self.call_count += 1
        self.last_request = {
            "messages": [m.to_dict() for m in messages],
            **kwargs
        }

        if self._should_fail and self._failure_error:
            raise self._failure_error

        content = self._get_next_response()
        usage = TokenUsage(
            prompt_tokens=sum(len(m.content.split()) for m in messages) * 4,
            completion_tokens=len(content.split()) * 4,
            total_tokens=0
        )
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens

        return CompletionResponse(
            content=content,
            model=self.config.model,
            provider=self.config.provider_type,
            usage=usage
        )

    async def stream(
        self,
        messages: list[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream a response."""
        self.call_count += 1

        if self._should_fail and self._failure_error:
            raise self._failure_error

        chunks = self._stream_chunks or [self._get_next_response()]
        for chunk in chunks:
            yield chunk

    def _get_next_response(self) -> str:
        """Get the next canned response."""
        if not self._responses:
            return "Default mock response"

        response = self._responses[self._response_index % len(self._responses)]
        self._response_index += 1
        return response


class MockProviderRegistry:
    """Registry of mock LLM providers."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
        return cls._instance

    def register(self, provider_type: ProviderType, provider: MockLLMProvider) -> None:
        """Register a provider."""
        self._providers[provider_type] = provider

    def get(self, provider_type: ProviderType) -> Optional[MockLLMProvider]:
        """Get a registered provider."""
        return self._providers.get(provider_type)

    def list_providers(self) -> list[ProviderType]:
        """List registered provider types."""
        return list(self._providers.keys())

    def clear(self) -> None:
        """Clear all registered providers."""
        self._providers.clear()


def create_llm_provider(
    provider_type: ProviderType = ProviderType.OPENAI,
    model: str = "gpt-4",
    **config_overrides
) -> MockLLMProvider:
    """Create a mock LLM provider."""
    config = ProviderConfig(
        provider_type=provider_type,
        model=model,
        **config_overrides
    )
    return MockLLMProvider(config)


def create_mock_response(
    content: str = "Mock response",
    provider_type: ProviderType = ProviderType.OPENAI,
    model: str = "gpt-4",
    **kwargs
) -> CompletionResponse:
    """Create a mock completion response."""
    return CompletionResponse(
        content=content,
        model=model,
        provider=provider_type,
        **kwargs
    )


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def openai_provider() -> MockLLMProvider:
    """Provide an OpenAI mock provider."""
    provider = create_llm_provider(ProviderType.OPENAI, "gpt-4")
    provider.set_responses(["OpenAI response"])
    return provider


@pytest.fixture
def anthropic_provider() -> MockLLMProvider:
    """Provide an Anthropic mock provider."""
    provider = create_llm_provider(ProviderType.ANTHROPIC, "claude-3-opus")
    provider.set_responses(["Anthropic response"])
    return provider


@pytest.fixture
def ollama_provider() -> MockLLMProvider:
    """Provide an Ollama mock provider."""
    config = ProviderConfig(
        provider_type=ProviderType.OLLAMA,
        model="llama3",
        base_url="http://localhost:11434"
    )
    provider = MockLLMProvider(config)
    provider.set_responses(["Ollama response"])
    return provider


@pytest.fixture
def all_providers() -> dict[ProviderType, MockLLMProvider]:
    """Provide all 8 mock providers."""
    providers = {}
    models = {
        ProviderType.COPILOT: "copilot-4",
        ProviderType.OPENROUTER: "openrouter/auto",
        ProviderType.OLLAMA: "llama3",
        ProviderType.LMSTUDIO: "local-model",
        ProviderType.GEMINI: "gemini-pro",
        ProviderType.OPENAI: "gpt-4",
        ProviderType.ANTHROPIC: "claude-3-opus",
        ProviderType.AZURE: "gpt-4-azure",
    }
    for ptype, model in models.items():
        providers[ptype] = create_llm_provider(ptype, model)
        providers[ptype].set_responses([f"Response from {ptype.value}"])
    return providers


@pytest.fixture
def provider_registry() -> MockProviderRegistry:
    """Provide a clean provider registry."""
    registry = MockProviderRegistry()
    registry.clear()
    return registry


@pytest.fixture
def llm_context(openai_provider: MockLLMProvider) -> LLMTestContext:
    """Provide an LLM test context."""
    return LLMTestContext(
        provider=openai_provider,
        config=openai_provider.config
    )


@pytest.fixture
def conversation_messages() -> list[Message]:
    """Provide sample conversation messages."""
    return [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="Hello, how are you?"),
        Message(role=MessageRole.ASSISTANT, content="I'm doing well, thank you!"),
        Message(role=MessageRole.USER, content="Can you help me with Python?"),
    ]


@pytest.fixture
def streaming_provider() -> MockLLMProvider:
    """Provide a provider configured for streaming."""
    provider = create_llm_provider(ProviderType.OPENAI)
    provider.set_stream_chunks([
        "Hello",
        ", ",
        "this ",
        "is ",
        "a ",
        "streaming ",
        "response."
    ])
    return provider
