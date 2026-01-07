"""
Cost Tracker - Phase 8 Implementation.

Real-time cost tracking for all LLM API calls.

World-Class Standards:
- <1ms cost calculation latency
- <0.1% error rate
- Provider-agnostic design
- Batch processing support
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import asyncio
import logging
import uuid

from ..models import CostRecord, SUPPORTED_PROVIDERS
from ..config import AnalyticsConfig, default_config
from .pricing import PricingEngine

logger = logging.getLogger(__name__)


@dataclass
class CostSummary:
    """Summary of costs for a period."""
    user_id: str
    total_cost: float
    by_provider: Dict[str, float]
    by_model: Dict[str, float]
    total_prompt_tokens: int
    total_completion_tokens: int
    request_count: int
    period_start: str
    period_end: str
    
    @property
    def average_cost_per_request(self) -> float:
        """Calculate average cost per request."""
        if self.request_count == 0:
            return 0.0
        return self.total_cost / self.request_count


class CostTracker:
    """
    Real-time cost tracking for LLM API calls.
    
    Features:
    - Multi-provider cost calculation
    - Real-time aggregation
    - Budget integration
    - Webhook callbacks
    """
    
    def __init__(
        self,
        config: Optional[AnalyticsConfig] = None,
        pricing_engine: Optional[PricingEngine] = None,
    ) -> None:
        """Initialize cost tracker."""
        self.config = config or default_config
        self.pricing = pricing_engine or PricingEngine()
        
        # In-memory cost tracking
        self._records: List[CostRecord] = []
        self._by_user: Dict[str, List[CostRecord]] = defaultdict(list)
        self._by_provider: Dict[str, float] = defaultdict(float)
        self._total_cost: float = 0.0
        
        # Callbacks for cost events
        self._callbacks: List[Callable[[CostRecord], None]] = []
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        logger.info("CostTracker initialized")
    
    async def track_request(
        self,
        user_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CostRecord:
        """
        Track cost for an LLM request.
        
        Args:
            user_id: User identifier
            provider: LLM provider (one of 8 supported)
            model: Model identifier
            prompt_tokens: Input token count
            completion_tokens: Output token count
            agent_id: Optional agent identifier
            task_id: Optional task identifier
            metadata: Optional additional data
            
        Returns:
            CostRecord with calculated cost
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        # Calculate cost
        cost = self.pricing.calculate_cost(
            provider, model, prompt_tokens, completion_tokens
        )
        
        # Create record
        record = CostRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent_id,
            task_id=task_id,
        )
        
        # Store record
        async with self._lock:
            self._records.append(record)
            self._by_user[user_id].append(record)
            self._by_provider[provider] += cost
            self._total_cost += cost
        
        # Trigger callbacks
        for callback in self._callbacks:
            try:
                callback(record)
            except Exception as e:
                logger.error("Callback error: %s", e)
        
        logger.debug(
            "Tracked cost: %s/%s - $%.6f (%d+%d tokens)",
            provider, model, cost, prompt_tokens, completion_tokens
        )
        
        return record
    
    async def get_user_cost(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> CostSummary:
        """Get cost summary for a user."""
        async with self._lock:
            records = self._by_user.get(user_id, [])
        
        # Filter by time
        if start_time or end_time:
            filtered = []
            for r in records:
                record_time = datetime.fromisoformat(r.timestamp)
                if start_time and record_time < start_time:
                    continue
                if end_time and record_time > end_time:
                    continue
                filtered.append(r)
            records = filtered
        
        # Aggregate
        total_cost = 0.0
        by_provider: Dict[str, float] = defaultdict(float)
        by_model: Dict[str, float] = defaultdict(float)
        total_prompt = 0
        total_completion = 0
        
        for r in records:
            total_cost += r.cost_usd
            by_provider[r.provider] += r.cost_usd
            by_model[f"{r.provider}/{r.model}"] += r.cost_usd
            total_prompt += r.prompt_tokens
            total_completion += r.completion_tokens
        
        return CostSummary(
            user_id=user_id,
            total_cost=total_cost,
            by_provider=dict(by_provider),
            by_model=dict(by_model),
            total_prompt_tokens=total_prompt,
            total_completion_tokens=total_completion,
            request_count=len(records),
            period_start=start_time.isoformat() if start_time else "",
            period_end=end_time.isoformat() if end_time else "",
        )
    
    async def get_provider_cost(self, provider: str) -> float:
        """Get total cost for a provider."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        async with self._lock:
            return self._by_provider.get(provider, 0.0)
    
    async def get_total_cost(self) -> float:
        """Get total tracked cost."""
        async with self._lock:
            return self._total_cost
    
    async def get_provider_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by provider."""
        async with self._lock:
            return dict(self._by_provider)
    
    async def get_records(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        limit: int = 100,
    ) -> List[CostRecord]:
        """Get cost records with optional filters."""
        async with self._lock:
            if user_id:
                records = self._by_user.get(user_id, [])
            else:
                records = self._records.copy()
        
        if provider:
            if provider not in SUPPORTED_PROVIDERS:
                raise ValueError(
                    f"Unknown provider: {provider}. "
                    f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
                )
            records = [r for r in records if r.provider == provider]
        
        return records[-limit:]
    
    def add_callback(self, callback: Callable[[CostRecord], None]) -> None:
        """Add callback for cost events."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[CostRecord], None]) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def reset(self) -> None:
        """Reset all tracked costs."""
        async with self._lock:
            self._records.clear()
            self._by_user.clear()
            self._by_provider.clear()
            self._total_cost = 0.0
        
        logger.info("Cost tracker reset")
    
    async def export_records(self) -> List[Dict[str, Any]]:
        """Export all records as dictionaries."""
        async with self._lock:
            return [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "provider": r.provider,
                    "model": r.model,
                    "prompt_tokens": r.prompt_tokens,
                    "completion_tokens": r.completion_tokens,
                    "cost_usd": r.cost_usd,
                    "timestamp": r.timestamp,
                    "agent_id": r.agent_id,
                    "task_id": r.task_id,
                }
                for r in self._records
            ]
