"""
Budget Manager - Phase 8 Implementation.

Budget enforcement and alerting for LLM costs.

World-Class Standards:
- Real-time budget monitoring
- Multi-level alerts (warning, critical)
- User and org-level budgets
- Automatic enforcement
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import asyncio
import logging

from ..models import BudgetStatus, SUPPORTED_PROVIDERS
from ..config import AnalyticsConfig, default_config
from .cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class BudgetPeriod(Enum):
    """Budget period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Budget:
    """Budget configuration."""
    id: str
    user_id: str
    limit_usd: float
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    provider: Optional[str] = None  # None = all providers
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    enforce: bool = True  # Block requests when exceeded
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def get_period_start(self) -> datetime:
        """Get start of current budget period."""
        now = datetime.utcnow()
        
        if self.period == BudgetPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.period == BudgetPeriod.WEEKLY:
            days_since_monday = now.weekday()
            return (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:  # MONTHLY
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


@dataclass
class BudgetAlert:
    """Budget alert notification."""
    id: str
    budget_id: str
    user_id: str
    level: AlertLevel
    message: str
    current_usage: float
    limit: float
    percentage: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BudgetManager:
    """
    Budget management and enforcement.
    
    Features:
    - Per-user and per-provider budgets
    - Real-time monitoring
    - Multi-level alerts
    - Optional enforcement
    """
    
    def __init__(
        self,
        cost_tracker: CostTracker,
        config: Optional[AnalyticsConfig] = None,
    ) -> None:
        """Initialize budget manager."""
        self.cost_tracker = cost_tracker
        self.config = config or default_config
        
        # Budget storage
        self._budgets: Dict[str, Budget] = {}
        self._user_budgets: Dict[str, List[str]] = defaultdict(list)
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[BudgetAlert], None]] = []
        
        # Alert tracking (avoid duplicate alerts)
        self._sent_alerts: Dict[str, AlertLevel] = {}
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        logger.info("BudgetManager initialized")
    
    async def create_budget(self, budget: Budget) -> None:
        """Create or update a budget."""
        if budget.provider and budget.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {budget.provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        async with self._lock:
            self._budgets[budget.id] = budget
            if budget.id not in self._user_budgets[budget.user_id]:
                self._user_budgets[budget.user_id].append(budget.id)
        
        logger.info(
            "Created budget %s for user %s: $%.2f/%s",
            budget.id, budget.user_id, budget.limit_usd, budget.period.value
        )
    
    async def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get a budget by ID."""
        async with self._lock:
            return self._budgets.get(budget_id)
    
    async def get_user_budgets(self, user_id: str) -> List[Budget]:
        """Get all budgets for a user."""
        async with self._lock:
            budget_ids = self._user_budgets.get(user_id, [])
            return [self._budgets[bid] for bid in budget_ids if bid in self._budgets]
    
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget."""
        async with self._lock:
            budget = self._budgets.pop(budget_id, None)
            if budget:
                if budget_id in self._user_budgets[budget.user_id]:
                    self._user_budgets[budget.user_id].remove(budget_id)
                return True
            return False
    
    async def check_budget(
        self,
        user_id: str,
        provider: Optional[str] = None,
    ) -> BudgetStatus:
        """Check budget status for a user."""
        budgets = await self.get_user_budgets(user_id)
        
        if not budgets:
            return BudgetStatus(
                user_id=user_id,
                total_budget=0.0,
                used=0.0,
                remaining=0.0,
                percentage_used=0.0,
                status="no_budget",
                provider=provider,
            )
        
        # Find applicable budget
        applicable_budget = None
        for budget in budgets:
            if provider and budget.provider and budget.provider != provider:
                continue
            if not budget.provider or budget.provider == provider:
                applicable_budget = budget
                break
        
        if not applicable_budget:
            applicable_budget = budgets[0]  # Use first budget as fallback
        
        # Get current usage
        period_start = applicable_budget.get_period_start()
        summary = await self.cost_tracker.get_user_cost(
            user_id,
            start_time=period_start,
        )
        
        if provider and provider in summary.by_provider:
            used = summary.by_provider[provider]
        else:
            used = summary.total_cost
        
        remaining = max(0, applicable_budget.limit_usd - used)
        percentage = (used / applicable_budget.limit_usd * 100) if applicable_budget.limit_usd > 0 else 0
        
        # Determine status
        if percentage >= 100:
            status = "exceeded"
        elif percentage >= applicable_budget.critical_threshold * 100:
            status = "critical"
        elif percentage >= applicable_budget.warning_threshold * 100:
            status = "warning"
        else:
            status = "ok"
        
        budget_status = BudgetStatus(
            user_id=user_id,
            total_budget=applicable_budget.limit_usd,
            used=used,
            remaining=remaining,
            percentage_used=percentage,
            status=status,
            provider=provider,
        )
        
        # Check for alerts
        await self._check_alerts(applicable_budget, used, percentage)
        
        return budget_status
    
    async def _check_alerts(
        self,
        budget: Budget,
        current_usage: float,
        percentage: float,
    ) -> None:
        """Check and trigger budget alerts."""
        alert_key = f"{budget.id}:{budget.get_period_start().isoformat()}"
        
        level = None
        message = ""
        
        if percentage >= 100:
            level = AlertLevel.CRITICAL
            message = f"Budget exceeded! Usage: ${current_usage:.2f} / ${budget.limit_usd:.2f}"
        elif percentage >= budget.critical_threshold * 100:
            level = AlertLevel.CRITICAL
            message = f"Budget critical ({percentage:.1f}%): ${current_usage:.2f} / ${budget.limit_usd:.2f}"
        elif percentage >= budget.warning_threshold * 100:
            level = AlertLevel.WARNING
            message = f"Budget warning ({percentage:.1f}%): ${current_usage:.2f} / ${budget.limit_usd:.2f}"
        
        if level:
            # Check if we already sent this alert level
            existing_level = self._sent_alerts.get(alert_key)
            if existing_level and existing_level.value >= level.value:
                return
            
            alert = BudgetAlert(
                id=f"{alert_key}:{level.value}",
                budget_id=budget.id,
                user_id=budget.user_id,
                level=level,
                message=message,
                current_usage=current_usage,
                limit=budget.limit_usd,
                percentage=percentage,
            )
            
            # Record and dispatch alert
            self._sent_alerts[alert_key] = level
            await self._dispatch_alert(alert)
    
    async def _dispatch_alert(self, alert: BudgetAlert) -> None:
        """Dispatch alert to callbacks."""
        logger.warning(
            "Budget alert [%s] for %s: %s",
            alert.level.value, alert.user_id, alert.message
        )
        
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error("Alert callback error: %s", e)
    
    async def can_proceed(
        self,
        user_id: str,
        provider: str,
        estimated_cost: float = 0.0,
    ) -> tuple[bool, str]:
        """
        Check if a request can proceed within budget.
        
        Returns:
            Tuple of (allowed, reason)
        """
        if provider not in SUPPORTED_PROVIDERS:
            return False, f"Unknown provider: {provider}"
        
        budgets = await self.get_user_budgets(user_id)
        if not budgets:
            return True, "No budget configured"
        
        for budget in budgets:
            if not budget.enforce:
                continue
            
            if budget.provider and budget.provider != provider:
                continue
            
            status = await self.check_budget(user_id, provider)
            
            if status.status == "exceeded":
                return False, f"Budget exceeded: ${status.used:.2f} / ${status.total_budget:.2f}"
            
            if estimated_cost > 0 and status.remaining < estimated_cost:
                return False, f"Estimated cost ${estimated_cost:.4f} exceeds remaining budget ${status.remaining:.2f}"
        
        return True, "Within budget"
    
    def add_alert_callback(self, callback: Callable[[BudgetAlert], None]) -> None:
        """Add callback for budget alerts."""
        self._alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[BudgetAlert], None]) -> None:
        """Remove an alert callback."""
        if callback in self._alert_callbacks:
            self._alert_callbacks.remove(callback)
    
    async def reset_period_alerts(self) -> None:
        """Reset alert tracking for new period."""
        async with self._lock:
            self._sent_alerts.clear()
        logger.info("Budget alerts reset")
