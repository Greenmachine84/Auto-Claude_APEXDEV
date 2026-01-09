"""
Provider Metrics Tracker - Phase 8 Implementation.

Real-time health and performance monitoring per provider.

World-Class Standards:
- Sub-second metric collection
- Health status computation
- Alert threshold management
- Historical tracking
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..config import AnalyticsConfig, default_config
from ..models import SUPPORTED_PROVIDERS

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Provider health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class LatencyStats:
    """Latency statistics."""

    min_ms: float
    max_ms: float
    avg_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    sample_count: int


@dataclass
class ProviderHealth:
    """Health status for a provider."""

    provider: str
    status: HealthStatus
    latency: LatencyStats
    error_rate: float  # 0-1
    success_rate: float  # 0-1
    requests_per_minute: float
    last_request_at: str | None
    last_error_at: str | None
    issues: list[str]
    checked_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "status": self.status.value,
            "latency": {
                "min_ms": self.latency.min_ms,
                "max_ms": self.latency.max_ms,
                "avg_ms": self.latency.avg_ms,
                "p50_ms": self.latency.p50_ms,
                "p95_ms": self.latency.p95_ms,
                "p99_ms": self.latency.p99_ms,
                "sample_count": self.latency.sample_count,
            },
            "error_rate": self.error_rate,
            "success_rate": self.success_rate,
            "requests_per_minute": self.requests_per_minute,
            "last_request_at": self.last_request_at,
            "last_error_at": self.last_error_at,
            "issues": self.issues,
            "checked_at": self.checked_at,
        }


@dataclass
class ProviderMetric:
    """Single metric data point."""

    timestamp: datetime
    latency_ms: float
    success: bool
    tokens: int
    error_message: str | None = None


class ProviderMetricsTracker:
    """
    Real-time provider health monitoring.

    Features:
    - Latency percentile tracking
    - Error rate computation
    - Health status derivation
    - Automatic alerting
    """

    def __init__(
        self,
        config: AnalyticsConfig | None = None,
        window_minutes: int = 5,
    ) -> None:
        """Initialize metrics tracker."""
        self.config = config or default_config
        self.window_minutes = window_minutes

        # Metrics storage per provider
        self._metrics: dict[str, list[ProviderMetric]] = defaultdict(list)

        # Health thresholds
        self._thresholds = {
            "latency_warning_ms": 1000,
            "latency_critical_ms": 5000,
            "error_rate_warning": 0.05,
            "error_rate_critical": 0.20,
        }

        # Lock for thread safety
        self._lock = asyncio.Lock()

        logger.info(
            "ProviderMetricsTracker initialized with %d min window", window_minutes
        )

    async def record_request(
        self,
        provider: str,
        latency_ms: float,
        success: bool,
        tokens: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Record a request metric."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )

        metric = ProviderMetric(
            timestamp=datetime.utcnow(),
            latency_ms=latency_ms,
            success=success,
            tokens=tokens,
            error_message=error_message,
        )

        async with self._lock:
            self._metrics[provider].append(metric)

            # Cleanup old metrics
            cutoff = datetime.utcnow() - timedelta(minutes=self.window_minutes * 2)
            self._metrics[provider] = [
                m for m in self._metrics[provider] if m.timestamp > cutoff
            ]

    async def get_health(self, provider: str) -> ProviderHealth:
        """Get health status for a provider."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )

        async with self._lock:
            metrics = self._metrics.get(provider, [])

        # Filter to window
        cutoff = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        recent = [m for m in metrics if m.timestamp > cutoff]

        if not recent:
            return ProviderHealth(
                provider=provider,
                status=HealthStatus.UNKNOWN,
                latency=LatencyStats(0, 0, 0, 0, 0, 0, 0),
                error_rate=0.0,
                success_rate=1.0,
                requests_per_minute=0.0,
                last_request_at=None,
                last_error_at=None,
                issues=["No recent data"],
            )

        # Calculate latency stats
        latencies = sorted([m.latency_ms for m in recent])
        latency_stats = LatencyStats(
            min_ms=latencies[0],
            max_ms=latencies[-1],
            avg_ms=sum(latencies) / len(latencies),
            p50_ms=self._percentile(latencies, 50),
            p95_ms=self._percentile(latencies, 95),
            p99_ms=self._percentile(latencies, 99),
            sample_count=len(latencies),
        )

        # Calculate rates
        success_count = sum(1 for m in recent if m.success)
        error_count = len(recent) - success_count
        error_rate = error_count / len(recent)
        success_rate = success_count / len(recent)

        # Requests per minute
        window_seconds = self.window_minutes * 60
        rpm = len(recent) / (window_seconds / 60)

        # Find last request and error times
        last_request = max(recent, key=lambda m: m.timestamp)
        errors = [m for m in recent if not m.success]
        last_error = max(errors, key=lambda m: m.timestamp) if errors else None

        # Determine health status and issues
        status, issues = self._compute_status(latency_stats, error_rate)

        return ProviderHealth(
            provider=provider,
            status=status,
            latency=latency_stats,
            error_rate=error_rate,
            success_rate=success_rate,
            requests_per_minute=rpm,
            last_request_at=last_request.timestamp.isoformat(),
            last_error_at=last_error.timestamp.isoformat() if last_error else None,
            issues=issues,
        )

    async def get_all_health(self) -> dict[str, ProviderHealth]:
        """Get health status for all providers."""
        results = {}
        for provider in SUPPORTED_PROVIDERS:
            results[provider] = await self.get_health(provider)
        return results

    def _percentile(self, sorted_data: list[float], p: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0

        k = (len(sorted_data) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f

        return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)

    def _compute_status(
        self,
        latency: LatencyStats,
        error_rate: float,
    ) -> tuple[HealthStatus, list[str]]:
        """Compute health status and issues."""
        issues = []
        status = HealthStatus.HEALTHY

        # Check latency
        if latency.p99_ms >= self._thresholds["latency_critical_ms"]:
            issues.append(f"Critical latency: P99={latency.p99_ms:.0f}ms")
            status = HealthStatus.UNHEALTHY
        elif latency.p95_ms >= self._thresholds["latency_warning_ms"]:
            issues.append(f"High latency: P95={latency.p95_ms:.0f}ms")
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.DEGRADED

        # Check error rate
        if error_rate >= self._thresholds["error_rate_critical"]:
            issues.append(f"Critical error rate: {error_rate * 100:.1f}%")
            status = HealthStatus.UNHEALTHY
        elif error_rate >= self._thresholds["error_rate_warning"]:
            issues.append(f"High error rate: {error_rate * 100:.1f}%")
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.DEGRADED

        if not issues:
            issues.append("All metrics within normal range")

        return status, issues

    def set_threshold(self, name: str, value: float) -> None:
        """Set a health threshold."""
        if name in self._thresholds:
            self._thresholds[name] = value
            logger.info("Threshold %s set to %s", name, value)
        else:
            raise ValueError(f"Unknown threshold: {name}")

    async def get_summary(self) -> dict[str, Any]:
        """Get summary of all provider health."""
        all_health = await self.get_all_health()

        healthy_count = sum(
            1 for h in all_health.values() if h.status == HealthStatus.HEALTHY
        )
        degraded_count = sum(
            1 for h in all_health.values() if h.status == HealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1 for h in all_health.values() if h.status == HealthStatus.UNHEALTHY
        )

        return {
            "total_providers": len(SUPPORTED_PROVIDERS),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "unknown": len(SUPPORTED_PROVIDERS)
            - healthy_count
            - degraded_count
            - unhealthy_count,
            "providers": {
                provider: health.to_dict() for provider, health in all_health.items()
            },
            "checked_at": datetime.utcnow().isoformat(),
        }
