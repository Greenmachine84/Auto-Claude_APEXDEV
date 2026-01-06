"""LLM metrics collection.

Part of Phase 2: LLM Architecture
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading

from ..types import ProviderType, LLMUsage

logger = logging.getLogger(__name__)


class MetricType(Enum):
    REQUEST = "request"
    SUCCESS = "success"
    ERROR = "error"
    LATENCY = "latency"
    TOKENS = "tokens"
    COST = "cost"


@dataclass
class MetricEvent:
    """A single metric event."""
    metric_type: MetricType
    provider: ProviderType
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderMetrics:
    """Aggregated metrics for a provider."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    total_cost: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests


class LLMMetrics:
    """Collects and aggregates LLM metrics."""
    
    def __init__(self, window_minutes: int = 60):
        self._window = timedelta(minutes=window_minutes)
        self._events: List[MetricEvent] = []
        self._provider_metrics: Dict[ProviderType, ProviderMetrics] = {}
        self._lock = threading.RLock()
    
    def record_success(self, provider: ProviderType, latency_ms: float, usage: LLMUsage) -> None:
        with self._lock:
            metrics = self._get_or_create(provider)
            metrics.total_requests += 1
            metrics.successful_requests += 1
            metrics.total_latency_ms += latency_ms
            metrics.min_latency_ms = min(metrics.min_latency_ms, latency_ms)
            metrics.max_latency_ms = max(metrics.max_latency_ms, latency_ms)
            metrics.total_tokens += usage.total_tokens
            metrics.prompt_tokens += usage.prompt_tokens
            metrics.completion_tokens += usage.completion_tokens
            
            self._events.append(MetricEvent(
                metric_type=MetricType.SUCCESS, provider=provider, value=latency_ms
            ))
    
    def record_error(self, provider: ProviderType, error: str) -> None:
        with self._lock:
            metrics = self._get_or_create(provider)
            metrics.total_requests += 1
            metrics.failed_requests += 1
            
            self._events.append(MetricEvent(
                metric_type=MetricType.ERROR, provider=provider, value=1,
                metadata={"error": error}
            ))
    
    def get_provider_metrics(self, provider: ProviderType) -> ProviderMetrics:
        with self._lock:
            return self._get_or_create(provider)
    
    def summary(self) -> Dict[str, Any]:
        with self._lock:
            self._cleanup_old_events()
            
            return {
                "providers": {
                    pt.value: {
                        "requests": m.total_requests,
                        "success_rate": m.success_rate,
                        "avg_latency_ms": m.avg_latency_ms,
                        "total_tokens": m.total_tokens
                    }
                    for pt, m in self._provider_metrics.items()
                },
                "total_requests": sum(m.total_requests for m in self._provider_metrics.values()),
                "total_tokens": sum(m.total_tokens for m in self._provider_metrics.values()),
                "window_minutes": self._window.total_seconds() / 60
            }
    
    def _get_or_create(self, provider: ProviderType) -> ProviderMetrics:
        if provider not in self._provider_metrics:
            self._provider_metrics[provider] = ProviderMetrics()
        return self._provider_metrics[provider]
    
    def _cleanup_old_events(self) -> None:
        cutoff = datetime.utcnow() - self._window
        self._events = [e for e in self._events if e.timestamp > cutoff]
