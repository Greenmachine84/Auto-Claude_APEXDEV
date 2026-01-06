"""LLM core module - Central LLM management.

Provides core LLM functionality:
- LLM Manager (singleton)
- Provider registry
- Request routing
- Fallback handling
- Metrics collection

Part of Phase 2: LLM Architecture
"""

from .llm_manager import LLMManager
from .provider_registry import ProviderRegistry
from .router import LLMRouter, RouteResult
from .fallback import FallbackHandler, FallbackResult
from .metrics import LLMMetrics, MetricEvent

__all__ = [
    "LLMManager",
    "ProviderRegistry",
    "LLMRouter",
    "RouteResult",
    "FallbackHandler",
    "FallbackResult",
    "LLMMetrics",
    "MetricEvent",
]
