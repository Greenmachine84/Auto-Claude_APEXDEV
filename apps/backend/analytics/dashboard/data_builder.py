"""
Dashboard Data Builder - Phase 8 Implementation.

Aggregates data from multiple sources for dashboard display.

World-Class Standards:
- <100ms P99 API latency
- Real-time data aggregation
- Caching for performance
- Provider-agnostic design
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..config import AnalyticsConfig, default_config
from ..cost.budget_manager import BudgetManager
from ..cost.cost_tracker import CostTracker
from ..metrics.aggregator import MetricsAggregator
from ..metrics.collector import MetricsCollector
from ..models import (
    SUPPORTED_PROVIDERS,
    DashboardData,
    ProviderUsageMetrics,
    TimeSeriesPoint,
)

logger = logging.getLogger(__name__)


@dataclass
class DashboardCache:
    """Cached dashboard data."""

    data: DashboardData
    timestamp: datetime
    ttl_seconds: int = 60

    @property
    def is_valid(self) -> bool:
        """Check if cache is still valid."""
        elapsed = (datetime.utcnow() - self.timestamp).total_seconds()
        return elapsed < self.ttl_seconds


class DashboardDataBuilder:
    """
    Builds comprehensive dashboard data.

    Features:
    - Multi-source aggregation
    - Intelligent caching
    - Real-time updates
    - Provider comparison
    """

    def __init__(
        self,
        metrics_collector: MetricsCollector,
        metrics_aggregator: MetricsAggregator,
        cost_tracker: CostTracker,
        budget_manager: BudgetManager,
        config: AnalyticsConfig | None = None,
    ) -> None:
        """Initialize dashboard data builder."""
        self.metrics = metrics_collector
        self.aggregator = metrics_aggregator
        self.costs = cost_tracker
        self.budgets = budget_manager
        self.config = config or default_config

        # Cache storage
        self._cache: dict[str, DashboardCache] = {}

        logger.info("DashboardDataBuilder initialized")

    async def build_dashboard(
        self,
        user_id: str,
        time_range_hours: int = 24,
        use_cache: bool = True,
    ) -> DashboardData:
        """
        Build complete dashboard data for a user.

        Args:
            user_id: User identifier
            time_range_hours: Hours of data to include
            use_cache: Whether to use cached data

        Returns:
            Complete dashboard data
        """
        cache_key = f"{user_id}:{time_range_hours}"

        # Check cache
        if use_cache and cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached.is_valid:
                logger.debug("Returning cached dashboard for %s", user_id)
                return cached.data

        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)

        # Gather data in parallel
        (
            cost_summary,
            budget_status,
            provider_metrics,
            time_series,
        ) = await asyncio.gather(
            self.costs.get_user_cost(user_id, start_time=start_time),
            self.budgets.check_budget(user_id),
            self._build_provider_metrics(user_id, start_time),
            self._build_time_series(user_id, start_time),
        )

        # Build dashboard data
        dashboard = DashboardData(
            user_id=user_id,
            time_range_hours=time_range_hours,
            total_cost=cost_summary.total_cost,
            total_requests=cost_summary.request_count,
            total_tokens=cost_summary.total_prompt_tokens
            + cost_summary.total_completion_tokens,
            provider_metrics=provider_metrics,
            cost_time_series=time_series,
            budget_status=budget_status,
            last_updated=datetime.utcnow().isoformat(),
        )

        # Cache result
        self._cache[cache_key] = DashboardCache(
            data=dashboard,
            timestamp=datetime.utcnow(),
            ttl_seconds=self.config.dashboard.cache_ttl_seconds,
        )

        return dashboard

    async def _build_provider_metrics(
        self,
        user_id: str,
        start_time: datetime,
    ) -> list[ProviderUsageMetrics]:
        """Build usage metrics for each provider."""
        records = await self.costs.get_records(user_id=user_id, limit=10000)

        # Filter by time
        filtered = [
            r for r in records if datetime.fromisoformat(r.timestamp) >= start_time
        ]

        # Aggregate by provider
        provider_data: dict[str, dict[str, Any]] = {}
        total_cost = 0.0

        for r in filtered:
            total_cost += r.cost_usd

            if r.provider not in provider_data:
                provider_data[r.provider] = {
                    "requests": 0,
                    "cost": 0.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "errors": 0,
                    "latencies": [],
                }

            pd = provider_data[r.provider]
            pd["requests"] += 1
            pd["cost"] += r.cost_usd
            pd["prompt_tokens"] += r.prompt_tokens
            pd["completion_tokens"] += r.completion_tokens

        # Build metrics for all providers (even unused ones)
        metrics = []
        for provider in SUPPORTED_PROVIDERS:
            if provider in provider_data:
                pd = provider_data[provider]
                metrics.append(
                    ProviderUsageMetrics(
                        provider=provider,
                        request_count=pd["requests"],
                        total_cost=pd["cost"],
                        total_prompt_tokens=pd["prompt_tokens"],
                        total_completion_tokens=pd["completion_tokens"],
                        error_count=pd["errors"],
                        average_latency_ms=0.0,  # Would need latency tracking
                        cost_percentage=(pd["cost"] / total_cost * 100)
                        if total_cost > 0
                        else 0,
                    )
                )
            else:
                # Include zero-usage providers for completeness
                metrics.append(
                    ProviderUsageMetrics(
                        provider=provider,
                        request_count=0,
                        total_cost=0.0,
                        total_prompt_tokens=0,
                        total_completion_tokens=0,
                        error_count=0,
                        average_latency_ms=0.0,
                        cost_percentage=0.0,
                    )
                )

        # Sort by cost descending
        metrics.sort(key=lambda x: x.total_cost, reverse=True)

        return metrics

    async def _build_time_series(
        self,
        user_id: str,
        start_time: datetime,
    ) -> list[TimeSeriesPoint]:
        """Build time series data for charts."""
        records = await self.costs.get_records(user_id=user_id, limit=10000)

        # Bucket by hour
        hourly: dict[str, dict[str, float]] = {}

        for r in records:
            record_time = datetime.fromisoformat(r.timestamp)
            if record_time < start_time:
                continue

            # Round to hour
            hour_key = record_time.strftime("%Y-%m-%dT%H:00:00")

            if hour_key not in hourly:
                hourly[hour_key] = {"cost": 0.0, "requests": 0.0}

            hourly[hour_key]["cost"] += r.cost_usd
            hourly[hour_key]["requests"] += 1

        # Build time series
        points = []
        for timestamp in sorted(hourly.keys()):
            data = hourly[timestamp]
            points.append(
                TimeSeriesPoint(
                    timestamp=timestamp,
                    value=data["cost"],
                    metadata={"requests": data["requests"]},
                )
            )

        return points

    async def get_summary_stats(self, user_id: str) -> dict[str, Any]:
        """Get quick summary statistics."""
        now = datetime.utcnow()

        # Get data for different periods
        day_summary = await self.costs.get_user_cost(
            user_id, start_time=now - timedelta(days=1)
        )
        week_summary = await self.costs.get_user_cost(
            user_id, start_time=now - timedelta(days=7)
        )
        month_summary = await self.costs.get_user_cost(
            user_id, start_time=now - timedelta(days=30)
        )

        return {
            "user_id": user_id,
            "last_24h": {
                "cost": day_summary.total_cost,
                "requests": day_summary.request_count,
            },
            "last_7d": {
                "cost": week_summary.total_cost,
                "requests": week_summary.request_count,
            },
            "last_30d": {
                "cost": month_summary.total_cost,
                "requests": month_summary.request_count,
            },
            "timestamp": now.isoformat(),
        }

    def clear_cache(self, user_id: str | None = None) -> None:
        """Clear cached data."""
        if user_id:
            keys_to_remove = [k for k in self._cache if k.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()

        logger.info("Dashboard cache cleared")
