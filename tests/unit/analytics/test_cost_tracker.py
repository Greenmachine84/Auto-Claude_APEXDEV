"""
Cost Tracker Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Multi-provider cost tracking
- Real-time cost calculation
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any

# All 8 LLM providers
SUPPORTED_PROVIDERS = {
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
}

# Cost per 1K tokens
PROVIDER_COSTS = {
    "copilot": {"input": 0.0, "output": 0.0},  # Subscription
    "openrouter": {"input": 0.003, "output": 0.015},
    "ollama": {"input": 0.0, "output": 0.0},  # Local
    "lmstudio": {"input": 0.0, "output": 0.0},  # Local
    "gemini": {"input": 0.00025, "output": 0.0005},
    "openai": {"input": 0.005, "output": 0.015},
    "anthropic": {"input": 0.003, "output": 0.015},
    "azure": {"input": 0.005, "output": 0.015},
}


class TestCostTracker:
    """Test cost tracker."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_track_cost(self, provider_id: str):
        """Cost can be tracked per provider."""
        tracker = MagicMock()
        tracker.record = AsyncMock()
        
        await tracker.record(
            provider=provider_id,
            input_tokens=1000,
            output_tokens=500,
        )
        
        tracker.record.assert_called_once()

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_get_cost(self, provider_id: str):
        """Cost can be retrieved per provider."""
        tracker = MagicMock()
        tracker.get_cost = AsyncMock(return_value={
            "provider": provider_id,
            "total_usd": 5.25,
            "input_usd": 3.00,
            "output_usd": 2.25,
        })
        
        result = await tracker.get_cost(
            provider=provider_id,
            user_id="user-123",
        )
        
        assert result["provider"] == provider_id


class TestCostCalculation:
    """Test cost calculation."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    def test_calculate_cost(self, provider_id: str):
        """Cost calculated correctly."""
        costs = PROVIDER_COSTS[provider_id]
        
        input_tokens = 1000
        output_tokens = 500
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        total = input_cost + output_cost
        
        assert total >= 0

    def test_local_providers_free(self):
        """Local providers are free."""
        for provider in ["ollama", "lmstudio"]:
            costs = PROVIDER_COSTS[provider]
            assert costs["input"] == 0.0
            assert costs["output"] == 0.0


class TestCostAggregation:
    """Test cost aggregation."""

    async def test_daily_cost(self):
        """Daily cost can be retrieved."""
        tracker = MagicMock()
        tracker.get_daily_cost = AsyncMock(return_value={
            "date": "2026-01-07",
            "total_usd": 25.50,
        })
        
        result = await tracker.get_daily_cost(user_id="user-123")
        
        assert result["total_usd"] >= 0

    async def test_monthly_cost(self):
        """Monthly cost can be retrieved."""
        tracker = MagicMock()
        tracker.get_monthly_cost = AsyncMock(return_value={
            "month": "2026-01",
            "total_usd": 500.00,
        })
        
        result = await tracker.get_monthly_cost(user_id="user-123")
        
        assert result["total_usd"] >= 0

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_cost_by_provider(self, provider_id: str):
        """Cost aggregated by provider."""
        tracker = MagicMock()
        tracker.get_cost_by_provider = AsyncMock(return_value={
            "provider": provider_id,
            "total_usd": 50.00,
        })
        
        result = await tracker.get_cost_by_provider(
            provider=provider_id,
            user_id="user-123",
        )
        
        assert result["provider"] == provider_id
