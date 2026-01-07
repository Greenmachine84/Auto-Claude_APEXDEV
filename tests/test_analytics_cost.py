"""
Analytics Cost Tests - Phase 8.

Tests for cost tracking, pricing, and budget management.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from apps.backend.analytics.models import CostRecord
from apps.backend.analytics.cost.pricing import PricingEngine, PROVIDER_PRICING
from apps.backend.analytics.cost.cost_tracker import CostTracker
from apps.backend.analytics.cost.budget_manager import BudgetManager
from apps.backend.analytics.cost.cost_report import CostReportGenerator


class TestProviderPricing:
    """Test provider pricing configuration."""
    
    def test_all_8_providers_defined(self):
        """Test all 8 providers have pricing."""
        required = ["copilot", "openrouter", "ollama", "lmstudio",
                    "gemini", "openai", "anthropic", "azure"]
        
        for provider in required:
            assert provider in PROVIDER_PRICING, f"Missing: {provider}"
    
    def test_local_providers_free(self):
        """Test local providers (ollama, lmstudio) are free."""
        for provider in ["ollama", "lmstudio"]:
            pricing = PROVIDER_PRICING[provider]
            default = pricing.get("default", (0.0, 0.0))
            assert default[0] == 0.0
            assert default[1] == 0.0
    
    def test_copilot_subscription_based(self):
        """Test copilot is subscription-based (no per-token cost)."""
        pricing = PROVIDER_PRICING["copilot"]
        default = pricing.get("default", (0.0, 0.0))
        assert default[0] == 0.0


class TestPricingEngine:
    """Test PricingEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create pricing engine."""
        return PricingEngine()
    
    def test_calculate_openai_cost(self, engine):
        """Test OpenAI cost calculation."""
        cost = engine.calculate_cost(
            provider="openai",
            model="gpt-4o",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        
        # gpt-4o: $5/1M input, $15/1M output
        expected = (1000 / 1_000_000) * 5.0 + (500 / 1_000_000) * 15.0
        assert abs(cost - expected) < 0.000001
    
    def test_calculate_anthropic_cost(self, engine):
        """Test Anthropic cost calculation."""
        cost = engine.calculate_cost(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        
        # claude-sonnet-4: $3/1M input, $15/1M output
        expected = (1000 / 1_000_000) * 3.0 + (500 / 1_000_000) * 15.0
        assert abs(cost - expected) < 0.000001
    
    def test_calculate_gemini_cost(self, engine):
        """Test Gemini cost calculation."""
        cost = engine.calculate_cost(
            provider="gemini",
            model="gemini-1.5-pro",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        assert cost > 0
    
    def test_calculate_azure_cost(self, engine):
        """Test Azure cost calculation."""
        cost = engine.calculate_cost(
            provider="azure",
            model="gpt-4o",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        assert cost > 0
    
    def test_calculate_openrouter_cost(self, engine):
        """Test OpenRouter cost calculation."""
        cost = engine.calculate_cost(
            provider="openrouter",
            model="anthropic/claude-3-opus",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        assert cost > 0
    
    def test_local_providers_zero_cost(self, engine):
        """Test local providers have zero cost."""
        for provider in ["ollama", "lmstudio"]:
            cost = engine.calculate_cost(
                provider=provider,
                model="llama3",
                prompt_tokens=10000,
                completion_tokens=5000,
            )
            assert cost == 0.0
    
    def test_unknown_model_uses_default(self, engine):
        """Test unknown model uses default pricing."""
        cost = engine.calculate_cost(
            provider="openai",
            model="unknown-model-xyz",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        # Should use default pricing, not raise error
        assert cost >= 0
    
    def test_cost_accuracy_within_threshold(self, engine):
        """Test cost calculation accuracy (<0.1% error target)."""
        # Test with known values
        cost = engine.calculate_cost(
            provider="openai",
            model="gpt-4o",
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000,
        )
        
        # Expected: $5 + $15 = $20
        expected = 20.0
        error_rate = abs(cost - expected) / expected
        assert error_rate < 0.001  # <0.1% error


class TestCostTracker:
    """Test CostTracker."""
    
    @pytest.fixture
    def tracker(self):
        """Create cost tracker."""
        return CostTracker()
    
    @pytest.mark.asyncio
    async def test_track_request(self, tracker):
        """Test tracking a request."""
        await tracker.track(
            user_id="user-001",
            provider="openai",
            model="gpt-4o",
            prompt_tokens=100,
            completion_tokens=50,
        )
        
        summary = await tracker.get_summary("user-001")
        assert summary["total_requests"] >= 1
    
    @pytest.mark.asyncio
    async def test_track_all_providers(self, tracker):
        """Test tracking requests for all 8 providers."""
        providers = ["copilot", "openrouter", "ollama", "lmstudio",
                     "gemini", "openai", "anthropic", "azure"]
        
        for provider in providers:
            await tracker.track(
                user_id="user-all",
                provider=provider,
                model="default",
                prompt_tokens=100,
                completion_tokens=50,
            )
        
        breakdown = await tracker.get_provider_breakdown("user-all")
        assert len(breakdown) == 8
    
    @pytest.mark.asyncio
    async def test_cost_calculation_speed(self, tracker):
        """Test cost calculation performance (<1ms target)."""
        import time
        
        start = time.perf_counter()
        for _ in range(1000):
            tracker._calculate_cost("openai", "gpt-4o", 100, 50)
        duration = time.perf_counter() - start
        
        # 1000 calculations in <1 second means <1ms each
        assert duration < 1.0


class TestBudgetManager:
    """Test BudgetManager."""
    
    @pytest.fixture
    def manager(self):
        """Create budget manager."""
        return BudgetManager()
    
    @pytest.mark.asyncio
    async def test_set_budget(self, manager):
        """Test setting a budget."""
        await manager.set_budget(
            user_id="user-001",
            monthly_limit=100.0,
            daily_limit=10.0,
        )
        
        budget = await manager.get_budget("user-001")
        assert budget["monthly_limit"] == 100.0
        assert budget["daily_limit"] == 10.0
    
    @pytest.mark.asyncio
    async def test_check_budget_ok(self, manager):
        """Test budget check passes when under limit."""
        await manager.set_budget("user-002", monthly_limit=100.0)
        
        result = await manager.check_budget("user-002", cost=10.0)
        assert result["allowed"] is True
    
    @pytest.mark.asyncio
    async def test_check_budget_exceeded(self, manager):
        """Test budget check fails when over limit."""
        await manager.set_budget("user-003", monthly_limit=10.0)
        await manager.record_spend("user-003", 10.0)
        
        result = await manager.check_budget("user-003", cost=5.0)
        assert result["allowed"] is False
    
    @pytest.mark.asyncio
    async def test_budget_alert(self, manager):
        """Test budget alert at threshold."""
        alerts = []
        manager.add_alert_callback(lambda a: alerts.append(a))
        
        await manager.set_budget("user-004", monthly_limit=100.0, alert_threshold=0.8)
        await manager.record_spend("user-004", 85.0)
        
        assert len(alerts) > 0


class TestCostReportGenerator:
    """Test CostReportGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create report generator."""
        return CostReportGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_json_report(self, generator):
        """Test JSON report generation."""
        report = await generator.generate(
            user_id="user-001",
            format="json",
            days=30,
        )
        
        assert "total_cost" in report
        assert "by_provider" in report
    
    @pytest.mark.asyncio
    async def test_generate_csv_report(self, generator):
        """Test CSV report generation."""
        csv_data = await generator.generate(
            user_id="user-001",
            format="csv",
            days=30,
        )
        
        assert isinstance(csv_data, str)
        assert "provider" in csv_data.lower()
    
    @pytest.mark.asyncio
    async def test_provider_comparison_report(self, generator):
        """Test provider comparison in report."""
        report = await generator.generate(
            user_id="user-001",
            format="json",
            include_comparison=True,
        )
        
        assert "comparison" in report or "by_provider" in report
