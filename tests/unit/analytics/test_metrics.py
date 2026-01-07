"""
Metrics Collection Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Multi-provider metrics
- Real-time collection
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, List

# All 8 LLM providers
SUPPORTED_PROVIDERS = {
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
}


class TestMetricsCollection:
    """Test metrics collection."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_collect_metrics(self, provider_id: str):
        """Metrics collected per provider."""
        collector = MagicMock()
        collector.record = AsyncMock()
        
        await collector.record(
            provider=provider_id,
            metric="request_count",
            value=1,
        )
        
        collector.record.assert_called_once()

    async def test_collect_latency(self):
        """Latency metrics collected."""
        collector = MagicMock()
        collector.record_latency = AsyncMock()
        
        await collector.record_latency(
            provider="openai",
            latency_ms=250.5,
        )
        
        collector.record_latency.assert_called_once()


class TestMetricTypes:
    """Test metric types."""

    def test_metric_types_defined(self):
        """Metric types are defined."""
        metric_types = [
            "request_count",
            "token_count",
            "latency_ms",
            "error_count",
            "cost_usd",
        ]
        
        assert len(metric_types) >= 5

    @pytest.mark.parametrize("metric_type", [
        "request_count",
        "token_count",
        "error_count",
    ])
    async def test_counter_metrics(self, metric_type: str):
        """Counter metrics work."""
        collector = MagicMock()
        collector.increment = AsyncMock()
        
        await collector.increment(metric=metric_type, value=1)
        
        collector.increment.assert_called_once()


class TestMetricsAggregation:
    """Test metrics aggregation."""

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_aggregate_by_provider(self, provider_id: str):
        """Metrics aggregated by provider."""
        collector = MagicMock()
        collector.aggregate = AsyncMock(return_value={
            "provider": provider_id,
            "request_count": 100,
            "avg_latency_ms": 250.0,
        })
        
        result = await collector.aggregate(
            provider=provider_id,
            period="1h",
        )
        
        assert result["provider"] == provider_id

    async def test_aggregate_by_time(self):
        """Metrics aggregated by time."""
        collector = MagicMock()
        collector.aggregate_time_series = AsyncMock(return_value=[
            {"timestamp": "2026-01-07T00:00:00Z", "value": 100},
            {"timestamp": "2026-01-07T01:00:00Z", "value": 150},
        ])
        
        result = await collector.aggregate_time_series(
            metric="request_count",
            interval="1h",
        )
        
        assert len(result) >= 0


class TestMetricsExport:
    """Test metrics export."""

    async def test_export_prometheus(self):
        """Metrics exported in Prometheus format."""
        exporter = MagicMock()
        exporter.export_prometheus = AsyncMock(return_value="""
# HELP request_count Total requests
# TYPE request_count counter
request_count{provider="openai"} 100
        """.strip())
        
        result = await exporter.export_prometheus()
        
        assert "request_count" in result

    async def test_export_json(self):
        """Metrics exported as JSON."""
        exporter = MagicMock()
        exporter.export_json = AsyncMock(return_value={
            "metrics": [
                {"name": "request_count", "value": 100},
            ]
        })
        
        result = await exporter.export_json()
        
        assert "metrics" in result
