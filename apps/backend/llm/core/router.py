"""LLM request router.

Part of Phase 2: LLM Architecture
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import random

from ..types import RouterConfig, RoutingStrategy, ProviderType

if TYPE_CHECKING:
    from .provider_registry import ProviderRegistry
    from ..providers import BaseLLMProvider
    from .llm_manager import ChatRequest

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Result of routing decision."""
    provider_type: ProviderType
    reason: str
    alternatives: List[ProviderType] = field(default_factory=list)
    latency_estimate_ms: float = 0.0


class LLMRouter:
    """Routes requests to appropriate LLM providers."""
    
    def __init__(self, config: RouterConfig, registry: "ProviderRegistry"):
        self._config = config
        self._registry = registry
        self._round_robin_idx = 0
        self._latency_cache: Dict[ProviderType, float] = {}
    
    def route(self, request: "ChatRequest") -> "BaseLLMProvider":
        if request.provider:
            provider = self._registry.get(request.provider)
            if provider and self._registry.is_available(request.provider):
                return provider
            logger.warning("Requested provider %s unavailable", request.provider.value)
        
        result = self._select_provider(request)
        provider = self._registry.get(result.provider_type)
        
        if not provider:
            raise RuntimeError(f"No provider available for routing")
        
        logger.debug("Routed to %s: %s", result.provider_type.value, result.reason)
        return provider
    
    def _select_provider(self, request: "ChatRequest") -> RouteResult:
        strategy = self._config.strategy
        
        if strategy == RoutingStrategy.PRIORITY:
            return self._route_by_priority()
        elif strategy == RoutingStrategy.ROUND_ROBIN:
            return self._route_round_robin()
        elif strategy == RoutingStrategy.LEAST_LATENCY:
            return self._route_least_latency()
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            return self._route_cost_optimized(request)
        else:
            return self._route_by_priority()
    
    def _route_by_priority(self) -> RouteResult:
        providers = self._registry.get_by_priority()
        if not providers:
            raise RuntimeError("No providers available")
        
        selected = providers[0]
        return RouteResult(
            provider_type=selected.provider_type,
            reason="highest_priority",
            alternatives=[p.provider_type for p in providers[1:3]]
        )
    
    def _route_round_robin(self) -> RouteResult:
        healthy = self._registry.get_healthy()
        if not healthy:
            raise RuntimeError("No healthy providers")
        
        self._round_robin_idx = (self._round_robin_idx + 1) % len(healthy)
        selected = healthy[self._round_robin_idx]
        
        return RouteResult(
            provider_type=selected.provider_type,
            reason="round_robin",
            alternatives=[p.provider_type for p in healthy if p != selected][:2]
        )
    
    def _route_least_latency(self) -> RouteResult:
        healthy = self._registry.get_healthy()
        if not healthy:
            raise RuntimeError("No healthy providers")
        
        # Sort by cached latency
        sorted_providers = sorted(
            healthy,
            key=lambda p: self._latency_cache.get(p.provider_type, float('inf'))
        )
        selected = sorted_providers[0]
        
        return RouteResult(
            provider_type=selected.provider_type,
            reason="least_latency",
            latency_estimate_ms=self._latency_cache.get(selected.provider_type, 0)
        )
    
    def _route_cost_optimized(self, request: "ChatRequest") -> RouteResult:
        # For now, default to priority routing
        return self._route_by_priority()
    
    def update_latency(self, provider_type: ProviderType, latency_ms: float) -> None:
        # Exponential moving average
        current = self._latency_cache.get(provider_type, latency_ms)
        self._latency_cache[provider_type] = 0.7 * current + 0.3 * latency_ms
