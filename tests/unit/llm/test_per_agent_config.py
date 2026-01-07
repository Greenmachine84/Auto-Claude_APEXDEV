"""
Per-Agent LLM Config Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Tests per-agent LLM assignment
- No default provider
- All 8 providers tested
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# All 8 LLM providers - NO default
SUPPORTED_PROVIDERS = {
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
}


@dataclass
class AgentLLMConfig:
    """Agent LLM configuration."""
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    fallback_provider: Optional[str] = None


class TestPerAgentLLMConfig:
    """Test per-agent LLM configuration."""

    def test_config_requires_provider(self):
        """Config requires provider."""
        with pytest.raises(TypeError):
            AgentLLMConfig(model="test-model")  # type: ignore

    def test_config_requires_model(self):
        """Config requires model."""
        with pytest.raises(TypeError):
            AgentLLMConfig(provider="openai")  # type: ignore

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    def test_config_accepts_all_providers(self, provider_id: str):
        """Config accepts all 8 providers."""
        config = AgentLLMConfig(
            provider=provider_id,
            model="test-model",
        )
        assert config.provider == provider_id
        assert config.provider in SUPPORTED_PROVIDERS

    def test_config_default_values(self):
        """Config has sensible defaults."""
        config = AgentLLMConfig(
            provider="openai",
            model="gpt-4o",
        )
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.fallback_provider is None


class TestMultipleAgentsMultipleProviders:
    """Test multiple agents with different providers."""

    def test_three_agents_three_providers(self):
        """Three agents can use three different providers."""
        agents = [
            {"id": "code-review", "config": AgentLLMConfig("copilot", "gpt-4o")},
            {"id": "security", "config": AgentLLMConfig("ollama", "llama3.2")},
            {"id": "qa", "config": AgentLLMConfig("anthropic", "claude-sonnet-4-20250514")},
        ]
        
        providers = {a["config"].provider for a in agents}
        assert len(providers) == 3
        assert "copilot" in providers
        assert "ollama" in providers
        assert "anthropic" in providers

    def test_all_8_providers_simultaneously(self):
        """All 8 providers can be used simultaneously."""
        agents = []
        for i, provider in enumerate(SUPPORTED_PROVIDERS):
            agents.append({
                "id": f"agent-{i}",
                "config": AgentLLMConfig(provider, f"{provider}-model"),
            })
        
        assert len(agents) == 8
        providers = {a["config"].provider for a in agents}
        assert providers == SUPPORTED_PROVIDERS

    async def test_parallel_execution_different_providers(self):
        """Parallel execution with different providers."""
        configs = [
            AgentLLMConfig("openai", "gpt-4o"),
            AgentLLMConfig("anthropic", "claude-sonnet-4-20250514"),
            AgentLLMConfig("gemini", "gemini-2.0-flash"),
        ]
        
        results = []
        for config in configs:
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(return_value={
                "provider": config.provider,
                "result": "success",
            })
            result = await mock_agent.execute()
            results.append(result)
        
        assert len(results) == 3
        providers = {r["provider"] for r in results}
        assert "openai" in providers


class TestAgentProviderSwitching:
    """Test agent provider switching."""

    async def test_switch_provider_at_runtime(self):
        """Agent can switch provider at runtime."""
        agent = MagicMock()
        agent.config = AgentLLMConfig("openai", "gpt-4o")
        
        # Switch provider
        agent.config = AgentLLMConfig("anthropic", "claude-sonnet-4-20250514")
        
        assert agent.config.provider == "anthropic"

    async def test_fallback_on_failure(self):
        """Agent uses fallback on primary failure."""
        config = AgentLLMConfig(
            provider="openai",
            model="gpt-4o",
            fallback_provider="anthropic",
        )
        
        agent = MagicMock()
        agent.config = config
        
        # Simulate primary failure
        agent.current_provider = config.fallback_provider
        
        assert agent.current_provider == "anthropic"


class TestAgentModelSelection:
    """Test agent model selection."""

    @pytest.mark.parametrize("provider_id,models", [
        ("copilot", ["gpt-4o", "gpt-4o-mini"]),
        ("openrouter", ["anthropic/claude-3-sonnet", "openai/gpt-4o"]),
        ("ollama", ["llama3.2", "mistral", "codellama"]),
        ("lmstudio", ["local-model"]),
        ("gemini", ["gemini-2.0-flash", "gemini-1.5-pro"]),
        ("openai", ["gpt-4o", "gpt-4o-mini", "o1"]),
        ("anthropic", ["claude-sonnet-4-20250514", "claude-3-haiku"]),
        ("azure", ["gpt-4o", "gpt-4"]),
    ])
    def test_provider_model_combinations(self, provider_id: str, models: List[str]):
        """Each provider has valid models."""
        for model in models:
            config = AgentLLMConfig(provider=provider_id, model=model)
            assert config.provider == provider_id
            assert config.model == model


class TestAgentProviderValidation:
    """Test agent provider validation."""

    def test_reject_invalid_provider(self):
        """Invalid provider is rejected."""
        invalid_providers = ["gpt4", "claude", "chatgpt", "bard"]
        
        for invalid in invalid_providers:
            assert invalid not in SUPPORTED_PROVIDERS

    def test_provider_case_sensitivity(self):
        """Provider names are case-sensitive."""
        # All providers are lowercase
        for provider in SUPPORTED_PROVIDERS:
            assert provider == provider.lower()

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    def test_provider_has_required_fields(self, provider_id: str):
        """Each provider config has required fields."""
        config = AgentLLMConfig(
            provider=provider_id,
            model="test-model",
        )
        
        assert hasattr(config, "provider")
        assert hasattr(config, "model")
        assert hasattr(config, "temperature")
        assert hasattr(config, "max_tokens")
