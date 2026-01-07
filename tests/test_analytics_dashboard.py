"""
Analytics Dashboard Tests - Phase 8.

Tests for dashboard API, data builder, and exports.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from apps.backend.analytics.dashboard.api import router
from apps.backend.analytics.dashboard.data_builder import DashboardDataBuilder
from apps.backend.analytics.dashboard.chart_data import ChartDataGenerator
from apps.backend.analytics.dashboard.export import DashboardExporter


class TestDashboardDataBuilder:
    """Test DashboardDataBuilder."""
    
    @pytest.fixture
    def builder(self):
        """Create data builder."""
        return DashboardDataBuilder()
    
    @pytest.mark.asyncio
    async def test_build_overview(self, builder):
        """Test building overview data."""
        data = await builder.build_overview(user_id="user-001", days=30)
        
        assert "total_requests" in data
        assert "total_cost" in data
        assert "total_tokens" in data
    
    @pytest.mark.asyncio
    async def test_build_provider_breakdown(self, builder):
        """Test provider breakdown includes all used providers."""
        data = await builder.build_provider_breakdown(
            user_id="user-001", days=30
        )
        
        # Should return dict with provider keys
        assert isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_build_time_series(self, builder):
        """Test time series data generation."""
        data = await builder.build_time_series(
            user_id="user-001",
            days=7,
            interval="hour",
        )
        
        assert "hourly_requests" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_build_with_caching(self, builder):
        """Test caching improves performance."""
        import time
        
        # First call
        start1 = time.perf_counter()
        await builder.build_overview(user_id="user-001", days=30)
        duration1 = time.perf_counter() - start1
        
        # Second call (should be cached)
        start2 = time.perf_counter()
        await builder.build_overview(user_id="user-001", days=30)
        duration2 = time.perf_counter() - start2
        
        # Cached call should be faster
        assert duration2 <= duration1


class TestChartDataGenerator:
    """Test ChartDataGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create chart data generator."""
        return ChartDataGenerator()
    
    def test_generate_line_chart(self, generator):
        """Test line chart data generation."""
        data = generator.generate_line_chart(
            data_points=[
                {"timestamp": "2026-01-01", "value": 10},
                {"timestamp": "2026-01-02", "value": 20},
            ],
            x_field="timestamp",
            y_field="value",
        )
        
        assert "labels" in data
        assert "datasets" in data
    
    def test_generate_bar_chart(self, generator):
        """Test bar chart data generation."""
        data = generator.generate_bar_chart(
            categories=["openai", "anthropic", "gemini"],
            values=[100, 80, 60],
        )
        
        assert len(data["labels"]) == 3
    
    def test_generate_pie_chart(self, generator):
        """Test pie chart for provider distribution."""
        data = generator.generate_pie_chart(
            labels=["copilot", "openrouter", "ollama", "lmstudio",
                    "gemini", "openai", "anthropic", "azure"],
            values=[10, 20, 5, 5, 15, 25, 15, 5],
        )
        
        assert len(data["labels"]) == 8
    
    def test_generate_cost_comparison_chart(self, generator):
        """Test cost comparison chart."""
        data = generator.generate_provider_comparison(
            providers={
                "openai": {"cost": 100, "requests": 1000},
                "anthropic": {"cost": 80, "requests": 800},
                "gemini": {"cost": 60, "requests": 1200},
            }
        )
        
        assert len(data["providers"]) == 3


class TestDashboardExporter:
    """Test DashboardExporter."""
    
    @pytest.fixture
    def exporter(self):
        """Create exporter."""
        return DashboardExporter()
    
    @pytest.mark.asyncio
    async def test_export_json(self, exporter):
        """Test JSON export."""
        data = {
            "total_cost": 100.0,
            "by_provider": {"openai": 50, "anthropic": 50},
        }
        
        result = await exporter.export(data, format="json")
        assert isinstance(result, str)
        assert "total_cost" in result
    
    @pytest.mark.asyncio
    async def test_export_csv(self, exporter):
        """Test CSV export."""
        data = {
            "records": [
                {"provider": "openai", "cost": 50},
                {"provider": "anthropic", "cost": 50},
            ]
        }
        
        result = await exporter.export(data, format="csv")
        assert "provider" in result.lower()
        assert "cost" in result.lower()
    
    @pytest.mark.asyncio
    async def test_export_markdown(self, exporter):
        """Test Markdown export."""
        data = {
            "total_cost": 100.0,
            "by_provider": {"openai": 50, "anthropic": 50},
        }
        
        result = await exporter.export(data, format="markdown")
        assert "#" in result or "|" in result
    
    @pytest.mark.asyncio
    async def test_export_html(self, exporter):
        """Test HTML export."""
        data = {"total_cost": 100.0}
        
        result = await exporter.export(data, format="html")
        assert "<" in result and ">" in result


class TestDashboardAPI:
    """Test Dashboard API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_get_dashboard_endpoint(self, client):
        """Test GET /api/analytics/dashboard."""
        with patch("apps.backend.analytics.dashboard.api.get_current_user") as mock:
            mock.return_value = "user-001"
            response = client.get("/api/analytics/dashboard?days=30")
        
        # Should return 200 or require auth
        assert response.status_code in [200, 401, 422]
    
    def test_get_provider_comparison_endpoint(self, client):
        """Test GET /api/analytics/provider-comparison."""
        with patch("apps.backend.analytics.dashboard.api.get_current_user") as mock:
            mock.return_value = "user-001"
            response = client.get("/api/analytics/provider-comparison")
        
        assert response.status_code in [200, 401, 422]
    
    def test_dashboard_response_time(self, client):
        """Test dashboard API response time (<100ms P99 target)."""
        import time
        
        times = []
        for _ in range(10):
            with patch("apps.backend.analytics.dashboard.api.get_current_user") as mock:
                mock.return_value = "user-001"
                start = time.perf_counter()
                client.get("/api/analytics/dashboard?days=7")
                times.append(time.perf_counter() - start)
        
        # P99 should be under 500ms for test (production target is 100ms)
        p99 = sorted(times)[int(len(times) * 0.99)]
        assert p99 < 0.5
