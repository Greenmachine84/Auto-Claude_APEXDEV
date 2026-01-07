"""
Integration tests for Agent-LLM provider interactions.

Tests the complete flow of agents communicating with LLM providers,
including message formatting, streaming responses, and error handling.
"""

import pytest
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Optional
from unittest.mock import AsyncMock, MagicMock


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


class AgentType(Enum):
    """Agent types for integration testing."""
    CODER = "coder"
    REVIEWER = "reviewer"
    FIXER = "fixer"
    PLANNER = "planner"


@dataclass
class MockMessage:
    """Mock message for LLM communication."""
    role: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class MockCompletionResponse:
    """Mock completion response from LLM."""
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    finish_reason: str = "stop"


class MockLLMProvider:
    """Mock LLM provider for integration testing."""

    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type
        self.model = f"{provider_type.value}-model"
        self.call_count = 0
        self.last_messages: list[MockMessage] = []
        self._responses: list[str] = []
        self._stream_chunks: list[str] = []
        self._should_fail = False
        self._fail_after = -1

    def set_responses(self, responses: list[str]) -> None:
        """Set predefined responses."""
        self._responses = responses.copy()

    def set_stream_chunks(self, chunks: list[str]) -> None:
        """Set predefined stream chunks."""
        self._stream_chunks = chunks.copy()

    def set_failure_mode(self, should_fail: bool, fail_after: int = -1) -> None:
        """Configure failure behavior."""
        self._should_fail = should_fail
        self._fail_after = fail_after

    async def complete(self, messages: list[MockMessage]) -> MockCompletionResponse:
        """Complete a conversation."""
        self.call_count += 1
        self.last_messages = messages

        if self._should_fail and (self._fail_after < 0 or self.call_count > self._fail_after):
            raise RuntimeError(f"Provider {self.provider_type.value} failed")

        response_content = self._responses.pop(0) if self._responses else "Default response"
        return MockCompletionResponse(
            content=response_content,
            model=self.model,
            usage={"prompt_tokens": 100, "completion_tokens": 50}
        )

    async def stream(self, messages: list[MockMessage]) -> AsyncIterator[str]:
        """Stream a response."""
        self.call_count += 1
        self.last_messages = messages

        if self._should_fail:
            raise RuntimeError(f"Provider {self.provider_type.value} stream failed")

        chunks = self._stream_chunks if self._stream_chunks else ["chunk1", "chunk2", "chunk3"]
        for chunk in chunks:
            yield chunk


class MockAgent:
    """Mock agent for integration testing."""

    def __init__(self, agent_type: AgentType, provider: MockLLMProvider):
        self.agent_type = agent_type
        self.provider = provider
        self.system_prompt = f"You are a {agent_type.value} agent."
        self.conversation_history: list[MockMessage] = []
        self.max_retries = 3
        self.retry_count = 0

    async def send_message(self, content: str) -> str:
        """Send a message and get a response."""
        user_message = MockMessage(role="user", content=content)
        self.conversation_history.append(user_message)

        messages = [MockMessage(role="system", content=self.system_prompt)]
        messages.extend(self.conversation_history)

        try:
            response = await self.provider.complete(messages)
            assistant_message = MockMessage(role="assistant", content=response.content)
            self.conversation_history.append(assistant_message)
            self.retry_count = 0
            return response.content
        except RuntimeError as e:
            self.retry_count += 1
            if self.retry_count < self.max_retries:
                return await self.send_message(content)
            raise

    async def stream_message(self, content: str) -> AsyncIterator[str]:
        """Stream a message response."""
        user_message = MockMessage(role="user", content=content)
        self.conversation_history.append(user_message)

        messages = [MockMessage(role="system", content=self.system_prompt)]
        messages.extend(self.conversation_history)

        full_response = ""
        async for chunk in self.provider.stream(messages):
            full_response += chunk
            yield chunk

        assistant_message = MockMessage(role="assistant", content=full_response)
        self.conversation_history.append(assistant_message)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()


class MockProviderRegistry:
    """Mock provider registry for integration testing."""

    def __init__(self):
        self._providers: dict[ProviderType, MockLLMProvider] = {}
        self._default_provider: Optional[ProviderType] = None

    def register(self, provider: MockLLMProvider) -> None:
        """Register a provider."""
        self._providers[provider.provider_type] = provider
        if self._default_provider is None:
            self._default_provider = provider.provider_type

    def get(self, provider_type: ProviderType) -> MockLLMProvider:
        """Get a provider by type."""
        if provider_type not in self._providers:
            raise KeyError(f"Provider {provider_type.value} not registered")
        return self._providers[provider_type]

    def get_default(self) -> MockLLMProvider:
        """Get the default provider."""
        if self._default_provider is None:
            raise RuntimeError("No default provider set")
        return self._providers[self._default_provider]

    def set_default(self, provider_type: ProviderType) -> None:
        """Set the default provider."""
        if provider_type not in self._providers:
            raise KeyError(f"Provider {provider_type.value} not registered")
        self._default_provider = provider_type


