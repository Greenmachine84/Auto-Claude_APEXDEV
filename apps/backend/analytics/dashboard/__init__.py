"""
Dashboard Module - Phase 8 Implementation.

Real-time analytics dashboard with API endpoints and data visualization.

8 Supported Providers (Equal Treatment):
- copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
"""

from .api import DashboardAPI, router
from .data_builder import DashboardDataBuilder
from .chart_data import ChartDataGenerator, ChartType
from .export import DashboardExporter, ExportFormat

__all__ = [
    "DashboardAPI",
    "router",
    "DashboardDataBuilder",
    "ChartDataGenerator",
    "ChartType",
    "DashboardExporter",
    "ExportFormat",
]
