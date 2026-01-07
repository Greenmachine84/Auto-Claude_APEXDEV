"""
Usage Optimizer - Phase 8 Implementation.

Intelligent optimization recommendations for LLM usage.

World-Class Standards:
- Cost optimization suggestions
- Model right-sizing
- Provider routing recommendations
- Usage pattern analysis
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from ..models import SUPPORTED_PROVIDERS
from ..cost.cost_tracker import CostTracker
from ..cost.pricing import PricingEngine

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of optimization recommendations."""
    COST_REDUCTION = "cost_reduction"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    MODEL_SWITCH = "model_switch"
    PROVIDER_SWITCH = "provider_switch"
    USAGE_PATTERN = "usage_pattern"
    BUDGET_WARNING = "budget_warning"


class Priority(Enum):
    """Recommendation priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OptimizationRecommendation:
    """Single optimization recommendation."""
    type: RecommendationType
    priority: Priority
    title: str
    description: str
    current_state: str
    recommended_action: str
    estimated_savings: Optional[float] = None
    estimated_savings_percent: Optional[float] = None
    affected_provider: Optional[str] = None
    affected_model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "current_state": self.current_state,
            "recommended_action": self.recommended_action,
            "estimated_savings": self.estimated_savings,
            "estimated_savings_percent": self.estimated_savings_percent,
            "affected_provider": self.affected_provider,
            "affected_model": self.affected_model,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class UsageOptimizer:
    """
    Intelligent usage optimization engine.
    
    Features:
    - Cost reduction analysis
    - Model right-sizing
    - Provider routing optimization
    - Pattern-based recommendations
    """
    
    def __init__(
        self,
        cost_tracker: CostTracker,
        pricing_engine: PricingEngine,
    ) -> None:
        """Initialize optimizer."""
        self.cost_tracker = cost_tracker
        self.pricing = pricing_engine
        
        # Model tiers for right-sizing
        self._model_tiers = {
            "premium": [
                "gpt-4", "gpt-4-turbo", "claude-3-opus", "gemini-1.5-pro"
            ],
            "standard": [
                "gpt-4o", "claude-3-sonnet", "claude-3.5-sonnet", "gemini-pro"
            ],
            "economy": [
                "gpt-4o-mini", "gpt-3.5-turbo", "claude-3-haiku", "gemini-1.5-flash"
            ],
            "local": [
                "llama3", "codellama", "mistral"
            ],
        }
        
        logger.info("UsageOptimizer initialized")
    
    async def analyze(
        self,
        user_id: str,
        time_range_hours: int = 168,  # 1 week
    ) -> List[OptimizationRecommendation]:
        """
        Analyze usage and generate recommendations.
        
        Args:
            user_id: User identifier
            time_range_hours: Hours of data to analyze
            
        Returns:
            List of optimization recommendations
        """
        start_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Get usage data
        summary = await self.cost_tracker.get_user_cost(
            user_id, start_time=start_time
        )
        records = await self.cost_tracker.get_records(user_id=user_id, limit=10000)
        
        # Filter records
        recent = [
            r for r in records
            if datetime.fromisoformat(r.timestamp) >= start_time
        ]
        
        recommendations: List[OptimizationRecommendation] = []
        
        # Run all analyzers
        recommendations.extend(self._analyze_cost_concentration(summary, recent))
        recommendations.extend(self._analyze_model_right_sizing(recent))
        recommendations.extend(self._analyze_local_provider_usage(summary))
        recommendations.extend(self._analyze_token_efficiency(recent))
        recommendations.extend(self._analyze_usage_patterns(recent))
        
        # Sort by priority
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }
        recommendations.sort(key=lambda r: priority_order[r.priority])
        
        return recommendations
    
    def _analyze_cost_concentration(
        self,
        summary,
        records: List,
    ) -> List[OptimizationRecommendation]:
        """Check for over-reliance on expensive providers."""
        recommendations = []
        
        if summary.total_cost == 0:
            return recommendations
        
        for provider, cost in summary.by_provider.items():
            percentage = cost / summary.total_cost * 100
            
            if percentage > 80 and provider not in ["ollama", "lmstudio", "copilot"]:
                recommendations.append(OptimizationRecommendation(
                    type=RecommendationType.PROVIDER_SWITCH,
                    priority=Priority.MEDIUM,
                    title=f"High concentration on {provider}",
                    description=(
                        f"Over {percentage:.0f}% of costs come from {provider}. "
                        "Consider diversifying to reduce vendor lock-in and costs."
                    ),
                    current_state=f"{percentage:.1f}% of spend on {provider}",
                    recommended_action=(
                        "Evaluate alternative providers for some use cases"
                    ),
                    affected_provider=provider,
                    estimated_savings_percent=10.0,
                ))
        
        return recommendations
    
    def _analyze_model_right_sizing(
        self,
        records: List,
    ) -> List[OptimizationRecommendation]:
        """Check if premium models are overused."""
        recommendations = []
        
        model_usage: Dict[str, Dict[str, Any]] = {}
        
        for r in records:
            key = f"{r.provider}/{r.model}"
            if key not in model_usage:
                model_usage[key] = {"cost": 0.0, "count": 0, "tokens": 0}
            
            model_usage[key]["cost"] += r.cost_usd
            model_usage[key]["count"] += 1
            model_usage[key]["tokens"] += r.prompt_tokens + r.completion_tokens
        
        # Check premium model usage
        premium_cost = 0.0
        total_cost = 0.0
        
        for model_key, usage in model_usage.items():
            total_cost += usage["cost"]
            model_name = model_key.split("/")[-1] if "/" in model_key else model_key
            
            if any(pm in model_name.lower() for pm in ["gpt-4", "opus", "1.5-pro"]):
                premium_cost += usage["cost"]
        
        if total_cost > 0 and premium_cost / total_cost > 0.7:
            recommendations.append(OptimizationRecommendation(
                type=RecommendationType.MODEL_SWITCH,
                priority=Priority.HIGH,
                title="Consider model right-sizing",
                description=(
                    f"Premium models account for {premium_cost/total_cost*100:.0f}% of costs. "
                    "Many tasks may work well with more economical models."
                ),
                current_state=f"${premium_cost:.2f} on premium models",
                recommended_action=(
                    "Use GPT-4o-mini, Claude Haiku, or Gemini Flash for simpler tasks"
                ),
                estimated_savings=premium_cost * 0.5,
                estimated_savings_percent=35.0,
            ))
        
        return recommendations
    
    def _analyze_local_provider_usage(
        self,
        summary,
    ) -> List[OptimizationRecommendation]:
        """Check if local providers are underutilized."""
        recommendations = []
        
        local_providers = ["ollama", "lmstudio"]
        local_cost = sum(
            summary.by_provider.get(p, 0.0) for p in local_providers
        )
        
        if summary.total_cost > 10 and local_cost == 0:
            recommendations.append(OptimizationRecommendation(
                type=RecommendationType.COST_REDUCTION,
                priority=Priority.MEDIUM,
                title="Use local models for development",
                description=(
                    "Local models (Ollama, LM Studio) have zero API costs. "
                    "Consider using them for development, testing, and iteration."
                ),
                current_state="No local model usage detected",
                recommended_action=(
                    "Set up Ollama or LM Studio for development workflows"
                ),
                estimated_savings=summary.total_cost * 0.2,
                estimated_savings_percent=20.0,
            ))
        
        return recommendations
    
    def _analyze_token_efficiency(
        self,
        records: List,
    ) -> List[OptimizationRecommendation]:
        """Check token usage efficiency."""
        recommendations = []
        
        if not records:
            return recommendations
        
        # Calculate average tokens per request
        total_tokens = sum(r.prompt_tokens + r.completion_tokens for r in records)
        avg_tokens = total_tokens / len(records)
        
        # Check for potentially inefficient prompts
        high_token_requests = [
            r for r in records
            if r.prompt_tokens > 4000  # Arbitrary threshold
        ]
        
        if len(high_token_requests) > len(records) * 0.3:
            recommendations.append(OptimizationRecommendation(
                type=RecommendationType.USAGE_PATTERN,
                priority=Priority.LOW,
                title="Optimize prompt sizes",
                description=(
                    f"{len(high_token_requests)} requests ({len(high_token_requests)/len(records)*100:.0f}%) "
                    "use more than 4000 prompt tokens. Consider prompt optimization."
                ),
                current_state=f"Average {avg_tokens:.0f} tokens per request",
                recommended_action=(
                    "Review and optimize system prompts, use caching where possible"
                ),
                estimated_savings_percent=10.0,
            ))
        
        return recommendations
    
    def _analyze_usage_patterns(
        self,
        records: List,
    ) -> List[OptimizationRecommendation]:
        """Analyze usage patterns for optimization opportunities."""
        recommendations = []
        
        if not records:
            return recommendations
        
        # Check for off-hours usage that could use local models
        off_hours_requests = [
            r for r in records
            if 0 <= datetime.fromisoformat(r.timestamp).hour < 6
        ]
        
        if len(off_hours_requests) > len(records) * 0.1:
            recommendations.append(OptimizationRecommendation(
                type=RecommendationType.USAGE_PATTERN,
                priority=Priority.LOW,
                title="Optimize off-hours processing",
                description=(
                    f"{len(off_hours_requests)} requests occur during off-hours. "
                    "These could potentially use local or batch processing."
                ),
                current_state=f"{len(off_hours_requests)} requests between midnight and 6am",
                recommended_action=(
                    "Consider batch processing or local model usage for async tasks"
                ),
            ))
        
        return recommendations
    
    async def get_quick_wins(
        self,
        user_id: str,
        max_recommendations: int = 3,
    ) -> List[OptimizationRecommendation]:
        """Get top quick-win recommendations."""
        all_recs = await self.analyze(user_id)
        
        # Filter to actionable high-impact items
        quick_wins = [
            r for r in all_recs
            if r.priority in [Priority.HIGH, Priority.CRITICAL]
            or (r.estimated_savings_percent and r.estimated_savings_percent > 20)
        ]
        
        return quick_wins[:max_recommendations]
    
    async def estimate_potential_savings(
        self,
        user_id: str,
        time_range_hours: int = 720,  # 30 days
    ) -> Dict[str, Any]:
        """Estimate total potential savings."""
        recommendations = await self.analyze(user_id, time_range_hours)
        
        total_savings = sum(
            r.estimated_savings or 0 for r in recommendations
        )
        
        summary = await self.cost_tracker.get_user_cost(user_id)
        
        return {
            "current_monthly_cost": summary.total_cost,
            "potential_savings": total_savings,
            "savings_percentage": (total_savings / summary.total_cost * 100) if summary.total_cost > 0 else 0,
            "recommendation_count": len(recommendations),
            "high_priority_count": sum(1 for r in recommendations if r.priority in [Priority.HIGH, Priority.CRITICAL]),
        }
