"""
Analytics Metrics Tests - Phase 8.

Tests for metrics collector, aggregator, time series, and storage.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from apps.backend.analytics.models import (
    MetricEvent, MetricType, EventType, ProviderUsageMetrics
)
from apps.backend.analytics.metrics.collector import MetricsCollector
from apps.backend.analytics.metrics.aggregator import MetricsAggregator
from apps.backend.analytics.metrics.time_series import TimeSeriesManager
from apps.backend.analytics.metrics.storage import MetricsStorage


class TestMetricEvent:
    """Test MetricEvent model."""
    
    def test_create_event(self):
        """Test creating a metric event."""
        event = MetricEvent(
            id="test-001",
            event_type=EventType.LLM_REQUEST,
            timestamp=datetime.utcnow().isoformat(),
            provider="openai",
            model="gpt-4o",
            value=1.0,
        )
        assert event.id == "test-001"
        assert event.event_type == EventType.LLM_REQUEST
        assert event.provider == "openai"
    
    def test_event_with_all_providers(self):
        """Test events for all 8 providers."""
        providers = ["copilot", "openrouter", "ollama", "lmstudio", 
                     "gemini", "openai", "anthropic", "azure"]
        
        for provider in providers:
            event = MetricEvent(
                id=f"test-{provider}",
                event_type=EventType.LLM_REQUEST,
                timestamp=datetime.utcnow().isoformat(),
                provider=provider,
            )
            assert event.provider == provider


class TestMetricsCollector:
    """Test MetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance."""
        return MetricsCollector()
    
    @pytest.mark.asyncio
    async def test_collect_event(self, collector):
        """Test collecting a single event."""
        event = MetricEvent(
            id="test-001",
            event_type=EventType.LLM_REQUEST,
            timestamp=datetime.utcnow().isoformat(),
            provider="openai",
        )
        
        await collector.collect(event)
        stats = collector.get_statistics()
        assert stats["total_collected"] >= 1
    
    @pytest.mark.asyncio
    async def test_collect_batch(self, collector):
        """Test collecting batch of events."""
        events = [
            MetricEvent(
                id=f"test-{i}",
                event_type=EventType.LLM_REQUEST,
                timestamp=datetime.utcnow().isoformat(),
                provider="openai",
            )
            for i in range(100)
        ]
        
        await collector.collect_batch(events)
        stats = collector.get_statistics()
        assert stats["total_collected"] >= 100
    
    @pytest.mark.asyncio
    async def test_high_throughput(self, collector):
        """Test high-throughput collection (>10K events/s target)."""
        events = [
            MetricEvent(
                id=f"perf-{i}",
                event_type=EventType.LLM_REQUEST,
                timestamp=datetime.utcnow().isoformat(),
                provider="anthropic",
            )
            for i in range(1000)
        ]
        
        start = datetime.utcnow()
        await collector.collect_batch(events)
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Should process 1000 events in under 100ms
        assert duration < 0.1


class TestMetricsAggregator:
    """Test MetricsAggregator."""
    
    @pytest.fixture
    def aggregator(self):
        """Create aggregator instance."""
        return MetricsAggregator()
    
    def test_aggregate_by_provider(self, aggregator):
        """Test aggregation by provider."""
        events = [
            MetricEvent(
                id=f"agg-{i}",
                event_type=EventType.LLM_REQUEST,
                timestamp=datetime.utcnow().isoformat(),
                provider="openai" if i % 2 == 0 else "anthropic",
                value=1.0,
            )
            for i in range(10)
        ]
        
        result = aggregator.aggregate(events, group_by="provider")
        assert "openai" in result or "anthropic" in result
    
    def test_aggregate_by_time(self, aggregator):
        """Test time-based aggregation."""
        now = datetime.utcnow()
        events = [
            MetricEvent(
                id=f"time-{i}",
                event_type=EventType.LLM_REQUEST,
                timestamp=(now - timedelta(hours=i)).isoformat(),
                provider="gemini",
                value=1.0,
            )
            for i in range(24)
        ]
        
        result = aggregator.aggregate_time_series(events, interval="hour")
        assert len(result) > 0


class TestTimeSeriesManager:
    """Test TimeSeriesManager."""
    
    @pytest.fixture
    def ts_manager(self):
        """Create time series manager."""
        return TimeSeriesManager()
    
    @pytest.mark.asyncio
    async def test_add_point(self, ts_manager):
        """Test adding data point."""
        await ts_manager.add_point(
            metric_name="requests",
            value=1.0,
            timestamp=datetime.utcnow(),
            tags={"provider": "openai"},
        )
        
        data = await ts_manager.get_series("requests")
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_query_range(self, ts_manager):
        """Test querying time range."""
        now = datetime.utcnow()
        
        for i in range(10):
            await ts_manager.add_point(
                metric_name="test_metric",
                value=float(i),
                timestamp=now - timedelta(minutes=i),
            )
        
        data = await ts_manager.query(
            metric_name="test_metric",
            start=now - timedelta(hours=1),
            end=now,
        )
        assert len(data) == 10


class TestMetricsStorage:
    """Test MetricsStorage."""
    
    @pytest.fixture
    def storage(self, tmp_path):
        """Create storage with temp database."""
        db_path = str(tmp_path / "test_metrics.db")
        return MetricsStorage(db_path=db_path)
    
    @pytest.mark.asyncio
    async def test_store_event(self, storage):
        """Test storing event."""
        event = MetricEvent(
            id="store-001",
            event_type=EventType.LLM_REQUEST,
            timestamp=datetime.utcnow().isoformat(),
            provider="azure",
        )
        
        await storage.store(event)
        retrieved = await storage.get("store-001")
        assert retrieved is not None
        assert retrieved.provider == "azure"
    
    @pytest.mark.asyncio
    async def test_store_batch(self, storage):
        """Test batch storage."""
        events = [
            MetricEvent(
                id=f"batch-{i}",
                event_type=EventType.LLM_REQUEST,
                timestamp=datetime.utcnow().isoformat(),
                provider="lmstudio",
            )
            for i in range(100)
        ]
        
        await storage.store_batch(events)
        count = await storage.count()
        assert count >= 100
    
    @pytest.mark.asyncio
    async def test_query_by_provider(self, storage):
        """Test querying by provider."""
        providers = ["copilot", "ollama"]
        
        for provider in providers:
            event = MetricEvent(
                id=f"query-{provider}",
                event_type=EventType.LLM_REQUEST,
                timestamp=datetime.utcnow().isoformat(),
                provider=provider,
            )
            await storage.store(event)
        
        results = await storage.query(provider="ollama")
        assert all(r.provider == "ollama" for r in results)
