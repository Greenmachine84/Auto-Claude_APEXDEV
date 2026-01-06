"""Token usage and cost tracking.

Part of Phase 2: LLM Architecture
"""

import logging
import threading
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage for a single request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    @classmethod
    def from_response(cls, usage_dict: Dict[str, int]) -> "TokenUsage":
        return cls(
            prompt_tokens=usage_dict.get("prompt_tokens", 0),
            completion_tokens=usage_dict.get("completion_tokens", 0),
            total_tokens=usage_dict.get("total_tokens", 0)
        )


@dataclass
class TokenCost:
    """Cost breakdown for token usage."""
    input_cost: float
    output_cost: float
    total_cost: float


@dataclass 
class UsageRecord:
    """A single usage record."""
    timestamp: datetime
    provider: str
    model: str
    usage: TokenUsage
    cost: TokenCost
    task_id: Optional[str] = None
    agent_id: Optional[str] = None


@dataclass
class UsageReport:
    """Aggregated usage report."""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens: int
    total_cost: float
    by_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_model: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_agent: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class CostTracker:
    """Track token usage and costs across providers.
    
    Features:
    - Per-request usage recording
    - Cost calculation
    - Aggregated reports
    - Budget alerts
    """
    
    _instance: Optional["CostTracker"] = None
    _lock = threading.Lock()
    
    # Default pricing per 1K tokens (USD)
    DEFAULT_PRICING = {
        "anthropic": {
            "claude-3-opus": (0.015, 0.075),
            "claude-3-sonnet": (0.003, 0.015),
            "claude-3-haiku": (0.00025, 0.00125),
            "default": (0.003, 0.015)
        },
        "openai": {
            "gpt-4o": (0.005, 0.015),
            "gpt-4o-mini": (0.00015, 0.0006),
            "gpt-4-turbo": (0.01, 0.03),
            "default": (0.005, 0.015)
        },
        "gemini": {
            "gemini-pro": (0.00025, 0.0005),
            "gemini-flash": (0.000075, 0.0003),
            "default": (0.00025, 0.0005)
        },
        "azure": {
            "default": (0.005, 0.015)
        },
        "ollama": {
            "default": (0.0, 0.0)  # Free (local)
        },
        "lmstudio": {
            "default": (0.0, 0.0)  # Free (local)
        },
        "openrouter": {
            "default": (0.002, 0.006)
        },
        "copilot": {
            "default": (0.0, 0.0)  # Included in subscription
        }
    }
    
    def __new__(cls) -> "CostTracker":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._records: List[UsageRecord] = []
        self._pricing = self.DEFAULT_PRICING.copy()
        self._budget_limit: Optional[float] = None
        self._budget_alert_threshold: float = 0.8
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("CostTracker initialized")
    
    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> UsageRecord:
        """Record token usage."""
        usage = TokenUsage(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )
        
        cost = self._calculate_cost(provider, model, usage)
        
        record = UsageRecord(
            timestamp=datetime.utcnow(),
            provider=provider,
            model=model,
            usage=usage,
            cost=cost,
            task_id=task_id,
            agent_id=agent_id
        )
        
        with self._lock:
            self._records.append(record)
        
        # Check budget
        if self._budget_limit:
            self._check_budget()
        
        logger.debug(
            "Recorded usage: %s/%s - %d tokens, $%.4f",
            provider, model, usage.total_tokens, cost.total_cost
        )
        
        return record
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        usage: TokenUsage
    ) -> TokenCost:
        """Calculate cost for usage."""
        provider_pricing = self._pricing.get(provider.lower(), {})
        
        # Try exact model match, then default
        pricing = provider_pricing.get(model.lower())
        if not pricing:
            pricing = provider_pricing.get("default", (0.0, 0.0))
        
        input_price, output_price = pricing
        
        input_cost = (usage.prompt_tokens / 1000) * input_price
        output_cost = (usage.completion_tokens / 1000) * output_price
        
        return TokenCost(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost
        )
    
    def get_usage_report(self, period: str = "day") -> UsageReport:
        """Get aggregated usage report."""
        now = datetime.utcnow()
        
        if period == "hour":
            start = now - timedelta(hours=1)
        elif period == "day":
            start = now - timedelta(days=1)
        elif period == "week":
            start = now - timedelta(weeks=1)
        elif period == "month":
            start = now - timedelta(days=30)
        else:
            start = datetime.min
        
        records = [
            r for r in self._records
            if r.timestamp >= start
        ]
        
        # Aggregate
        by_provider: Dict[str, Dict[str, Any]] = {}
        by_model: Dict[str, Dict[str, Any]] = {}
        by_agent: Dict[str, Dict[str, Any]] = {}
        
        total_tokens = 0
        total_cost = 0.0
        
        for r in records:
            total_tokens += r.usage.total_tokens
            total_cost += r.cost.total_cost
            
            # By provider
            if r.provider not in by_provider:
                by_provider[r.provider] = {"requests": 0, "tokens": 0, "cost": 0.0}
            by_provider[r.provider]["requests"] += 1
            by_provider[r.provider]["tokens"] += r.usage.total_tokens
            by_provider[r.provider]["cost"] += r.cost.total_cost
            
            # By model
            if r.model not in by_model:
                by_model[r.model] = {"requests": 0, "tokens": 0, "cost": 0.0}
            by_model[r.model]["requests"] += 1
            by_model[r.model]["tokens"] += r.usage.total_tokens
            by_model[r.model]["cost"] += r.cost.total_cost
            
            # By agent
            if r.agent_id:
                if r.agent_id not in by_agent:
                    by_agent[r.agent_id] = {"requests": 0, "tokens": 0, "cost": 0.0}
                by_agent[r.agent_id]["requests"] += 1
                by_agent[r.agent_id]["tokens"] += r.usage.total_tokens
                by_agent[r.agent_id]["cost"] += r.cost.total_cost
        
        return UsageReport(
            period_start=start,
            period_end=now,
            total_requests=len(records),
            total_tokens=total_tokens,
            total_cost=total_cost,
            by_provider=by_provider,
            by_model=by_model,
            by_agent=by_agent
        )
    
    def get_estimated_cost(self) -> float:
        """Get total estimated cost to date."""
        return sum(r.cost.total_cost for r in self._records)
    
    def set_budget(self, limit: float, alert_threshold: float = 0.8) -> None:
        """Set budget limit with alert threshold."""
        self._budget_limit = limit
        self._budget_alert_threshold = alert_threshold
    
    def _check_budget(self) -> None:
        """Check if budget limits are approached/exceeded."""
        total = self.get_estimated_cost()
        
        if self._budget_limit:
            if total >= self._budget_limit:
                logger.warning("BUDGET EXCEEDED: $%.2f / $%.2f", total, self._budget_limit)
            elif total >= self._budget_limit * self._budget_alert_threshold:
                logger.warning(
                    "BUDGET ALERT: $%.2f / $%.2f (%.0f%%)",
                    total, self._budget_limit,
                    (total / self._budget_limit) * 100
                )
    
    def set_pricing(self, provider: str, model: str, input_per_1k: float, output_per_1k: float) -> None:
        """Set custom pricing for a model."""
        if provider.lower() not in self._pricing:
            self._pricing[provider.lower()] = {}
        self._pricing[provider.lower()][model.lower()] = (input_per_1k, output_per_1k)
    
    def clear_records(self) -> None:
        """Clear all usage records."""
        with self._lock:
            self._records.clear()
    
    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance."""
        with cls._lock:
            cls._instance = None
