"""
Analytics Metrics Tests - Phase 8.

Tests for metrics collection, aggregation, time series, and storage.
Focus on module importability and basic class instantiation.
"""

import pytest
from datetime import datetime


class TestAnalyticsModelsImport:
    """Test analytics models are importable."""

    def test_import_models(self):
        """Test importing core analytics models."""
        from apps.backend.analytics.models import MetricEvent
        from apps.backend.analytics.models import SUPPORTED_PROVIDERS
        assert MetricEvent is not None
        assert SUPPORTED_PROVIDERS is not None

    def test_metric_event_creation(self):
        """Test creating a MetricEvent."""
        from apps.backend.analytics.models import MetricEvent
        
        event = MetricEvent(
            id="test-event-1",
            event_type="llm_request",
            timestamp=datetime.now(),
            provider="openai",
            model="gpt-4",
            value=100.0,
            metadata={"tokens": 100},
        )
        assert event.id == "test-event-1"
        assert event.provider == "openai"

    def test_all_providers_equal(self):
        """Test that all 8 providers are supported equally."""
        from apps.backend.analytics.models import SUPPORTED_PROVIDERS
        
        expected_providers = {
            "copilot", "openrouter", "ollama", "lmstudio",
            "gemini", "openai", "anthropic", "azure"
        }
        actual_providers = set(SUPPORTED_PROVIDERS)
        assert expected_providers == actual_providers


class TestMetricsCollectorImport:
    """Test MetricsCollector is importable."""

    def test_import_collector(self):
        """Test importing MetricsCollector."""
        from apps.backend.analytics.metrics.collector import MetricsCollector
        assert MetricsCollector is not None

    def test_instantiate_collector(self):
        """Test creating MetricsCollector instance."""
        from apps.backend.analytics.metrics.collector import MetricsCollector
        collector = MetricsCollector()
        assert collector is not None

    def test_collector_has_record_method(self):
        """Test collector has record methods."""
        from apps.backend.analytics.metrics.collector import MetricsCollector
        collector = MetricsCollector()
        # Check for actual methods
        assert hasattr(collector, 'record_event') or hasattr(collector, 'record_llm_request')


class TestMetricsAggregatorImport:
    """Test MetricsAggregator is importable."""

    def test_import_aggregator(self):
        """Test importing MetricsAggregator."""
        from apps.backend.analytics.metrics.aggregator import MetricsAggregator
        assert MetricsAggregator is not None

    def test_instantiate_aggregator(self):
        """Test creating MetricsAggregator instance."""
        from apps.backend.analytics.metrics.aggregator import MetricsAggregator
        aggregator = MetricsAggregator()
        assert aggregator is not None


class TestTimeSeriesImport:
    """Test TimeSeries is importable."""

    def test_import_time_series(self):
        """Test importing TimeSeriesManager."""
        from apps.backend.analytics.metrics.time_series import TimeSeriesManager
        assert TimeSeriesManager is not None

    def test_instantiate_time_series(self):
        """Test creating TimeSeriesManager instance."""
        from apps.backend.analytics.metrics.time_series import TimeSeriesManager
        ts = TimeSeriesManager()
        assert ts is not None


class TestMetricsStorageImport:
    """Test MetricsStorage is importable."""

    def test_import_storage(self):
        """Test importing MetricsStorage."""
        from apps.backend.analytics.metrics.storage import MetricsStorage
        assert MetricsStorage is not None

    def test_instantiate_storage(self):
        """Test creating MetricsStorage instance."""
        from apps.backend.analytics.metrics.storage import MetricsStorage
        storage = MetricsStorage()
        assert storage is not None
