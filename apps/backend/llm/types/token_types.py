"""Token counting and cost types.

Part of Phase 2: LLM Architecture
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenUsage:
    """Token usage for a single request."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> "TokenUsage":
        """Create from dictionary."""
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )

    @classmethod
    def zero(cls) -> "TokenUsage":
        """Create zero usage."""
        return cls(0, 0, 0)

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        """Add two usages together."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class TokenCost:
    """Cost breakdown for token usage."""

    input_cost: float
    output_cost: float
    total_cost: float
    currency: str = "USD"

    @classmethod
    def calculate(
        cls, usage: TokenUsage, input_price_per_1k: float, output_price_per_1k: float
    ) -> "TokenCost":
        """Calculate cost from usage and pricing."""
        input_cost = (usage.prompt_tokens / 1000) * input_price_per_1k
        output_cost = (usage.completion_tokens / 1000) * output_price_per_1k
        return cls(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
        )

    @classmethod
    def zero(cls) -> "TokenCost":
        """Create zero cost."""
        return cls(0.0, 0.0, 0.0)

    def __add__(self, other: "TokenCost") -> "TokenCost":
        """Add two costs together."""
        return TokenCost(
            input_cost=self.input_cost + other.input_cost,
            output_cost=self.output_cost + other.output_cost,
            total_cost=self.total_cost + other.total_cost,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "total_cost": self.total_cost,
            "currency": self.currency,
        }


@dataclass
class TokenLimit:
    """Token limits for a model or context."""

    max_input_tokens: int
    max_output_tokens: int
    max_total_tokens: int

    def can_fit(self, usage: TokenUsage) -> bool:
        """Check if usage fits within limits."""
        return (
            usage.prompt_tokens <= self.max_input_tokens
            and usage.completion_tokens <= self.max_output_tokens
            and usage.total_tokens <= self.max_total_tokens
        )

    def remaining(self, current_prompt_tokens: int) -> int:
        """Calculate remaining tokens for output."""
        remaining_total = self.max_total_tokens - current_prompt_tokens
        return min(remaining_total, self.max_output_tokens)


@dataclass
class TokenBudget:
    """Token budget for cost management."""

    max_tokens: int
    max_cost: float
    current_tokens: int = 0
    current_cost: float = 0.0

    def can_spend(self, estimated_tokens: int, estimated_cost: float) -> bool:
        """Check if spending is within budget."""
        return (
            self.current_tokens + estimated_tokens <= self.max_tokens
            and self.current_cost + estimated_cost <= self.max_cost
        )

    def spend(self, usage: TokenUsage, cost: TokenCost) -> None:
        """Record spending."""
        self.current_tokens += usage.total_tokens
        self.current_cost += cost.total_cost

    @property
    def remaining_tokens(self) -> int:
        """Get remaining token budget."""
        return max(0, self.max_tokens - self.current_tokens)

    @property
    def remaining_cost(self) -> float:
        """Get remaining cost budget."""
        return max(0.0, self.max_cost - self.current_cost)

    @property
    def utilization_percent(self) -> float:
        """Get budget utilization percentage."""
        token_util = (
            (self.current_tokens / self.max_tokens) * 100 if self.max_tokens > 0 else 0
        )
        cost_util = (
            (self.current_cost / self.max_cost) * 100 if self.max_cost > 0 else 0
        )
        return max(token_util, cost_util)


@dataclass
class TokenCounter:
    """Accumulated token counting."""

    total: TokenUsage = field(default_factory=TokenUsage.zero)
    by_model: dict[str, TokenUsage] = field(default_factory=dict)
    by_provider: dict[str, TokenUsage] = field(default_factory=dict)

    def record(
        self,
        usage: TokenUsage,
        model: str | None = None,
        provider: str | None = None,
    ) -> None:
        """Record token usage."""
        self.total = self.total + usage

        if model:
            if model not in self.by_model:
                self.by_model[model] = TokenUsage.zero()
            self.by_model[model] = self.by_model[model] + usage

        if provider:
            if provider not in self.by_provider:
                self.by_provider[provider] = TokenUsage.zero()
            self.by_provider[provider] = self.by_provider[provider] + usage

    def reset(self) -> None:
        """Reset all counters."""
        self.total = TokenUsage.zero()
        self.by_model.clear()
        self.by_provider.clear()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total.to_dict(),
            "by_model": {k: v.to_dict() for k, v in self.by_model.items()},
            "by_provider": {k: v.to_dict() for k, v in self.by_provider.items()},
        }


# Common token limits for popular models
MODEL_TOKEN_LIMITS = {
    # OpenAI
    "gpt-4o": TokenLimit(128000, 16384, 128000),
    "gpt-4o-mini": TokenLimit(128000, 16384, 128000),
    "gpt-4-turbo": TokenLimit(128000, 4096, 128000),
    "gpt-4": TokenLimit(8192, 8192, 8192),
    # Anthropic
    "claude-3-opus": TokenLimit(200000, 4096, 200000),
    "claude-3-sonnet": TokenLimit(200000, 4096, 200000),
    "claude-3-haiku": TokenLimit(200000, 4096, 200000),
    "claude-3.5-sonnet": TokenLimit(200000, 8192, 200000),
    # Google Gemini
    "gemini-pro": TokenLimit(32000, 8192, 32000),
    "gemini-1.5-pro": TokenLimit(2000000, 8192, 2000000),
    "gemini-1.5-flash": TokenLimit(1000000, 8192, 1000000),
}


def get_model_limits(model: str) -> TokenLimit:
    """Get token limits for a model."""
    # Try exact match
    if model in MODEL_TOKEN_LIMITS:
        return MODEL_TOKEN_LIMITS[model]

    # Try prefix match
    for key, limits in MODEL_TOKEN_LIMITS.items():
        if model.startswith(key):
            return limits

    # Default limits
    return TokenLimit(8192, 4096, 8192)
