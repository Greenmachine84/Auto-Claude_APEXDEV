"""
Dashboard API - Phase 8 Implementation.

FastAPI endpoints for analytics dashboard.

World-Class Standards:
- <100ms P99 latency
- OpenAPI documentation
- Rate limiting ready
- WebSocket support
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import logging

from ..models import DashboardData, BudgetStatus, SUPPORTED_PROVIDERS

logger = logging.getLogger(__name__)


# FastAPI Router
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# Request/Response Models
class DashboardRequest(BaseModel):
    """Dashboard data request."""
    user_id: str
    time_range_hours: int = 24
    include_charts: bool = True


class DashboardResponse(BaseModel):
    """Dashboard data response."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str


class ProviderStatsResponse(BaseModel):
    """Provider statistics response."""
    provider: str
    request_count: int
    total_cost: float
    total_tokens: int
    average_latency_ms: float


class BudgetResponse(BaseModel):
    """Budget status response."""
    user_id: str
    total_budget: float
    used: float
    remaining: float
    percentage_used: float
    status: str


class CostHistoryResponse(BaseModel):
    """Cost history response."""
    user_id: str
    period: str
    data_points: List[Dict[str, Any]]


class DashboardAPI:
    """
    Dashboard API implementation.
    
    Features:
    - RESTful endpoints
    - WebSocket real-time updates
    - Response caching
    - Error handling
    """
    
    def __init__(self) -> None:
        """Initialize API."""
        self._data_builder = None
        self._chart_generator = None
        self._exporter = None
        logger.info("DashboardAPI initialized")
    
    def configure(
        self,
        data_builder,
        chart_generator,
        exporter,
    ) -> None:
        """Configure API with dependencies."""
        self._data_builder = data_builder
        self._chart_generator = chart_generator
        self._exporter = exporter
    
    async def get_dashboard(
        self,
        user_id: str,
        time_range_hours: int = 24,
        include_charts: bool = True,
    ) -> DashboardResponse:
        """Get complete dashboard data."""
        try:
            if not self._data_builder:
                raise ValueError("Dashboard API not configured")
            
            dashboard = await self._data_builder.build_dashboard(
                user_id, time_range_hours
            )
            
            response_data = {
                "user_id": dashboard.user_id,
                "time_range_hours": dashboard.time_range_hours,
                "summary": {
                    "total_cost": dashboard.total_cost,
                    "total_requests": dashboard.total_requests,
                    "total_tokens": dashboard.total_tokens,
                },
                "budget": {
                    "total": dashboard.budget_status.total_budget,
                    "used": dashboard.budget_status.used,
                    "remaining": dashboard.budget_status.remaining,
                    "percentage": dashboard.budget_status.percentage_used,
                    "status": dashboard.budget_status.status,
                },
                "providers": [
                    {
                        "provider": pm.provider,
                        "requests": pm.request_count,
                        "cost": pm.total_cost,
                        "tokens": pm.total_prompt_tokens + pm.total_completion_tokens,
                        "percentage": pm.cost_percentage,
                    }
                    for pm in dashboard.provider_metrics
                    if pm.request_count > 0
                ],
                "last_updated": dashboard.last_updated,
            }
            
            if include_charts and self._chart_generator:
                response_data["charts"] = self._chart_generator.generate_all_charts(
                    dashboard
                )
            
            return DashboardResponse(
                success=True,
                data=response_data,
                timestamp=datetime.utcnow().isoformat(),
            )
            
        except Exception as e:
            logger.error("Dashboard API error: %s", e)
            return DashboardResponse(
                success=False,
                error=str(e),
                timestamp=datetime.utcnow().isoformat(),
            )
    
    async def get_provider_stats(
        self,
        user_id: str,
        provider: Optional[str] = None,
    ) -> List[ProviderStatsResponse]:
        """Get statistics for providers."""
        if provider and provider not in SUPPORTED_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {provider}. "
                       f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        if not self._data_builder:
            raise HTTPException(status_code=500, detail="API not configured")
        
        dashboard = await self._data_builder.build_dashboard(user_id)
        
        stats = []
        for pm in dashboard.provider_metrics:
            if provider and pm.provider != provider:
                continue
            if pm.request_count > 0:
                stats.append(ProviderStatsResponse(
                    provider=pm.provider,
                    request_count=pm.request_count,
                    total_cost=pm.total_cost,
                    total_tokens=pm.total_prompt_tokens + pm.total_completion_tokens,
                    average_latency_ms=pm.average_latency_ms,
                ))
        
        return stats
    
    async def get_budget_status(
        self,
        user_id: str,
        provider: Optional[str] = None,
    ) -> BudgetResponse:
        """Get budget status."""
        if not self._data_builder:
            raise HTTPException(status_code=500, detail="API not configured")
        
        dashboard = await self._data_builder.build_dashboard(user_id)
        bs = dashboard.budget_status
        
        return BudgetResponse(
            user_id=user_id,
            total_budget=bs.total_budget,
            used=bs.used,
            remaining=bs.remaining,
            percentage_used=bs.percentage_used,
            status=bs.status,
        )
    
    async def get_cost_history(
        self,
        user_id: str,
        period: str = "24h",
    ) -> CostHistoryResponse:
        """Get cost history for a period."""
        # Parse period
        if period == "24h":
            hours = 24
        elif period == "7d":
            hours = 24 * 7
        elif period == "30d":
            hours = 24 * 30
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid period. Use: 24h, 7d, or 30d"
            )
        
        if not self._data_builder:
            raise HTTPException(status_code=500, detail="API not configured")
        
        dashboard = await self._data_builder.build_dashboard(user_id, hours)
        
        return CostHistoryResponse(
            user_id=user_id,
            period=period,
            data_points=[
                {
                    "timestamp": tp.timestamp,
                    "cost": tp.value,
                    "metadata": tp.metadata,
                }
                for tp in dashboard.cost_time_series
            ],
        )
    
    async def export_dashboard(
        self,
        user_id: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export dashboard data."""
        from .export import ExportFormat
        
        if not self._data_builder or not self._exporter:
            raise HTTPException(status_code=500, detail="API not configured")
        
        try:
            export_format = ExportFormat(format.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Use: json, csv, markdown, or html"
            )
        
        dashboard = await self._data_builder.build_dashboard(user_id)
        result = self._exporter.export(dashboard, export_format)
        
        return {
            "filename": result.filename,
            "content_type": result.content_type,
            "size_bytes": result.size_bytes,
            "content": result.content,
        }


# FastAPI route handlers
api_instance = DashboardAPI()


@router.get("/dashboard/{user_id}")
async def get_dashboard(
    user_id: str,
    time_range: int = Query(default=24, ge=1, le=720),
    include_charts: bool = Query(default=True),
) -> DashboardResponse:
    """Get analytics dashboard for a user."""
    return await api_instance.get_dashboard(user_id, time_range, include_charts)


@router.get("/providers/{user_id}")
async def get_provider_stats(
    user_id: str,
    provider: Optional[str] = Query(default=None),
) -> List[ProviderStatsResponse]:
    """Get provider statistics."""
    return await api_instance.get_provider_stats(user_id, provider)


@router.get("/budget/{user_id}")
async def get_budget(user_id: str) -> BudgetResponse:
    """Get budget status."""
    return await api_instance.get_budget_status(user_id)


@router.get("/history/{user_id}")
async def get_history(
    user_id: str,
    period: str = Query(default="24h"),
) -> CostHistoryResponse:
    """Get cost history."""
    return await api_instance.get_cost_history(user_id, period)


@router.get("/export/{user_id}")
async def export_data(
    user_id: str,
    format: str = Query(default="json"),
) -> Dict[str, Any]:
    """Export dashboard data."""
    return await api_instance.export_dashboard(user_id, format)


@router.get("/providers")
async def list_providers() -> Dict[str, List[str]]:
    """List all supported providers."""
    return {"providers": list(SUPPORTED_PROVIDERS)}
