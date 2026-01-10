"""LLM core module - Central LLM management.

Provides core LLM functionality:
- LLM Manager (singleton)
- Provider registry
- Request routing
- Fallback handling
- Metrics collection

Part of Phase 2: LLM Architecture
"""

from .fallback import FallbackHandler, FallbackResult
from .llm_manager import LLMManager
from .metrics import LLMMetrics, MetricEvent
from .provider_registry import ProviderRegistry
from .router import LLMRouter, RouteResult

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