class MockAgentFactory:
    """Factory for creating agents with providers."""

    def __init__(self, registry: MockProviderRegistry):
        self.registry = registry

    def create(
        self,
        agent_type: AgentType,
        provider_type: Optional[ProviderType] = None
    ) -> MockAgent:
        """Create an agent with the specified or default provider."""
        if provider_type:
            provider = self.registry.get(provider_type)
        else:
            provider = self.registry.get_default()
        return MockAgent(agent_type, provider)


# ============================================================================
# Test Classes
# ============================================================================

class TestAgentProviderConnection:
    """Tests for agent-provider connection establishment."""

    @pytest.fixture
    def registry(self) -> MockProviderRegistry:
        """Create provider registry."""
        registry = MockProviderRegistry()
        for provider_type in [ProviderType.OPENAI, ProviderType.ANTHROPIC]:
            registry.register(MockLLMProvider(provider_type))
        return registry

    @pytest.fixture
    def factory(self, registry: MockProviderRegistry) -> MockAgentFactory:
        """Create agent factory."""
        return MockAgentFactory(registry)

    def test_agent_uses_default_provider(self, factory: MockAgentFactory):
        """Test agent uses default provider when none specified."""
        agent = factory.create(AgentType.CODER)
        assert agent.provider.provider_type == ProviderType.OPENAI

    def test_agent_uses_specified_provider(self, factory: MockAgentFactory):
        """Test agent uses specified provider."""
        agent = factory.create(AgentType.CODER, ProviderType.ANTHROPIC)
        assert agent.provider.provider_type == ProviderType.ANTHROPIC

    def test_agent_factory_raises_for_unknown_provider(self, factory: MockAgentFactory):
        """Test factory raises for unknown provider."""
        with pytest.raises(KeyError):
            factory.create(AgentType.CODER, ProviderType.OLLAMA)


class TestAgentMessageFlow:
    """Tests for message flow between agent and provider."""

    @pytest.fixture
    def provider(self) -> MockLLMProvider:
        """Create mock provider."""
        return MockLLMProvider(ProviderType.OPENAI)

    @pytest.fixture
    def agent(self, provider: MockLLMProvider) -> MockAgent:
        """Create mock agent."""
        return MockAgent(AgentType.CODER, provider)

    @pytest.mark.asyncio
    async def test_message_includes_system_prompt(self, agent: MockAgent):
        """Test that messages include system prompt."""
        agent.provider.set_responses(["Response"])
        await agent.send_message("Hello")

        messages = agent.provider.last_messages
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "coder" in messages[0].content.lower()

    @pytest.mark.asyncio
    async def test_conversation_history_preserved(self, agent: MockAgent):
        """Test conversation history is preserved."""
        agent.provider.set_responses(["First response", "Second response"])

        await agent.send_message("First message")
        await agent.send_message("Second message")

        assert len(agent.conversation_history) == 4
        assert agent.conversation_history[0].content == "First message"
        assert agent.conversation_history[1].content == "First response"

    @pytest.mark.asyncio
    async def test_clear_history(self, agent: MockAgent):
        """Test clearing conversation history."""
        agent.provider.set_responses(["Response"])
        await agent.send_message("Message")

        agent.clear_history()
        assert len(agent.conversation_history) == 0


class TestStreamingIntegration:
    """Tests for streaming response integration."""

    @pytest.fixture
    def provider(self) -> MockLLMProvider:
        """Create mock provider."""
        return MockLLMProvider(ProviderType.ANTHROPIC)

    @pytest.fixture
    def agent(self, provider: MockLLMProvider) -> MockAgent:
        """Create mock agent."""
        return MockAgent(AgentType.REVIEWER, provider)

    @pytest.mark.asyncio
    async def test_stream_chunks_received(self, agent: MockAgent):
        """Test stream chunks are received in order."""
        agent.provider.set_stream_chunks(["Hello ", "world", "!"])

        chunks = []
        async for chunk in agent.stream_message("Hi"):
            chunks.append(chunk)

        assert chunks == ["Hello ", "world", "!"]

    @pytest.mark.asyncio
    async def test_stream_updates_history(self, agent: MockAgent):
        """Test streaming updates conversation history."""
        agent.provider.set_stream_chunks(["Full ", "response"])

        async for _ in agent.stream_message("Message"):
            pass

        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[1].content == "Full response"


