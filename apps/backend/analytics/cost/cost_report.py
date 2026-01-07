"""
Cost Report Generator - Phase 8 Implementation.

Comprehensive cost reporting and export.

World-Class Standards:
- Multi-format export (JSON, CSV, PDF)
- Customizable date ranges
- Provider comparison reports
- Trend analysis
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import csv
import io

from ..models import CostRecord, SUPPORTED_PROVIDERS
from .cost_tracker import CostTracker, CostSummary

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"


class ReportPeriod(Enum):
    """Predefined report periods."""
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"


@dataclass
class ProviderStats:
    """Statistics for a single provider."""
    provider: str
    total_cost: float
    request_count: int
    total_tokens: int
    average_cost_per_request: float
    percentage_of_total: float
    top_models: List[Dict[str, Any]]


@dataclass
class CostTrend:
    """Cost trend data point."""
    date: str
    cost: float
    request_count: int
    cumulative_cost: float


@dataclass
class CostReport:
    """Comprehensive cost report."""
    user_id: str
    period_start: str
    period_end: str
    total_cost: float
    total_requests: int
    total_tokens: int
    average_daily_cost: float
    by_provider: List[ProviderStats]
    daily_trends: List[CostTrend]
    recommendations: List[str]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class CostReportGenerator:
    """
    Cost report generation.
    
    Features:
    - Multiple output formats
    - Predefined and custom periods
    - Provider comparison
    - Trend analysis
    """
    
    def __init__(self, cost_tracker: CostTracker) -> None:
        """Initialize report generator."""
        self.cost_tracker = cost_tracker
        logger.info("CostReportGenerator initialized")
    
    def _get_period_range(
        self,
        period: ReportPeriod,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None,
    ) -> tuple[datetime, datetime]:
        """Get start and end times for a period."""
        now = datetime.utcnow()
        
        if period == ReportPeriod.LAST_24H:
            return now - timedelta(hours=24), now
        elif period == ReportPeriod.LAST_7D:
            return now - timedelta(days=7), now
        elif period == ReportPeriod.LAST_30D:
            return now - timedelta(days=30), now
        elif period == ReportPeriod.THIS_MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, now
        elif period == ReportPeriod.LAST_MONTH:
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_end = first_of_this_month - timedelta(seconds=1)
            last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return last_month_start, last_month_end
        elif period == ReportPeriod.CUSTOM:
            if not custom_start or not custom_end:
                raise ValueError("Custom period requires start and end times")
            return custom_start, custom_end
        else:
            return now - timedelta(days=30), now
    
    async def generate_report(
        self,
        user_id: str,
        period: ReportPeriod = ReportPeriod.LAST_30D,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None,
    ) -> CostReport:
        """Generate a comprehensive cost report."""
        start_time, end_time = self._get_period_range(period, custom_start, custom_end)
        
        # Get cost summary
        summary = await self.cost_tracker.get_user_cost(
            user_id, start_time=start_time, end_time=end_time
        )
        
        # Get records for detailed analysis
        records = await self.cost_tracker.get_records(user_id=user_id, limit=10000)
        filtered_records = [
            r for r in records
            if start_time <= datetime.fromisoformat(r.timestamp) <= end_time
        ]
        
        # Calculate provider stats
        provider_stats = self._calculate_provider_stats(
            filtered_records, summary.total_cost
        )
        
        # Calculate daily trends
        daily_trends = self._calculate_daily_trends(filtered_records)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            provider_stats, summary, daily_trends
        )
        
        # Calculate days in period
        days = max(1, (end_time - start_time).days)
        
        return CostReport(
            user_id=user_id,
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            total_cost=summary.total_cost,
            total_requests=summary.request_count,
            total_tokens=summary.total_prompt_tokens + summary.total_completion_tokens,
            average_daily_cost=summary.total_cost / days,
            by_provider=provider_stats,
            daily_trends=daily_trends,
            recommendations=recommendations,
        )
    
    def _calculate_provider_stats(
        self,
        records: List[CostRecord],
        total_cost: float,
    ) -> List[ProviderStats]:
        """Calculate statistics per provider."""
        provider_data: Dict[str, Dict[str, Any]] = {}
        
        for r in records:
            if r.provider not in provider_data:
                provider_data[r.provider] = {
                    "cost": 0.0,
                    "count": 0,
                    "tokens": 0,
                    "models": {},
                }
            
            pd = provider_data[r.provider]
            pd["cost"] += r.cost_usd
            pd["count"] += 1
            pd["tokens"] += r.prompt_tokens + r.completion_tokens
            
            # Track models
            model_key = r.model
            if model_key not in pd["models"]:
                pd["models"][model_key] = {"cost": 0.0, "count": 0}
            pd["models"][model_key]["cost"] += r.cost_usd
            pd["models"][model_key]["count"] += 1
        
        stats = []
        for provider in SUPPORTED_PROVIDERS:
            if provider in provider_data:
                pd = provider_data[provider]
                
                # Sort models by cost
                top_models = sorted(
                    [
                        {"model": k, "cost": v["cost"], "count": v["count"]}
                        for k, v in pd["models"].items()
                    ],
                    key=lambda x: x["cost"],
                    reverse=True,
                )[:5]
                
                stats.append(ProviderStats(
                    provider=provider,
                    total_cost=pd["cost"],
                    request_count=pd["count"],
                    total_tokens=pd["tokens"],
                    average_cost_per_request=pd["cost"] / pd["count"] if pd["count"] > 0 else 0,
                    percentage_of_total=(pd["cost"] / total_cost * 100) if total_cost > 0 else 0,
                    top_models=top_models,
                ))
        
        # Sort by cost descending
        stats.sort(key=lambda x: x.total_cost, reverse=True)
        
        return stats
    
    def _calculate_daily_trends(
        self,
        records: List[CostRecord],
    ) -> List[CostTrend]:
        """Calculate daily cost trends."""
        daily: Dict[str, Dict[str, Any]] = {}
        
        for r in records:
            date = r.timestamp[:10]  # YYYY-MM-DD
            if date not in daily:
                daily[date] = {"cost": 0.0, "count": 0}
            daily[date]["cost"] += r.cost_usd
            daily[date]["count"] += 1
        
        # Sort by date
        sorted_dates = sorted(daily.keys())
        
        trends = []
        cumulative = 0.0
        for date in sorted_dates:
            data = daily[date]
            cumulative += data["cost"]
            trends.append(CostTrend(
                date=date,
                cost=data["cost"],
                request_count=data["count"],
                cumulative_cost=cumulative,
            ))
        
        return trends
    
    def _generate_recommendations(
        self,
        provider_stats: List[ProviderStats],
        summary: CostSummary,
        trends: List[CostTrend],
    ) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        if not provider_stats:
            return ["No usage data to analyze"]
        
        # High cost provider warning
        for ps in provider_stats:
            if ps.percentage_of_total > 70:
                recommendations.append(
                    f"Consider diversifying: {ps.provider} accounts for "
                    f"{ps.percentage_of_total:.1f}% of costs"
                )
        
        # Check for local provider usage
        local_providers = ["ollama", "lmstudio"]
        local_usage = sum(
            ps.percentage_of_total for ps in provider_stats
            if ps.provider in local_providers
        )
        if local_usage < 10 and summary.total_cost > 10:
            recommendations.append(
                "Consider using local models (ollama, lmstudio) for "
                "development/testing to reduce costs"
            )
        
        # Trend analysis
        if len(trends) >= 7:
            recent_avg = sum(t.cost for t in trends[-7:]) / 7
            earlier_avg = sum(t.cost for t in trends[:7]) / 7 if len(trends) >= 14 else recent_avg
            
            if recent_avg > earlier_avg * 1.5:
                recommendations.append(
                    f"Cost trend increasing: recent avg ${recent_avg:.2f}/day "
                    f"vs earlier ${earlier_avg:.2f}/day"
                )
        
        if not recommendations:
            recommendations.append("Usage patterns look optimal")
        
        return recommendations
    
    def export_json(self, report: CostReport) -> str:
        """Export report as JSON."""
        return json.dumps({
            "user_id": report.user_id,
            "period_start": report.period_start,
            "period_end": report.period_end,
            "total_cost": report.total_cost,
            "total_requests": report.total_requests,
            "total_tokens": report.total_tokens,
            "average_daily_cost": report.average_daily_cost,
            "by_provider": [
                {
                    "provider": ps.provider,
                    "total_cost": ps.total_cost,
                    "request_count": ps.request_count,
                    "total_tokens": ps.total_tokens,
                    "average_cost_per_request": ps.average_cost_per_request,
                    "percentage_of_total": ps.percentage_of_total,
                    "top_models": ps.top_models,
                }
                for ps in report.by_provider
            ],
            "daily_trends": [
                {
                    "date": t.date,
                    "cost": t.cost,
                    "request_count": t.request_count,
                    "cumulative_cost": t.cumulative_cost,
                }
                for t in report.daily_trends
            ],
            "recommendations": report.recommendations,
            "generated_at": report.generated_at,
        }, indent=2)
    
    def export_csv(self, report: CostReport) -> str:
        """Export report as CSV."""
        output = io.StringIO()
        
        # Summary section
        output.write("Cost Report Summary\n")
        output.write(f"User ID,{report.user_id}\n")
        output.write(f"Period,{report.period_start} to {report.period_end}\n")
        output.write(f"Total Cost,${report.total_cost:.2f}\n")
        output.write(f"Total Requests,{report.total_requests}\n")
        output.write(f"Average Daily Cost,${report.average_daily_cost:.2f}\n")
        output.write("\n")
        
        # Provider breakdown
        output.write("Provider Breakdown\n")
        output.write("Provider,Cost,Requests,Tokens,% of Total\n")
        for ps in report.by_provider:
            output.write(
                f"{ps.provider},${ps.total_cost:.2f},{ps.request_count},"
                f"{ps.total_tokens},{ps.percentage_of_total:.1f}%\n"
            )
        output.write("\n")
        
        # Daily trends
        output.write("Daily Trends\n")
        output.write("Date,Cost,Requests,Cumulative\n")
        for t in report.daily_trends:
            output.write(
                f"{t.date},${t.cost:.2f},{t.request_count},${t.cumulative_cost:.2f}\n"
            )
        
        return output.getvalue()
    
    def export_markdown(self, report: CostReport) -> str:
        """Export report as Markdown."""
        lines = [
            f"# Cost Report for {report.user_id}",
            "",
            f"**Period:** {report.period_start[:10]} to {report.period_end[:10]}",
            f"**Generated:** {report.generated_at[:19]}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Cost | ${report.total_cost:.2f} |",
            f"| Total Requests | {report.total_requests:,} |",
            f"| Total Tokens | {report.total_tokens:,} |",
            f"| Avg Daily Cost | ${report.average_daily_cost:.2f} |",
            "",
            "## By Provider",
            "",
            "| Provider | Cost | Requests | % of Total |",
            "|----------|------|----------|------------|",
        ]
        
        for ps in report.by_provider:
            lines.append(
                f"| {ps.provider} | ${ps.total_cost:.2f} | "
                f"{ps.request_count:,} | {ps.percentage_of_total:.1f}% |"
            )
        
        lines.extend([
            "",
            "## Recommendations",
            "",
        ])
        
        for rec in report.recommendations:
            lines.append(f"- {rec}")
        
        return "\n".join(lines)
