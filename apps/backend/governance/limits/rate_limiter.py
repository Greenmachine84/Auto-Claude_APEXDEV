"""
Rate Limiter - Phase 9 Implementation.

Provider-aware rate limiting with sliding window algorithm.

World-Class Standards:
- Sub-millisecond checks
- Per-provider limits
- Token and request tracking
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading
import logging

from ..models import RateLimit, RateLimitResult, SUPPORTED_PROVIDERS
from ..config import PROVIDER_RATE_LIMITS, get_provider_rate_limit


logger = logging.getLogger(__name__)


@dataclass
class WindowEntry:
    """Entry in sliding window."""
    timestamp: datetime
    count: int = 1
    tokens: int = 0


class SlidingWindow:
    """
    Sliding window for rate limiting.
    Thread-safe implementation.
    """
    
    def __init__(self, window_seconds: int = 60) -> None:
        self.window_seconds = window_seconds
        self._entries: deque = deque()
        self._lock = threading.Lock()
    
    def add(self, count: int = 1, tokens: int = 0) -> None:
        """Add entry to window."""
        with self._lock:
            now = datetime.utcnow()
            self._entries.append(WindowEntry(now, count, tokens))
            self._cleanup(now)
    
    def _cleanup(self, now: datetime) -> None:
        """Remove expired entries."""
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self._entries and self._entries[0].timestamp < cutoff:
            self._entries.popleft()
    
    def get_count(self) -> int:
        """Get current request count in window."""
        with self._lock:
            self._cleanup(datetime.utcnow())
            return sum(e.count for e in self._entries)
    
    def get_tokens(self) -> int:
        """Get current token count in window."""
        with self._lock:
            self._cleanup(datetime.utcnow())
            return sum(e.tokens for e in self._entries)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get window statistics."""
        with self._lock:
            self._cleanup(datetime.utcnow())
            return {
                "entries": len(self._entries),
                "count": sum(e.count for e in self._entries),
                "tokens": sum(e.tokens for e in self._entries),
            }


class RateLimiter:
    """
    Provider-aware rate limiter.
    
    Implements sliding window rate limiting with:
    - Per-provider limits
    - Request and token tracking
    - Configurable windows
    """
    
    def __init__(self) -> None:
        self._windows: Dict[str, Dict[str, SlidingWindow]] = {}
        self._limits: Dict[str, RateLimit] = {}
        self._lock = threading.Lock()
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize windows for all supported providers."""
        for provider in SUPPORTED_PROVIDERS:
            self._windows[provider] = {}
            rate_limit = get_provider_rate_limit(provider)
            self._limits[provider] = rate_limit
        logger.info(f"Initialized rate limiter for {len(SUPPORTED_PROVIDERS)} providers")
    
    def _get_window(
        self,
        provider: str,
        user_id: str,
        window_seconds: int = 60
    ) -> SlidingWindow:
        """Get or create sliding window for user."""
        key = f"{provider}:{user_id}"
        
        with self._lock:
            if user_id not in self._windows.get(provider, {}):
                if provider not in self._windows:
                    self._windows[provider] = {}
                self._windows[provider][user_id] = SlidingWindow(window_seconds)
        
        return self._windows[provider][user_id]
    
    def check(
        self,
        provider: str,
        user_id: str,
        tokens: int = 0
    ) -> RateLimitResult:
        """
        Check if request is within rate limits.
        
        Args:
            provider: Provider identifier
            user_id: User identifier
            tokens: Token count for request
            
        Returns:
            RateLimitResult with allowed status and details
        """
        if provider not in SUPPORTED_PROVIDERS:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=datetime.utcnow() + timedelta(seconds=60),
                reason=f"Unsupported provider: {provider}",
            )
        
        limit = self._limits.get(provider)
        if not limit:
            # No limit configured, allow
            return RateLimitResult(
                allowed=True,
                remaining=float("inf"),
                reset_at=datetime.utcnow() + timedelta(seconds=60),
            )
        
        window = self._get_window(provider, user_id, limit.window_seconds)
        current_count = window.get_count()
        current_tokens = window.get_tokens()
        
        # Check request limit
        if current_count >= limit.requests_per_minute:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=datetime.utcnow() + timedelta(seconds=limit.window_seconds),
                reason="Request limit exceeded",
                limit=limit.requests_per_minute,
            )
        
        # Check token limit
        if limit.tokens_per_minute and (current_tokens + tokens) > limit.tokens_per_minute:
            return RateLimitResult(
                allowed=False,
                remaining=limit.tokens_per_minute - current_tokens,
                reset_at=datetime.utcnow() + timedelta(seconds=limit.window_seconds),
                reason="Token limit exceeded",
                limit=limit.tokens_per_minute,
            )
        
        remaining = limit.requests_per_minute - current_count - 1
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_at=datetime.utcnow() + timedelta(seconds=limit.window_seconds),
            limit=limit.requests_per_minute,
        )
    
    def record(
        self,
        provider: str,
        user_id: str,
        tokens: int = 0
    ) -> None:
        """Record a request for rate limiting."""
        if provider not in SUPPORTED_PROVIDERS:
            return
        
        limit = self._limits.get(provider)
        window_seconds = limit.window_seconds if limit else 60
        
        window = self._get_window(provider, user_id, window_seconds)
        window.add(count=1, tokens=tokens)
    
    def check_and_record(
        self,
        provider: str,
        user_id: str,
        tokens: int = 0
    ) -> RateLimitResult:
        """Check rate limit and record if allowed."""
        result = self.check(provider, user_id, tokens)
        if result.allowed:
            self.record(provider, user_id, tokens)
        return result
    
    def get_usage(self, provider: str, user_id: str) -> Dict[str, Any]:
        """Get current usage stats for user."""
        if provider not in self._windows:
            return {"count": 0, "tokens": 0}
        
        if user_id not in self._windows[provider]:
            return {"count": 0, "tokens": 0}
        
        window = self._windows[provider][user_id]
        return window.get_stats()
    
    def reset(self, provider: str, user_id: str) -> None:
        """Reset rate limit for user."""
        if provider in self._windows:
            if user_id in self._windows[provider]:
                limit = self._limits.get(provider)
                window_seconds = limit.window_seconds if limit else 60
                self._windows[provider][user_id] = SlidingWindow(window_seconds)
    
    def set_limit(self, provider: str, limit: RateLimit) -> None:
        """Set custom rate limit for provider."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        self._limits[provider] = limit
    
    def get_all_usage(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get usage stats for all providers and users."""
        result = {}
        for provider in SUPPORTED_PROVIDERS:
            result[provider] = {}
            if provider in self._windows:
                for user_id, window in self._windows[provider].items():
                    result[provider][user_id] = window.get_stats()
        return result