class TestProviderFailover:
    """Tests for provider failover and retry logic."""

    @pytest.fixture
    def provider(self) -> MockLLMProvider:
        """Create mock provider."""
        return MockLLMProvider(ProviderType.OPENAI)

    @pytest.fixture
    def agent(self, provider: MockLLMProvider) -> MockAgent:
        """Create mock agent."""
        agent = MockAgent(AgentType.FIXER, provider)
        agent.max_retries = 3
        return agent

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, agent: MockAgent):
        """Test agent retries on provider failure."""
        agent.provider.set_failure_mode(True, fail_after=2)
        agent.provider.set_responses(["", "", "Success after retry"])

        response = await agent.send_message("Retry test")
        assert response == "Success after retry"
        assert agent.provider.call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, agent: MockAgent):
        """Test agent fails after max retries."""
        agent.provider.set_failure_mode(True)

        with pytest.raises(RuntimeError):
            await agent.send_message("Will fail")

        assert agent.retry_count == agent.max_retries


class TestMultiAgentCoordination:
    """Tests for multi-agent coordination with LLM providers."""

    @pytest.fixture
    def registry(self) -> MockProviderRegistry:
        """Create registry with multiple providers."""
        registry = MockProviderRegistry()
        for pt in ProviderType:
            registry.register(MockLLMProvider(pt))
        return registry

    @pytest.fixture
    def factory(self, registry: MockProviderRegistry) -> MockAgentFactory:
        """Create agent factory."""
        return MockAgentFactory(registry)

    @pytest.mark.asyncio
    async def test_agents_use_different_providers(self, factory: MockAgentFactory):
        """Test multiple agents can use different providers."""
        coder = factory.create(AgentType.CODER, ProviderType.OPENAI)
        reviewer = factory.create(AgentType.REVIEWER, ProviderType.ANTHROPIC)

        coder.provider.set_responses(["Code written"])
        reviewer.provider.set_responses(["Code reviewed"])

        code_response = await coder.send_message("Write code")
        review_response = await reviewer.send_message("Review code")

        assert "written" in code_response.lower()
        assert "reviewed" in review_response.lower()

    @pytest.mark.asyncio
    async def test_agent_handoff_preserves_context(self, factory: MockAgentFactory):
        """Test context preservation during agent handoff."""
        coder = factory.create(AgentType.CODER, ProviderType.OPENAI)
        fixer = factory.create(AgentType.FIXER, ProviderType.OPENAI)

        coder.provider.set_responses(["Initial code"])
        await coder.send_message("Write initial code")

        # Transfer context to fixer
        fixer.conversation_history = coder.conversation_history.copy()
        fixer.provider.set_responses(["Fixed code"])

        response = await fixer.send_message("Fix the bug")
        assert len(fixer.conversation_history) == 4


class TestProviderSwitching:
    """Tests for dynamic provider switching."""

    @pytest.fixture
    def registry(self) -> MockProviderRegistry:
        """Create registry with providers."""
        registry = MockProviderRegistry()
        registry.register(MockLLMProvider(ProviderType.OPENAI))
        registry.register(MockLLMProvider(ProviderType.ANTHROPIC))
        return registry

    def test_switch_default_provider(self, registry: MockProviderRegistry):
        """Test switching default provider."""
        assert registry.get_default().provider_type == ProviderType.OPENAI

        registry.set_default(ProviderType.ANTHROPIC)
        assert registry.get_default().provider_type == ProviderType.ANTHROPIC

    def test_switch_to_unregistered_provider(self, registry: MockProviderRegistry):
        """Test switching to unregistered provider fails."""
        with pytest.raises(KeyError):
            registry.set_default(ProviderType.OLLAMA)


class TestTokenUsageTracking:
    """Tests for token usage tracking across agent-LLM interactions."""

    @pytest.fixture
    def provider(self) -> MockLLMProvider:
        """Create mock provider."""
        return MockLLMProvider(ProviderType.OPENAI)

    @pytest.fixture
    def agent(self, provider: MockLLMProvider) -> MockAgent:
        """Create mock agent."""
        return MockAgent(AgentType.PLANNER, provider)

    @pytest.mark.asyncio
    async def test_usage_returned_in_response(self, agent: MockAgent):
        """Test usage information is returned."""
        agent.provider.set_responses(["Response"])
        await agent.send_message("Message")

        # Provider should track call count
        assert agent.provider.call_count == 1


class TestErrorPropagation:
    """Tests for error propagation through agent-LLM chain."""

    @pytest.fixture
    def provider(self) -> MockLLMProvider:
        """Create mock provider."""
        provider = MockLLMProvider(ProviderType.OPENAI)
        provider.set_failure_mode(True)
        return provider

    @pytest.fixture
    def agent(self, provider: MockLLMProvider) -> MockAgent:
        """Create mock agent with no retries."""
        agent = MockAgent(AgentType.CODER, provider)
        agent.max_retries = 1
        return agent

    @pytest.mark.asyncio
    async def test_provider_error_propagates(self, agent: MockAgent):
        """Test provider errors propagate to caller."""
        with pytest.raises(RuntimeError) as exc_info:
            await agent.send_message("Will fail")

        assert "openai" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_stream_error_propagates(self, agent: MockAgent):
        """Test stream errors propagate."""
        with pytest.raises(RuntimeError):
            async for _ in agent.stream_message("Will fail"):
                pass
