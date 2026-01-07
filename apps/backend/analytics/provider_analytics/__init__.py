"""
Provider Analytics Module - Phase 8 Implementation.

Advanced analytics for comparing and optimizing LLM provider usage.

8 Supported Providers (Equal Treatment):
- copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
"""

from .provider_comparison import ProviderComparison, ComparisonResult
from .provider_metrics import ProviderMetricsTracker, ProviderHealth
from .usage_optimizer import UsageOptimizer, OptimizationRecommendation

__all__ = [
    "ProviderComparison",
    "ComparisonResult",
    "ProviderMetricsTracker",
    "ProviderHealth",
    "UsageOptimizer",
    "OptimizationRecommendation",
]
