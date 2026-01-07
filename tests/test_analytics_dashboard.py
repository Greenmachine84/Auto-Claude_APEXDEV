"""
Analytics Dashboard Tests - Phase 8.

Tests for dashboard data building, chart generation, export, and API.
Focus on module importability and basic class instantiation.
"""

import pytest


class TestDashboardDataBuilderImport:
    """Test DashboardDataBuilder is importable."""

    def test_import_data_builder(self):
        """Test importing DashboardDataBuilder."""
        from apps.backend.analytics.dashboard.data_builder import DashboardDataBuilder
        assert DashboardDataBuilder is not None

    def test_data_builder_requires_dependencies(self):
        """Test DashboardDataBuilder requires proper dependencies."""
        from apps.backend.analytics.dashboard.data_builder import DashboardDataBuilder
        from apps.backend.analytics.metrics.collector import MetricsCollector
        from apps.backend.analytics.metrics.aggregator import MetricsAggregator
        from apps.backend.analytics.cost.cost_tracker import CostTracker
        from apps.backend.analytics.cost.budget_manager import BudgetManager
        
        # Instantiate dependencies - BudgetManager needs CostTracker
        collector = MetricsCollector()
        aggregator = MetricsAggregator()
        tracker = CostTracker()
        budget = BudgetManager(cost_tracker=tracker)
        
        # Create builder with dependencies
        builder = DashboardDataBuilder(
            metrics_collector=collector,
            metrics_aggregator=aggregator,
            cost_tracker=tracker,
            budget_manager=budget,
        )
        assert builder is not None


class TestChartDataGeneratorImport:
    """Test ChartDataGenerator is importable."""

    def test_import_chart_generator(self):
        """Test importing ChartDataGenerator."""
        from apps.backend.analytics.dashboard.chart_data import ChartDataGenerator
        assert ChartDataGenerator is not None

    def test_instantiate_chart_generator(self):
        """Test creating ChartDataGenerator instance."""
        from apps.backend.analytics.dashboard.chart_data import ChartDataGenerator
        generator = ChartDataGenerator()
        assert generator is not None

    def test_generator_has_chart_methods(self):
        """Test generator has chart generation methods."""
        from apps.backend.analytics.dashboard.chart_data import ChartDataGenerator
        generator = ChartDataGenerator()
        # Should have some chart method
        methods = [m for m in dir(generator) if 'chart' in m.lower() or 'generate' in m.lower()]
        assert len(methods) > 0


class TestDashboardExporterImport:
    """Test DashboardExporter is importable."""

    def test_import_exporter(self):
        """Test importing DashboardExporter."""
        from apps.backend.analytics.dashboard.export import DashboardExporter
        assert DashboardExporter is not None

    def test_import_export_format(self):
        """Test importing ExportFormat."""
        from apps.backend.analytics.dashboard.export import ExportFormat
        assert ExportFormat is not None

    def test_instantiate_exporter(self):
        """Test creating DashboardExporter instance."""
        from apps.backend.analytics.dashboard.export import DashboardExporter
        exporter = DashboardExporter()
        assert exporter is not None


class TestDashboardAPIImport:
    """Test DashboardAPI is importable."""

    def test_import_api(self):
        """Test importing DashboardAPI."""
        from apps.backend.analytics.dashboard.api import DashboardAPI
        assert DashboardAPI is not None

    def test_instantiate_api(self):
        """Test creating DashboardAPI instance."""
        from apps.backend.analytics.dashboard.api import DashboardAPI
        api = DashboardAPI()
        assert api is not None

    def test_api_has_dashboard_method(self):
        """Test API has dashboard-related methods."""
        from apps.backend.analytics.dashboard.api import DashboardAPI
        api = DashboardAPI()
        # Should have some dashboard method
        methods = [m for m in dir(api) if not m.startswith('_')]
        assert len(methods) > 0


class TestDashboardModelsImport:
    """Test dashboard models are importable."""

    def test_import_dashboard_request(self):
        """Test importing DashboardRequest."""
        from apps.backend.analytics.dashboard.api import DashboardRequest
        assert DashboardRequest is not None

    def test_import_dashboard_response(self):
        """Test importing DashboardResponse."""
        from apps.backend.analytics.dashboard.api import DashboardResponse
        assert DashboardResponse is not None
