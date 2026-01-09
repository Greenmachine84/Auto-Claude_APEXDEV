"""
Metrics Aggregator - Phase 8 Implementation.

Aggregates raw metrics into summaries for dashboard display.

World-Class Standards:
- Efficient aggregation algorithms
- Provider-aware grouping
- Time-based bucketing
- Agent attribution
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..config import AnalyticsConfig, default_config
from ..models import (
    SUPPORTED_PROVIDERS,
    AgentMetrics,
    DashboardData,
    MetricsSummary,
    ProviderUsageMetrics,
    TimeSeriesPoint,
)

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """
    Aggregates raw metrics into summaries.

    Provides:
    - Per-provider aggregation (all 8 providers)
    - Per-agent aggregation
    - Time-series aggregation
    - Summary statistics

    LLM-Agnostic: All 8 providers aggregated equally.
    """

    def __init__(self, config: AnalyticsConfig | None = None) -> None:
        """Initialize the aggregator."""
        self.config = config or default_config
        logger.info("MetricsAggregator initialized")

    async def aggregate_by_provider(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> dict[str, ProviderUsageMetrics]:
        """
        Aggregate metrics by provider.

        Returns usage metrics for each of the 8 providers
        that has recorded activity.

        Args:
            user_id: User to aggregate for
            period_days: Number of days to aggregate

        Returns:
            Dictionary mapping provider name to usage metrics
        """
        result: dict[str, ProviderUsageMetrics] = {}

        # In production, this would query the storage backend
        # Here we show the structure for all 8 providers
        for provider in SUPPORTED_PROVIDERS:
            metrics = await self._get_provider_metrics(user_id, provider, period_days)
            if metrics.total_requests > 0:
                result[provider] = metrics

        return result

    async def _get_provider_metrics(
        self,
        user_id: str,
        provider: str,
        period_days: int,
    ) -> ProviderUsageMetrics:
        """
        Get metrics for a specific provider.

        Args:
            user_id: User identifier
            provider: Provider name
            period_days: Period in days

        Returns:
            Provider usage metrics
        """
        # In production, query storage
        # Placeholder showing data structure
        return ProviderUsageMetrics(
            provider=provider,
            total_requests=0,
            total_tokens=0,
            prompt_tokens=0,
            completion_tokens=0,
            total_cost=0.0,
            avg_latency_ms=0.0,
            error_count=0,
            error_rate=0.0,
            models_used={},
        )

    async def aggregate_by_agent(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> dict[str, AgentMetrics]:
        """
        Aggregate metrics by agent.

        Args:
            user_id: User to aggregate for
            period_days: Number of days to aggregate

        Returns:
            Dictionary mapping agent_id to metrics
        """
        # In production, query storage
        return {}

    async def aggregate_by_time(
        self,
        user_id: str,
        granularity: str = "hour",
        period_days: int = 7,
    ) -> list[TimeSeriesPoint]:
        """
        Aggregate metrics by time buckets.

        Args:
            user_id: User to aggregate for
            granularity: Time bucket size (hour, day, week)
            period_days: Number of days to aggregate

        Returns:
            List of time series points
        """
        points: list[TimeSeriesPoint] = []

        now = datetime.utcnow()

        if granularity == "hour":
            for i in range(
                min(period_days * 24, self.config.dashboard.time_series_points)
            ):
                timestamp = now - timedelta(hours=i)
                points.append(
                    TimeSeriesPoint(
                        timestamp=timestamp.isoformat() + "Z",
                        value=0.0,
                        label=f"Hour {i}",
                    )
                )
        elif granularity == "day":
            for i in range(min(period_days, self.config.dashboard.time_series_points)):
                timestamp = now - timedelta(days=i)
                points.append(
                    TimeSeriesPoint(
                        timestamp=timestamp.isoformat() + "Z",
                        value=0.0,
                        label=f"Day {i}",
                    )
                )

        return list(reversed(points))

    async def get_summary(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> MetricsSummary:
        """
        Get high-level metrics summary.

        Args:
            user_id: User to summarize for
            period_days: Number of days to summarize

        Returns:
            Metrics summary
        """
        now = datetime.utcnow()
        period_start = now - timedelta(days=period_days)

        by_provider = await self.aggregate_by_provider(user_id, period_days)
        by_agent = await self.aggregate_by_agent(user_id, period_days)

        # Aggregate totals
        total_requests = sum(p.total_requests for p in by_provider.values())
        total_tokens = sum(p.total_tokens for p in by_provider.values())
        total_cost = sum(p.total_cost for p in by_provider.values())

        # Calculate averages
        total_errors = sum(p.error_count for p in by_provider.values())
        error_rate = (
            (total_errors / total_requests * 100) if total_requests > 0 else 0.0
        )

        latencies = [
            p.avg_latency_ms for p in by_provider.values() if p.avg_latency_ms > 0
        ]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        return MetricsSummary(
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost=total_cost,
            active_agents=len(by_agent),
            active_providers=len(by_provider),
            avg_latency_ms=avg_latency,
            error_rate=error_rate,
            period_start=period_start.isoformat() + "Z",
            period_end=now.isoformat() + "Z",
        )

    async def get_overview(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> dict[str, Any]:
        """
        Get dashboard overview data.

        Args:
            user_id: User to get overview for
            period_days: Number of days

        Returns:
            Overview dictionary for dashboard
        """
        summary = await self.get_summary(user_id, period_days)

        return {
            "total_requests": summary.total_requests,
            "total_tokens": summary.total_tokens,
            "total_cost": summary.total_cost,
            "active_agents": summary.active_agents,
            "active_providers": summary.active_providers,
            "avg_latency_ms": summary.avg_latency_ms,
            "error_rate": summary.error_rate,
        }

    async def get_agent_breakdown(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> dict[str, dict[str, Any]]:
        """
        Get per-agent metrics breakdown.

        Args:
            user_id: User to get breakdown for
            period_days: Number of days

        Returns:
            Dictionary mapping agent_id to metrics
        """
        by_agent = await self.aggregate_by_agent(user_id, period_days)

        return {
            agent_id: {
                "agent_type": metrics.agent_type,
                "total_tasks": metrics.total_tasks,
                "completed_tasks": metrics.completed_tasks,
                "failed_tasks": metrics.failed_tasks,
                "success_rate": metrics.success_rate,
                "total_cost": metrics.total_cost,
                "total_tokens": metrics.total_tokens,
                "avg_task_duration_ms": metrics.avg_task_duration_ms,
                "providers_used": metrics.providers_used,
            }
            for agent_id, metrics in by_agent.items()
        }

    async def get_time_series(
        self,
        user_id: str,
        period_days: int = 7,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Get time series data for charts.

        Args:
            user_id: User to get time series for
            period_days: Number of days

        Returns:
            Dictionary with hourly requests and cost data
        """
        hourly_points = await self.aggregate_by_time(user_id, "hour", period_days)
        daily_points = await self.aggregate_by_time(user_id, "day", period_days)

        return {
            "hourly_requests": [
                {"timestamp": p.timestamp, "value": p.value} for p in hourly_points
            ],
            "daily_cost": [
                {"timestamp": p.timestamp, "value": p.value} for p in daily_points
            ],
        }

    async def build_dashboard_data(
        self,
        user_id: str,
        period_days: int = 30,
    ) -> DashboardData:
        """
        Build complete dashboard data structure.

        Args:
            user_id: User to build dashboard for
            period_days: Number of days

        Returns:
            Complete dashboard data
        """
        now = datetime.utcnow()
        period_start = now - timedelta(days=period_days)

        # Gather all data
        by_provider = await self.aggregate_by_provider(user_id, period_days)
        by_agent = await self.get_agent_breakdown(user_id, period_days)
        time_series = await self.get_time_series(user_id, min(period_days, 7))

        # Calculate totals
        total_requests = sum(p.total_requests for p in by_provider.values())
        total_tokens = sum(p.total_tokens for p in by_provider.values())
        total_cost = sum(p.total_cost for p in by_provider.values())

        # Generate recommendations
        recommendations = await self._generate_recommendations(by_provider, total_cost)

        return DashboardData(
            period_start=period_start.isoformat() + "Z",
            period_end=now.isoformat() + "Z",
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost=total_cost,
            by_provider=by_provider,
            by_agent=by_agent,
            hourly_requests=[
                TimeSeriesPoint(timestamp=p["timestamp"], value=p["value"])
                for p in time_series.get("hourly_requests", [])
            ],
            hourly_cost=[
                TimeSeriesPoint(timestamp=p["timestamp"], value=p["value"])
                for p in time_series.get("daily_cost", [])
            ],
            recommendations=recommendations,
        )

    async def _generate_recommendations(
        self,
        by_provider: dict[str, ProviderUsageMetrics],
        total_cost: float,
    ) -> list[str]:
        """
        Generate cost optimization recommendations.

        Args:
            by_provider: Provider usage metrics
            total_cost: Total cost in period

        Returns:
            List of recommendation strings
        """
        recommendations: list[str] = []

        # Check for expensive provider usage
        for provider, metrics in by_provider.items():
            if metrics.total_cost > total_cost * 0.5 and total_cost > 10:
                recommendations.append(
                    f"Consider using local providers (ollama/lmstudio) for some tasks - "
                    f"{provider} accounts for {metrics.total_cost / total_cost * 100:.1f}% of costs"
                )

        # Check for high error rates
        for provider, metrics in by_provider.items():
            if metrics.error_rate > 5.0:
                recommendations.append(
                    f"High error rate ({metrics.error_rate:.1f}%) for {provider} - "
                    f"consider reviewing usage patterns"
                )

        # Local provider reminder
        local_providers = ["ollama", "lmstudio"]
        if not any(p in by_provider for p in local_providers):
            recommendations.append(
                "Consider using local providers (ollama/lmstudio) for development "
                "tasks to reduce costs"
            )

        return recommendations
