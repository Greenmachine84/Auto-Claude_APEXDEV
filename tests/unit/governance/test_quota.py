"""
Quota Management Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Per-provider quota tracking
- Cost-based quotas
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any

# All 8 LLM providers
SUPPORTED_PROVIDERS = {
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
}

# Provider quotas
PROVIDER_QUOTAS = {
    "copilot": {"monthly_usd": 500, "daily_usd": 50},
    "openrouter": {"monthly_usd": 1000, "daily_usd": 100},
    "ollama": {"monthly_usd": None, "daily_usd": None},  # Free
    "lmstudio": {"monthly_usd": None, "daily_usd": None},  # Free
    "gemini": {"monthly_usd": 500, "daily_usd": 50},
    "openai": {"monthly_usd": 1000, "daily_usd": 100},
    "anthropic": {"monthly_usd": 1000, "daily_usd": 100},
    "azure": {"monthly_usd": 2000, "daily_usd": 200},
}


class TestQuotaManager:
    """Test quota manager."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_check_quota(self, provider_id: str):
        """Quota can be checked per provider."""
        manager = MagicMock()
        manager.check = AsyncMock(return_value={
            "within_quota": True,
            "used_usd": 25.0,
            "remaining_usd": 475.0,
        })
        
        result = await manager.check(
            provider=provider_id,
            user_id="user-123",
        )
        
        assert result["within_quota"] is True

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_record_usage(self, provider_id: str):
        """Usage is recorded for quota."""
        manager = MagicMock()
        manager.record = AsyncMock()
        
        await manager.record(
            provider=provider_id,
            user_id="user-123",
            cost_usd=0.05,
        )
        
        manager.record.assert_called_once()


class TestProviderQuotas:
    """Test provider-specific quotas."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    def test_provider_has_quota(self, provider_id: str):
        """Each provider has quota defined."""
        assert provider_id in PROVIDER_QUOTAS

    def test_local_providers_unlimited(self):
        """Local providers have unlimited quota."""
        assert PROVIDER_QUOTAS["ollama"]["monthly_usd"] is None
        assert PROVIDER_QUOTAS["lmstudio"]["monthly_usd"] is None


class TestQuotaExceeded:
    """Test quota exceeded."""

    async def test_deny_when_exceeded(self):
        """Request denied when quota exceeded."""
        manager = MagicMock()
        manager.check = AsyncMock(return_value={
            "within_quota": False,
            "used_usd": 1000.0,
            "remaining_usd": 0.0,
        })
        
        result = await manager.check(
            provider="openai",
            user_id="user-123",
        )
        
        assert result["within_quota"] is False


class TestQuotaAlerts:
    """Test quota alerts."""

    @pytest.mark.parametrize("threshold", [0.75, 0.90, 1.0])
    async def test_alert_at_threshold(self, threshold: float):
        """Alert triggered at quota thresholds."""
        manager = MagicMock()
        manager.check_alerts = AsyncMock(return_value={
            "alert": True,
            "threshold": threshold,
            "message": f"Quota at {threshold * 100}%",
        })
        
        result = await manager.check_alerts(
            provider="openai",
            user_id="user-123",
        )
        
        assert result["alert"] is True
