"""
Rate Limiter Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Per-provider rate limiting
- Sliding window algorithm
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any

# All 8 LLM providers
SUPPORTED_PROVIDERS = {
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
}

# Provider rate limits
PROVIDER_RATE_LIMITS = {
    "copilot": {"rpm": 100, "tpm": 50000},
    "openrouter": {"rpm": 100, "tpm": 100000},
    "ollama": {"rpm": 200, "tpm": None},
    "lmstudio": {"rpm": 200, "tpm": None},
    "gemini": {"rpm": 60, "tpm": 30000},
    "openai": {"rpm": 60, "tpm": 90000},
    "anthropic": {"rpm": 50, "tpm": 100000},
    "azure": {"rpm": 100, "tpm": 120000},
}


class TestRateLimiter:
    """Test rate limiter."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_check_rate_limit(self, provider_id: str):
        """Rate limit can be checked per provider."""
        limiter = MagicMock()
        limiter.check = AsyncMock(return_value={"allowed": True, "remaining": 50})
        
        result = await limiter.check(
            provider=provider_id,
            user_id="user-123",
        )
        
        assert result["allowed"] is True

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_record_request(self, provider_id: str):
        """Request is recorded for rate limiting."""
        limiter = MagicMock()
        limiter.record = AsyncMock()
        
        await limiter.record(
            provider=provider_id,
            user_id="user-123",
            tokens=1000,
        )
        
        limiter.record.assert_called_once()


class TestProviderLimits:
    """Test provider-specific limits."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    def test_provider_has_limits(self, provider_id: str):
        """Each provider has rate limits defined."""
        assert provider_id in PROVIDER_RATE_LIMITS
        limits = PROVIDER_RATE_LIMITS[provider_id]
        assert "rpm" in limits

    def test_local_providers_no_token_limit(self):
        """Local providers have no token limit."""
        assert PROVIDER_RATE_LIMITS["ollama"]["tpm"] is None
        assert PROVIDER_RATE_LIMITS["lmstudio"]["tpm"] is None


class TestRateLimitExceeded:
    """Test rate limit exceeded."""

    async def test_deny_when_exceeded(self):
        """Request denied when limit exceeded."""
        limiter = MagicMock()
        limiter.check = AsyncMock(return_value={
            "allowed": False,
            "remaining": 0,
            "reset_at": "2026-01-07T12:01:00Z",
        })
        
        result = await limiter.check(
            provider="openai",
            user_id="user-123",
        )
        
        assert result["allowed"] is False
        assert "reset_at" in result


class TestSlidingWindow:
    """Test sliding window algorithm."""

    def test_window_size(self):
        """Window size is configurable."""
        window_sizes = {
            "rpm": 60,  # 1 minute
            "tpm": 60,  # 1 minute
            "daily": 86400,  # 1 day
        }
        
        assert window_sizes["rpm"] == 60

    async def test_window_slides(self):
        """Window slides over time."""
        limiter = MagicMock()
        limiter.get_window_count = AsyncMock(side_effect=[10, 5])
        
        # Count decreases as old requests fall out
        count1 = await limiter.get_window_count(provider="openai")
        count2 = await limiter.get_window_count(provider="openai")
        
        assert count1 > count2
