"""
Chart Data Generator - Phase 8 Implementation.

Generates chart-ready data for visualization.

World-Class Standards:
- Multiple chart types
- Responsive data sizing
- Color schemes per provider
- Export-ready formats
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging

from ..models import (
    DashboardData,
    ProviderUsageMetrics,
    TimeSeriesPoint,
    SUPPORTED_PROVIDERS,
)

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Supported chart types."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    DOUGHNUT = "doughnut"
    STACKED_BAR = "stacked_bar"


# Provider color scheme (consistent across all charts)
PROVIDER_COLORS: Dict[str, str] = {
    "openai": "#10a37f",      # OpenAI green
    "anthropic": "#d4a27f",   # Anthropic tan
    "azure": "#0078d4",       # Azure blue
    "gemini": "#4285f4",      # Google blue
    "openrouter": "#ff6b6b",  # OpenRouter red
    "copilot": "#6e40c9",     # GitHub purple
    "ollama": "#f97316",      # Ollama orange
    "lmstudio": "#22c55e",    # LM Studio green
}


@dataclass
class ChartDataset:
    """Single dataset for a chart."""
    label: str
    data: List[float]
    backgroundColor: str = ""
    borderColor: str = ""
    fill: bool = False
    tension: float = 0.4


@dataclass
class ChartData:
    """Chart-ready data structure."""
    chart_type: ChartType
    title: str
    labels: List[str]
    datasets: List[ChartDataset]
    options: Dict[str, Any] = field(default_factory=dict)


class ChartDataGenerator:
    """
    Generates chart-ready visualization data.
    
    Features:
    - Multiple chart types
    - Provider-consistent colors
    - Responsive sizing
    - Animation support
    """
    
    def __init__(self) -> None:
        """Initialize chart generator."""
        logger.info("ChartDataGenerator initialized")
    
    def cost_by_provider_pie(
        self,
        provider_metrics: List[ProviderUsageMetrics],
    ) -> ChartData:
        """Generate pie chart for cost distribution by provider."""
        # Filter out zero-cost providers
        active = [pm for pm in provider_metrics if pm.total_cost > 0]
        
        labels = [pm.provider for pm in active]
        data = [pm.total_cost for pm in active]
        colors = [PROVIDER_COLORS.get(pm.provider, "#888888") for pm in active]
        
        return ChartData(
            chart_type=ChartType.PIE,
            title="Cost Distribution by Provider",
            labels=labels,
            datasets=[
                ChartDataset(
                    label="Cost (USD)",
                    data=data,
                    backgroundColor=",".join(colors),
                )
            ],
            options={
                "responsive": True,
                "plugins": {
                    "legend": {"position": "right"},
                    "tooltip": {"callbacks": {"label": "formatCurrency"}},
                },
            },
        )
    
    def requests_by_provider_bar(
        self,
        provider_metrics: List[ProviderUsageMetrics],
    ) -> ChartData:
        """Generate bar chart for request counts by provider."""
        labels = [pm.provider for pm in provider_metrics if pm.request_count > 0]
        data = [pm.request_count for pm in provider_metrics if pm.request_count > 0]
        colors = [
            PROVIDER_COLORS.get(pm.provider, "#888888")
            for pm in provider_metrics if pm.request_count > 0
        ]
        
        return ChartData(
            chart_type=ChartType.BAR,
            title="Requests by Provider",
            labels=labels,
            datasets=[
                ChartDataset(
                    label="Requests",
                    data=data,
                    backgroundColor=",".join(colors),
                )
            ],
            options={
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True, "title": {"display": True, "text": "Requests"}},
                },
            },
        )
    
    def cost_over_time_line(
        self,
        time_series: List[TimeSeriesPoint],
        title: str = "Cost Over Time",
    ) -> ChartData:
        """Generate line chart for cost over time."""
        labels = []
        data = []
        
        for point in time_series:
            # Format timestamp for display
            dt = datetime.fromisoformat(point.timestamp)
            labels.append(dt.strftime("%m/%d %H:%M"))
            data.append(point.value)
        
        return ChartData(
            chart_type=ChartType.LINE,
            title=title,
            labels=labels,
            datasets=[
                ChartDataset(
                    label="Cost (USD)",
                    data=data,
                    borderColor="#10a37f",
                    backgroundColor="rgba(16, 163, 127, 0.1)",
                    fill=True,
                    tension=0.4,
                )
            ],
            options={
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True, "title": {"display": True, "text": "USD"}},
                    "x": {"title": {"display": True, "text": "Time"}},
                },
                "plugins": {
                    "tooltip": {"mode": "index", "intersect": False},
                },
            },
        )
    
    def tokens_by_provider_stacked(
        self,
        provider_metrics: List[ProviderUsageMetrics],
    ) -> ChartData:
        """Generate stacked bar chart for token usage."""
        active = [pm for pm in provider_metrics if pm.total_prompt_tokens > 0]
        
        labels = [pm.provider for pm in active]
        prompt_data = [pm.total_prompt_tokens for pm in active]
        completion_data = [pm.total_completion_tokens for pm in active]
        
        return ChartData(
            chart_type=ChartType.STACKED_BAR,
            title="Token Usage by Provider",
            labels=labels,
            datasets=[
                ChartDataset(
                    label="Prompt Tokens",
                    data=prompt_data,
                    backgroundColor="#3b82f6",  # Blue
                ),
                ChartDataset(
                    label="Completion Tokens",
                    data=completion_data,
                    backgroundColor="#10b981",  # Green
                ),
            ],
            options={
                "responsive": True,
                "scales": {
                    "x": {"stacked": True},
                    "y": {"stacked": True, "title": {"display": True, "text": "Tokens"}},
                },
            },
        )
    
    def provider_comparison_radar(
        self,
        provider_metrics: List[ProviderUsageMetrics],
    ) -> ChartData:
        """Generate radar chart for provider comparison."""
        active = [pm for pm in provider_metrics if pm.request_count > 0]
        
        if not active:
            return ChartData(
                chart_type=ChartType.BAR,
                title="Provider Comparison",
                labels=[],
                datasets=[],
            )
        
        # Normalize metrics for comparison
        max_requests = max(pm.request_count for pm in active) or 1
        max_tokens = max(pm.total_prompt_tokens + pm.total_completion_tokens for pm in active) or 1
        max_cost = max(pm.total_cost for pm in active) or 1
        
        datasets = []
        for pm in active:
            total_tokens = pm.total_prompt_tokens + pm.total_completion_tokens
            datasets.append(
                ChartDataset(
                    label=pm.provider,
                    data=[
                        pm.request_count / max_requests * 100,
                        total_tokens / max_tokens * 100,
                        pm.total_cost / max_cost * 100,
                    ],
                    borderColor=PROVIDER_COLORS.get(pm.provider, "#888888"),
                    backgroundColor=f"{PROVIDER_COLORS.get(pm.provider, '#888888')}40",
                    fill=True,
                )
            )
        
        return ChartData(
            chart_type=ChartType.BAR,  # Radar would be a special type
            title="Provider Comparison",
            labels=["Requests", "Tokens", "Cost"],
            datasets=datasets,
            options={
                "responsive": True,
                "scales": {"r": {"beginAtZero": True, "max": 100}},
            },
        )
    
    def budget_gauge(
        self,
        used: float,
        total: float,
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.95,
    ) -> Dict[str, Any]:
        """Generate gauge chart data for budget status."""
        percentage = (used / total * 100) if total > 0 else 0
        
        if percentage >= critical_threshold * 100:
            color = "#ef4444"  # Red
            status = "critical"
        elif percentage >= warning_threshold * 100:
            color = "#f59e0b"  # Amber
            status = "warning"
        else:
            color = "#10b981"  # Green
            status = "ok"
        
        return {
            "type": "gauge",
            "title": "Budget Status",
            "value": percentage,
            "max": 100,
            "color": color,
            "status": status,
            "used": used,
            "total": total,
            "remaining": max(0, total - used),
            "thresholds": {
                "warning": warning_threshold * 100,
                "critical": critical_threshold * 100,
            },
        }
    
    def generate_all_charts(
        self,
        dashboard_data: DashboardData,
    ) -> Dict[str, Any]:
        """Generate all charts from dashboard data."""
        return {
            "cost_by_provider": self.cost_by_provider_pie(
                dashboard_data.provider_metrics
            ),
            "requests_by_provider": self.requests_by_provider_bar(
                dashboard_data.provider_metrics
            ),
            "cost_over_time": self.cost_over_time_line(
                dashboard_data.cost_time_series
            ),
            "tokens_by_provider": self.tokens_by_provider_stacked(
                dashboard_data.provider_metrics
            ),
            "provider_comparison": self.provider_comparison_radar(
                dashboard_data.provider_metrics
            ),
            "budget_gauge": self.budget_gauge(
                dashboard_data.budget_status.used,
                dashboard_data.budget_status.total_budget,
            ),
        }
    
    def to_json(self, chart_data: ChartData) -> Dict[str, Any]:
        """Convert chart data to JSON-serializable format."""
        return {
            "type": chart_data.chart_type.value,
            "title": chart_data.title,
            "labels": chart_data.labels,
            "datasets": [
                {
                    "label": ds.label,
                    "data": ds.data,
                    "backgroundColor": ds.backgroundColor,
                    "borderColor": ds.borderColor,
                    "fill": ds.fill,
                    "tension": ds.tension,
                }
                for ds in chart_data.datasets
            ],
            "options": chart_data.options,
        }
