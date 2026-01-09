"""
Analytics Module - Phase 8 Implementation.

Provides comprehensive analytics for usage tracking, cost calculation,
and dashboard visualization. LLM-Agnostic design with per-provider
tracking for all 8 supported providers.

World-Class Standards:
- Real-time visibility (<5s event-to-dashboard)
- Financial-grade accuracy (<0.1% cost error)
- Enterprise-scale performance (>10K events/s)

Supported Providers (8 total, equal treatment):
- copilot, openrouter, ollama, lmstudio
- gemini, openai, anthropic, azure
"""

from .config import AnalyticsConfig
from .models import (
    BudgetStatus,
    CostRecord,
    DashboardData,
    EventType,
    MetricEvent,
    MetricType,
    ProviderUsageMetrics,
    TimeSeriesPoint,
)

__all__ = [
    # Models
    "MetricType",
    "EventType",
    "MetricEvent",
    "CostRecord",
    "ProviderUsageMetrics",
    "DashboardData",
    "BudgetStatus",
    "TimeSeriesPoint",
    # Config
    "AnalyticsConfig",
]

__version__ = "1.0.0"
__phase__ = "8"
