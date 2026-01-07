"""
Provider Comparison - Phase 8 Implementation.

Multi-dimensional comparison of LLM providers.

World-Class Standards:
- Cost efficiency analysis
- Quality scoring
- Latency comparison
- Recommendation engine
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from ..models import SUPPORTED_PROVIDERS
from ..cost.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class ComparisonDimension(Enum):
    """Dimensions for provider comparison."""
    COST = "cost"
    LATENCY = "latency"
    QUALITY = "quality"
    RELIABILITY = "reliability"
    THROUGHPUT = "throughput"


@dataclass
class ProviderScore:
    """Score for a single provider."""
    provider: str
    cost_score: float  # 0-100, lower cost = higher score
    latency_score: float  # 0-100, lower latency = higher score
    quality_score: float  # 0-100, based on success rate
    reliability_score: float  # 0-100, based on uptime/errors
    throughput_score: float  # 0-100, based on requests handled
    overall_score: float  # Weighted average
    rank: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "scores": {
                "cost": self.cost_score,
                "latency": self.latency_score,
                "quality": self.quality_score,
                "reliability": self.reliability_score,
                "throughput": self.throughput_score,
                "overall": self.overall_score,
            },
            "rank": self.rank,
        }


@dataclass
class ComparisonResult:
    """Result of provider comparison."""
    providers: List[ProviderScore]
    best_overall: str
    best_by_dimension: Dict[str, str]
    recommendations: List[str]
    analysis_period: str
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "providers": [p.to_dict() for p in self.providers],
            "best_overall": self.best_overall,
            "best_by_dimension": self.best_by_dimension,
            "recommendations": self.recommendations,
            "analysis_period": self.analysis_period,
            "generated_at": self.generated_at,
        }


class ProviderComparison:
    """
    Multi-dimensional provider comparison.
    
    Features:
    - Cost efficiency ranking
    - Performance benchmarking
    - Quality assessment
    - Smart recommendations
    """
    
    def __init__(
        self,
        cost_tracker: CostTracker,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initialize comparison engine."""
        self.cost_tracker = cost_tracker
        
        # Default weights for overall score
        self.weights = weights or {
            "cost": 0.30,
            "latency": 0.20,
            "quality": 0.25,
            "reliability": 0.15,
            "throughput": 0.10,
        }
        
        # Simulated metrics for demonstration
        # In production, these would come from real monitoring
        self._latency_data: Dict[str, List[float]] = {}
        self._error_counts: Dict[str, int] = {}
        self._success_counts: Dict[str, int] = {}
        
        logger.info("ProviderComparison initialized")
    
    async def compare_providers(
        self,
        user_id: str,
        time_range_hours: int = 24,
        include_unused: bool = False,
    ) -> ComparisonResult:
        """
        Compare all providers for a user.
        
        Args:
            user_id: User identifier
            time_range_hours: Hours of data to analyze
            include_unused: Include providers with no usage
            
        Returns:
            Comprehensive comparison result
        """
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Get cost data
        cost_summary = await self.cost_tracker.get_user_cost(
            user_id, start_time=start_time
        )
        records = await self.cost_tracker.get_records(user_id=user_id, limit=10000)
        
        # Calculate metrics per provider
        provider_data: Dict[str, Dict[str, Any]] = {}
        
        for r in records:
            if datetime.fromisoformat(r.timestamp) < start_time:
                continue
            
            if r.provider not in provider_data:
                provider_data[r.provider] = {
                    "total_cost": 0.0,
                    "request_count": 0,
                    "total_tokens": 0,
                    "latencies": [],
                    "errors": 0,
                }
            
            pd = provider_data[r.provider]
            pd["total_cost"] += r.cost_usd
            pd["request_count"] += 1
            pd["total_tokens"] += r.prompt_tokens + r.completion_tokens
        
        # Calculate scores
        scores: List[ProviderScore] = []
        
        # Find max values for normalization
        max_cost = max((pd["total_cost"] for pd in provider_data.values()), default=1)
        max_requests = max((pd["request_count"] for pd in provider_data.values()), default=1)
        
        for provider in SUPPORTED_PROVIDERS:
            if provider not in provider_data:
                if not include_unused:
                    continue
                # Zero scores for unused providers
                scores.append(ProviderScore(
                    provider=provider,
                    cost_score=100.0,  # No cost = perfect score
                    latency_score=50.0,  # Unknown
                    quality_score=50.0,  # Unknown
                    reliability_score=50.0,  # Unknown
                    throughput_score=0.0,  # No usage
                    overall_score=50.0,
                ))
                continue
            
            pd = provider_data[provider]
            
            # Cost score (inverted - lower cost = higher score)
            if max_cost > 0:
                cost_score = 100 * (1 - pd["total_cost"] / max_cost)
            else:
                cost_score = 100.0
            
            # Latency score (simulated - would need real latency tracking)
            latency_score = 80.0  # Placeholder
            
            # Quality score (based on error rate - simulated)
            quality_score = 95.0  # Placeholder
            
            # Reliability score
            reliability_score = 98.0  # Placeholder
            
            # Throughput score
            throughput_score = 100 * pd["request_count"] / max_requests if max_requests > 0 else 0
            
            # Calculate overall score
            overall = (
                cost_score * self.weights["cost"] +
                latency_score * self.weights["latency"] +
                quality_score * self.weights["quality"] +
                reliability_score * self.weights["reliability"] +
                throughput_score * self.weights["throughput"]
            )
            
            scores.append(ProviderScore(
                provider=provider,
                cost_score=round(cost_score, 1),
                latency_score=round(latency_score, 1),
                quality_score=round(quality_score, 1),
                reliability_score=round(reliability_score, 1),
                throughput_score=round(throughput_score, 1),
                overall_score=round(overall, 1),
            ))
        
        # Sort by overall score and assign ranks
        scores.sort(key=lambda x: x.overall_score, reverse=True)
        for i, score in enumerate(scores):
            score.rank = i + 1
        
        # Find best by dimension
        best_by_dim = {
            "cost": max(scores, key=lambda x: x.cost_score).provider if scores else "",
            "latency": max(scores, key=lambda x: x.latency_score).provider if scores else "",
            "quality": max(scores, key=lambda x: x.quality_score).provider if scores else "",
            "reliability": max(scores, key=lambda x: x.reliability_score).provider if scores else "",
            "throughput": max(scores, key=lambda x: x.throughput_score).provider if scores else "",
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, provider_data)
        
        return ComparisonResult(
            providers=scores,
            best_overall=scores[0].provider if scores else "",
            best_by_dimension=best_by_dim,
            recommendations=recommendations,
            analysis_period=f"Last {time_range_hours} hours",
        )
    
    def _generate_recommendations(
        self,
        scores: List[ProviderScore],
        provider_data: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if not scores:
            return ["No usage data available for recommendations"]
        
        # Check for cost optimization
        top_by_cost = max(scores, key=lambda x: x.cost_score)
        most_used = max(scores, key=lambda x: x.throughput_score)
        
        if top_by_cost.provider != most_used.provider:
            recommendations.append(
                f"Consider using {top_by_cost.provider} more - "
                f"it has the best cost efficiency"
            )
        
        # Check for local provider usage
        local_providers = ["ollama", "lmstudio"]
        local_usage = sum(
            s.throughput_score for s in scores
            if s.provider in local_providers
        )
        
        if local_usage < 20:
            recommendations.append(
                "Consider using local providers (ollama, lmstudio) "
                "for development and testing to reduce costs"
            )
        
        # Diversification check
        active_providers = [s for s in scores if s.throughput_score > 0]
        if len(active_providers) == 1:
            recommendations.append(
                f"All usage is on {active_providers[0].provider}. "
                "Consider diversifying to reduce vendor lock-in"
            )
        
        if not recommendations:
            recommendations.append("Provider usage is well optimized")
        
        return recommendations
    
    async def get_cost_efficiency(
        self,
        user_id: str,
        time_range_hours: int = 24,
    ) -> Dict[str, float]:
        """Get cost per 1K tokens for each provider."""
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        records = await self.cost_tracker.get_records(user_id=user_id, limit=10000)
        
        provider_efficiency: Dict[str, Dict[str, float]] = {}
        
        for r in records:
            if datetime.fromisoformat(r.timestamp) < start_time:
                continue
            
            if r.provider not in provider_efficiency:
                provider_efficiency[r.provider] = {"cost": 0.0, "tokens": 0}
            
            provider_efficiency[r.provider]["cost"] += r.cost_usd
            provider_efficiency[r.provider]["tokens"] += r.prompt_tokens + r.completion_tokens
        
        result = {}
        for provider, data in provider_efficiency.items():
            if data["tokens"] > 0:
                result[provider] = (data["cost"] / data["tokens"]) * 1000
            else:
                result[provider] = 0.0
        
        return result
