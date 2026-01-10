"""
Provider Analytics Module - Phase 8 Implementation.

Advanced analytics for comparing and optimizing LLM provider usage.

8 Supported Providers (Equal Treatment):
- copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
"""

from .provider_comparison import ComparisonResult, ProviderComparison
from .provider_metrics import ProviderHealth, ProviderMetricsTracker
from .usage_optimizer import OptimizationRecommendation, UsageOptimizer

__all__ = [
    "ProviderComparison",
    "ComparisonResult",
    "ProviderMetricsTracker",
    "ProviderHealth",
    "UsageOptimizer",
    "OptimizationRecommendation",
]
