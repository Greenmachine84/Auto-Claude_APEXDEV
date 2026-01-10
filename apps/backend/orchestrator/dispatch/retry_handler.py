"""Retry handler.

Handles task retries.

Capabilities:
- Configurable retries
- Exponential backoff
- Jitter
- Circuit breaker
"""

import asyncio
import logging
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Retry configuration."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1


@dataclass
class RetryAttempt:
    """Record of a retry attempt."""

    attempt: int
    timestamp: datetime
    error: str
    delay: float


class RetryHandler:
    """Handle retries with backoff.

    Example:
        handler = RetryHandler()
        result = await handler.execute(async_func, max_retries=3)
    """

    def __init__(self, config: RetryConfig | None = None):
        """Initialize handler."""
        self.config = config or RetryConfig()
        self._attempts: list[RetryAttempt] = []

        logger.debug("RetryHandler initialized")

    async def execute(
        self,
        func: Callable[[], T],
        max_retries: int | None = None,
        retryable_errors: list[type] | None = None,
    ) -> T:
        """Execute with retries."""
        max_retries = (
            max_retries if max_retries is not None else self.config.max_retries
        )
        retryable = retryable_errors or [Exception]

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # Execute function
                result = func()
                if asyncio.iscoroutine(result):
                    result = await result
                return result

            except tuple(retryable) as e:
                last_error = e

                if attempt >= max_retries:
                    logger.warning(f"Max retries ({max_retries}) exceeded")
                    raise

                # Calculate delay
                delay = self._calculate_delay(attempt)

                # Record attempt
                self._attempts.append(
                    RetryAttempt(
                        attempt=attempt + 1,
                        timestamp=datetime.now(),
                        error=str(e),
                        delay=delay,
                    )
                )

                logger.debug(
                    f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s: {e}"
                )

                await asyncio.sleep(delay)

        raise last_error

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate backoff delay."""
        # Exponential backoff
        delay = self.config.base_delay * (self.config.exponential_base**attempt)

        # Cap at max delay
        delay = min(delay, self.config.max_delay)

        # Add jitter
        if self.config.jitter:
            jitter = delay * self.config.jitter_factor
            delay += random.uniform(-jitter, jitter)

        return max(0, delay)

    def get_attempts(self) -> list[RetryAttempt]:
        """Get retry attempts."""
        return self._attempts.copy()

    def clear_attempts(self) -> None:
        """Clear retry attempts."""
        self._attempts.clear()


class CircuitBreaker:
    """Circuit breaker for failures.

    Prevents cascading failures.

    Example:
        breaker = CircuitBreaker(failure_threshold=5)
        if breaker.is_closed:
            result = await func()
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_time: float = 30.0,
    ):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time

        self._failure_count = 0
        self._last_failure: datetime | None = None
        self._state = "closed"  # closed, open, half-open

        logger.debug("CircuitBreaker initialized")

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        self._check_recovery()
        return self._state == "closed"

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing)."""
        self._check_recovery()
        return self._state == "open"

    def record_success(self) -> None:
        """Record successful call."""
        self._failure_count = 0
        self._state = "closed"

    def record_failure(self) -> None:
        """Record failed call."""
        self._failure_count += 1
        self._last_failure = datetime.now()

        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning("Circuit breaker opened")

    def _check_recovery(self) -> None:
        """Check if recovery time has passed."""
        if self._state == "open" and self._last_failure:
            elapsed = (datetime.now() - self._last_failure).total_seconds()
            if elapsed >= self.recovery_time:
                self._state = "half-open"
                logger.info("Circuit breaker half-open")

    def reset(self) -> None:
        """Reset circuit breaker."""
        self._failure_count = 0
        self._last_failure = None
        self._state = "closed"
