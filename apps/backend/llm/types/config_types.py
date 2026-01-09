"""Configuration type definitions.

Part of Phase 2: LLM Architecture
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .provider_types import ProviderConfig, ProviderType


class RoutingStrategy(Enum):
    """Strategy for routing requests to providers."""

    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    LEAST_LATENCY = "least_latency"
    COST_OPTIMIZED = "cost_optimized"
    CAPABILITY_MATCH = "capability_match"


class FallbackTrigger(Enum):
    """Conditions that trigger fallback."""

    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CONTENT_FILTER = "content_filter"
    CAPACITY = "capacity"


@dataclass
class RouterConfig:
    """Configuration for the LLM router."""

    strategy: RoutingStrategy = RoutingStrategy.PRIORITY
    enable_fallback: bool = True
    max_fallback_attempts: int = 3
    health_check_interval_seconds: int = 60
    cache_responses: bool = True
    cache_ttl_seconds: int = 300
    log_requests: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "enable_fallback": self.enable_fallback,
            "max_fallback_attempts": self.max_fallback_attempts,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "cache_responses": self.cache_responses,
        }


@dataclass
class FallbackConfig:
    """Configuration for fallback behavior."""

    triggers: list[FallbackTrigger] = field(
        default_factory=lambda: [FallbackTrigger.ERROR, FallbackTrigger.TIMEOUT]
    )
    fallback_chain: list[ProviderType] = field(default_factory=list)
    retry_on_fallback: bool = True
    preserve_context: bool = True
    notify_on_fallback: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "triggers": [t.value for t in self.triggers],
            "fallback_chain": [p.value for p in self.fallback_chain],
            "retry_on_fallback": self.retry_on_fallback,
            "preserve_context": self.preserve_context,
        }


@dataclass
class LLMConfig:
    """Master configuration for the LLM system."""

    providers: dict[ProviderType, ProviderConfig] = field(default_factory=dict)
    default_provider: ProviderType | None = None
    router: RouterConfig = field(default_factory=RouterConfig)
    fallback: FallbackConfig = field(default_factory=FallbackConfig)
    default_temperature: float = 0.7
    default_max_tokens: int = 4096
    enable_streaming: bool = True
    enable_caching: bool = True

    def add_provider(self, config: ProviderConfig) -> None:
        self.providers[config.provider_type] = config
        if self.default_provider is None:
            self.default_provider = config.provider_type

    def get_provider(self, provider_type: ProviderType) -> ProviderConfig | None:
        return self.providers.get(provider_type)

    def enabled_providers(self) -> list[ProviderType]:
        return [pt for pt, cfg in self.providers.items() if cfg.enabled]

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": {
                pt.value: cfg.to_dict() for pt, cfg in self.providers.items()
            },
            "default_provider": self.default_provider.value
            if self.default_provider
            else None,
            "router": self.router.to_dict(),
            "fallback": self.fallback.to_dict(),
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens,
            "enable_streaming": self.enable_streaming,
        }
