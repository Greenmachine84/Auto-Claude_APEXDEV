"""
Quota Manager - Phase 9 Implementation.

Provider-aware quota management with cost tracking.

World-Class Standards:
- Per-provider quotas
- Cost tracking
- Usage alerts
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import logging

from ..models import Quota, QuotaUsage, SUPPORTED_PROVIDERS
from ..config import PROVIDER_QUOTAS


logger = logging.getLogger(__name__)


class QuotaPeriod(Enum):
    """Quota period types."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class QuotaAlert:
    """Quota alert notification."""
    provider: str
    user_id: str
    usage_percentage: float
    threshold: float
    current_usage: float
    limit: float
    timestamp: datetime


@dataclass
class ProviderQuota:
    """
    Provider-specific quota configuration.
    
    Wraps the config data into a structured object.
    """
    monthly_cost_limit: float
    daily_cost_limit: Optional[float] = None


class QuotaManager:
    """
    Provider-aware quota manager.
    
    Tracks usage and enforces quotas with:
    - Per-provider cost limits
    - Usage tracking
    - Alert thresholds
    """
    
    def __init__(self) -> None:
        self._usage: Dict[str, Dict[str, QuotaUsage]] = {}
        self._quotas: Dict[str, Optional[ProviderQuota]] = {}
        self._lock = threading.Lock()
        self._alert_callbacks: List[Callable[[QuotaAlert], None]] = []
        self._alert_thresholds = [0.75, 0.90, 1.0]
        self._alerted: Dict[str, set] = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize quotas for all providers."""
        for provider in SUPPORTED_PROVIDERS:
            self._usage[provider] = {}
            # Get config dict for this provider
            config = PROVIDER_QUOTAS.get(provider, {})
            monthly = config.get("monthly_cost_usd")
            daily = config.get("daily_cost_usd")
            # Create ProviderQuota object from config if monthly limit exists
            if monthly is not None:
                self._quotas[provider] = ProviderQuota(
                    monthly_cost_limit=monthly,
                    daily_cost_limit=daily,
                )
            else:
                self._quotas[provider] = None
            self._alerted[provider] = set()
        logger.info(f"Initialized quota manager for {len(SUPPORTED_PROVIDERS)} providers")
    
    def _get_usage(self, provider: str, user_id: str) -> QuotaUsage:
        """Get or create usage tracker for user."""
        with self._lock:
            if user_id not in self._usage.get(provider, {}):
                if provider not in self._usage:
                    self._usage[provider] = {}
                
                quota = self._quotas.get(provider)
                limit = quota.monthly_cost_limit if quota else float("inf")
                self._usage[provider][user_id] = QuotaUsage(
                    quota_key=f"{provider}:{user_id}",
                    period_start=datetime.utcnow().replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    ),
                    period_end=self._get_period_end(datetime.utcnow()),
                    current_usage=0.0,
                    limit=limit,
                    remaining=limit,
                    usage_percent=0.0,
                    provider=provider,
                )
        
        return self._usage[provider][user_id]
    
    def _get_period_end(self, start: datetime) -> datetime:
        """Get end of current period (monthly)."""
        if start.month == 12:
            return start.replace(year=start.year + 1, month=1, day=1)
        return start.replace(month=start.month + 1, day=1)
    
    def check_quota(
        self,
        provider: str,
        user_id: str,
        estimated_cost: float = 0.0
    ) -> tuple[bool, QuotaUsage]:
        """
        Check if request is within quota.
        
        Args:
            provider: Provider identifier
            user_id: User identifier
            estimated_cost: Estimated cost of request
            
        Returns:
            Tuple of (allowed, current_usage)
        """
        if provider not in SUPPORTED_PROVIDERS:
            dummy = QuotaUsage(
                quota_key=f"{provider}:{user_id}",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                current_usage=0,
                limit=0,
                remaining=0,
                usage_percent=0.0,
                provider=provider,
            )
            return False, dummy
        
        usage = self._get_usage(provider, user_id)
        
        # Check if period has reset
        if datetime.utcnow() >= usage.period_end:
            self._reset_period(provider, user_id)
            usage = self._get_usage(provider, user_id)
        
        # Check quota
        if (usage.current_usage + estimated_cost) > usage.limit:
            logger.warning(
                f"Quota exceeded for {provider}/{user_id}: "
                f"{usage.current_usage + estimated_cost} > {usage.limit}"
            )
            return False, usage
        
        return True, usage
    
    def record_usage(
        self,
        provider: str,
        user_id: str,
        cost: float,
        tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QuotaUsage:
        """Record usage and update quota."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        usage = self._get_usage(provider, user_id)
        
        with self._lock:
            usage.current_usage += cost
            usage.remaining = max(0, usage.limit - usage.current_usage)
            if usage.limit > 0:
                usage.usage_percent = (usage.current_usage / usage.limit) * 100
        
        # Check for alerts
        self._check_alerts(provider, user_id, usage)
        
        logger.debug(
            f"Recorded usage for {provider}/{user_id}: "
            f"${cost:.4f} (total: ${usage.current_usage:.2f})"
        )
        
        return usage
    
    def _check_alerts(self, provider: str, user_id: str, usage: QuotaUsage) -> None:
        """Check and trigger quota alerts."""
        if usage.limit == 0:
            return
        
        percentage = usage.current_usage / usage.limit
        key = f"{provider}:{user_id}"
        
        for threshold in self._alert_thresholds:
            if percentage >= threshold:
                alert_key = f"{key}:{threshold}"
                if alert_key not in self._alerted.get(provider, set()):
                    self._alerted[provider].add(alert_key)
                    alert = QuotaAlert(
                        provider=provider,
                        user_id=user_id,
                        usage_percentage=percentage * 100,
                        threshold=threshold * 100,
                        current_usage=usage.current_usage,
                        limit=usage.limit,
                        timestamp=datetime.utcnow(),
                    )
                    self._notify_alert(alert)
    
    def _notify_alert(self, alert: QuotaAlert) -> None:
        """Notify registered callbacks of alert."""
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(
            f"Quota alert: {alert.provider}/{alert.user_id} "
            f"at {alert.usage_percentage:.1f}% (threshold: {alert.threshold}%)"
        )
    
    def add_alert_callback(self, callback: Callable[[QuotaAlert], None]) -> None:
        """Register callback for quota alerts."""
        self._alert_callbacks.append(callback)
    
    def _reset_period(self, provider: str, user_id: str) -> None:
        """Reset usage for new period."""
        with self._lock:
            quota = self._quotas.get(provider)
            now = datetime.utcnow()
            limit = quota.monthly_cost_limit if quota else float("inf")
            
            self._usage[provider][user_id] = QuotaUsage(
                quota_key=f"{provider}:{user_id}",
                period_start=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                period_end=self._get_period_end(now),
                current_usage=0.0,
                limit=limit,
                remaining=limit,
                usage_percent=0.0,
                provider=provider,
            )
            
            # Clear alerts for new period
            key_prefix = f"{provider}:{user_id}"
            self._alerted[provider] = {
                k for k in self._alerted.get(provider, set())
                if not k.startswith(key_prefix)
            }
        
        logger.info(f"Reset quota period for {provider}/{user_id}")
    
    def get_usage(self, provider: str, user_id: str) -> QuotaUsage:
        """Get current usage for user."""
        return self._get_usage(provider, user_id)
    
    def get_remaining(self, provider: str, user_id: str) -> float:
        """Get remaining quota for user."""
        usage = self._get_usage(provider, user_id)
        return max(0, usage.limit - usage.current_usage)
    
    def set_quota(self, provider: str, quota: ProviderQuota) -> None:
        """Set custom quota for provider."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        self._quotas[provider] = quota
    
    def get_all_usage(self) -> Dict[str, Dict[str, QuotaUsage]]:
        """Get usage for all providers and users."""
        return {
            provider: dict(users)
            for provider, users in self._usage.items()
        }
    
    def get_summary(self, provider: str) -> Dict[str, Any]:
        """Get usage summary for provider."""
        if provider not in self._usage:
            return {"total_usage": 0, "user_count": 0}
        
        users = self._usage[provider]
        total = sum(u.current_usage for u in users.values())
        
        return {
            "provider": provider,
            "total_usage": total,
            "user_count": len(users),
            "quota": self._quotas.get(provider),
        }
