"""
Throttle - Phase 9 Implementation.

Request throttling and backpressure management.

World-Class Standards:
- Adaptive throttling
- Priority queuing
- Backpressure handling
"""

import asyncio
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum

from ..models import SUPPORTED_PROVIDERS

logger = logging.getLogger(__name__)


class ThrottleState(Enum):
    """Throttle states."""

    NORMAL = "normal"
    THROTTLED = "throttled"
    BLOCKED = "blocked"


class Priority(Enum):
    """Request priorities."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ThrottleConfig:
    """Throttle configuration."""

    max_concurrent: int = 10
    max_queue_size: int = 100
    timeout_seconds: float = 30.0
    backoff_factor: float = 1.5
    max_backoff_seconds: float = 60.0


@dataclass
class ThrottleStats:
    """Throttle statistics."""

    provider: str
    state: ThrottleState
    current_concurrent: int
    queue_size: int
    total_requests: int
    throttled_requests: int
    average_wait_ms: float


class Throttle:
    """
    Request throttler with backpressure.

    Implements:
    - Concurrent request limiting
    - Priority queuing
    - Adaptive backoff
    """

    def __init__(self, config: ThrottleConfig | None = None) -> None:
        self.config = config or ThrottleConfig()
        self._semaphores: dict[str, threading.Semaphore] = {}
        self._queues: dict[str, list] = {}
        self._states: dict[str, ThrottleState] = {}
        self._backoff: dict[str, float] = {}
        self._stats: dict[str, dict[str, int]] = {}
        self._lock = threading.Lock()
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize throttles for all providers."""
        for provider in SUPPORTED_PROVIDERS:
            self._semaphores[provider] = threading.Semaphore(self.config.max_concurrent)
            self._queues[provider] = []
            self._states[provider] = ThrottleState.NORMAL
            self._backoff[provider] = 0.0
            self._stats[provider] = {
                "total": 0,
                "throttled": 0,
                "total_wait_ms": 0,
            }
        logger.info(f"Initialized throttle for {len(SUPPORTED_PROVIDERS)} providers")

    def acquire(
        self,
        provider: str,
        priority: Priority = Priority.NORMAL,
        timeout: float | None = None,
    ) -> bool:
        """
        Acquire throttle slot.

        Args:
            provider: Provider identifier
            priority: Request priority
            timeout: Optional timeout override

        Returns:
            True if acquired, False if timed out
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        timeout = timeout or self.config.timeout_seconds
        start_time = time.time()

        # Apply backoff if throttled
        backoff = self._backoff.get(provider, 0.0)
        if backoff > 0:
            if priority.value < Priority.CRITICAL.value:
                time.sleep(min(backoff, timeout))

        # Try to acquire semaphore
        semaphore = self._semaphores[provider]
        acquired = semaphore.acquire(timeout=timeout)

        wait_ms = (time.time() - start_time) * 1000

        with self._lock:
            self._stats[provider]["total"] += 1
            self._stats[provider]["total_wait_ms"] += wait_ms

            if not acquired:
                self._stats[provider]["throttled"] += 1

        if not acquired:
            self._states[provider] = ThrottleState.THROTTLED
            logger.warning(f"Throttle timeout for provider: {provider}")

        return acquired

    def release(self, provider: str) -> None:
        """Release throttle slot."""
        if provider not in self._semaphores:
            return

        self._semaphores[provider].release()

        # Reduce backoff on successful completion
        with self._lock:
            if self._backoff.get(provider, 0) > 0:
                self._backoff[provider] = max(
                    0, self._backoff[provider] / self.config.backoff_factor
                )
                if self._backoff[provider] < 0.1:
                    self._backoff[provider] = 0
                    self._states[provider] = ThrottleState.NORMAL

    def record_error(self, provider: str) -> None:
        """Record error and increase backoff."""
        if provider not in SUPPORTED_PROVIDERS:
            return

        with self._lock:
            current = self._backoff.get(provider, 0.0)
            if current == 0:
                self._backoff[provider] = 1.0
            else:
                self._backoff[provider] = min(
                    current * self.config.backoff_factor,
                    self.config.max_backoff_seconds,
                )

            self._states[provider] = ThrottleState.THROTTLED

        logger.info(f"Increased backoff for {provider}: {self._backoff[provider]:.1f}s")

    def get_state(self, provider: str) -> ThrottleState:
        """Get current throttle state."""
        return self._states.get(provider, ThrottleState.NORMAL)

    def get_stats(self, provider: str) -> ThrottleStats:
        """Get throttle statistics."""
        stats = self._stats.get(provider, {})
        total = stats.get("total", 0)
        avg_wait = stats.get("total_wait_ms", 0) / max(1, total)

        return ThrottleStats(
            provider=provider,
            state=self._states.get(provider, ThrottleState.NORMAL),
            current_concurrent=self.config.max_concurrent
            - self._semaphores[provider]._value,
            queue_size=len(self._queues.get(provider, [])),
            total_requests=total,
            throttled_requests=stats.get("throttled", 0),
            average_wait_ms=avg_wait,
        )

    def is_healthy(self, provider: str) -> bool:
        """Check if provider is healthy (not blocked)."""
        state = self._states.get(provider, ThrottleState.NORMAL)
        return state != ThrottleState.BLOCKED

    def set_blocked(self, provider: str, blocked: bool = True) -> None:
        """Set provider blocked state."""
        if provider not in SUPPORTED_PROVIDERS:
            return

        if blocked:
            self._states[provider] = ThrottleState.BLOCKED
            logger.warning(f"Provider blocked: {provider}")
        else:
            self._states[provider] = ThrottleState.NORMAL
            self._backoff[provider] = 0.0

    def reset(self, provider: str) -> None:
        """Reset throttle for provider."""
        if provider not in SUPPORTED_PROVIDERS:
            return

        with self._lock:
            self._semaphores[provider] = threading.Semaphore(self.config.max_concurrent)
            self._states[provider] = ThrottleState.NORMAL
            self._backoff[provider] = 0.0
            self._stats[provider] = {
                "total": 0,
                "throttled": 0,
                "total_wait_ms": 0,
            }

    def get_all_stats(self) -> dict[str, ThrottleStats]:
        """Get statistics for all providers."""
        return {provider: self.get_stats(provider) for provider in SUPPORTED_PROVIDERS}


class AsyncThrottle:
    """
    Async version of throttle.
    """

    def __init__(self, config: ThrottleConfig | None = None) -> None:
        self.config = config or ThrottleConfig()
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self._states: dict[str, ThrottleState] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure semaphores are initialized."""
        if self._initialized:
            return

        for provider in SUPPORTED_PROVIDERS:
            self._semaphores[provider] = asyncio.Semaphore(self.config.max_concurrent)
            self._states[provider] = ThrottleState.NORMAL
        self._initialized = True

    async def acquire(
        self, provider: str, priority: Priority = Priority.NORMAL
    ) -> bool:
        """Acquire throttle slot asynchronously."""
        self._ensure_initialized()

        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        try:
            await asyncio.wait_for(
                self._semaphores[provider].acquire(),
                timeout=self.config.timeout_seconds,
            )
            return True
        except asyncio.TimeoutError:
            self._states[provider] = ThrottleState.THROTTLED
            return False

    def release(self, provider: str) -> None:
        """Release throttle slot."""
        if provider in self._semaphores:
            self._semaphores[provider].release()
