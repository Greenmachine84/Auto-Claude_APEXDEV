"""
Time Series Manager - Phase 8 Implementation.

Manages time-bucketed metrics data for charts and trend analysis.

World-Class Standards:
- Efficient time-bucketed storage
- Automatic downsampling
- Rolling averages
- High-performance queries
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from ..models import TimeSeriesPoint, SUPPORTED_PROVIDERS

logger = logging.getLogger(__name__)


@dataclass
class TimeBucket:
    """A single time bucket for aggregation."""
    timestamp: datetime
    count: int = 0
    sum_value: float = 0.0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    def add(self, value: float) -> None:
        """Add a value to the bucket."""
        self.count += 1
        self.sum_value += value
        
        if self.min_value is None or value < self.min_value:
            self.min_value = value
        if self.max_value is None or value > self.max_value:
            self.max_value = value
    
    @property
    def avg(self) -> float:
        """Calculate average value."""
        return self.sum_value / self.count if self.count > 0 else 0.0
    
    def to_point(self) -> TimeSeriesPoint:
        """Convert to TimeSeriesPoint."""
        return TimeSeriesPoint(
            timestamp=self.timestamp.isoformat() + "Z",
            value=self.avg,
            metadata={
                "count": self.count,
                "sum": self.sum_value,
                "min": self.min_value,
                "max": self.max_value,
            },
        )


class TimeSeriesManager:
    """
    Manages time series data for analytics.
    
    Features:
    - Hour/day/week granularity
    - Automatic bucket creation
    - Efficient aggregation
    - Provider-aware series
    
    LLM-Agnostic: Tracks all 8 providers separately.
    """
    
    def __init__(self) -> None:
        """Initialize the time series manager."""
        # Series storage: {series_name: {bucket_key: TimeBucket}}
        self._series: Dict[str, Dict[str, TimeBucket]] = defaultdict(dict)
        
        # Provider-specific series for all 8 providers
        for provider in SUPPORTED_PROVIDERS:
            self._series[f"requests_{provider}"] = {}
            self._series[f"tokens_{provider}"] = {}
            self._series[f"cost_{provider}"] = {}
            self._series[f"latency_{provider}"] = {}
        
        logger.info("TimeSeriesManager initialized with %d providers", len(SUPPORTED_PROVIDERS))
    
    def record(
        self,
        series_name: str,
        value: float,
        timestamp: Optional[datetime] = None,
        granularity: str = "hour",
    ) -> None:
        """
        Record a value in a time series.
        
        Args:
            series_name: Name of the series
            value: Value to record
            timestamp: Time of the value (default: now)
            granularity: Bucket size (minute, hour, day)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        bucket_key = self._make_bucket_key(timestamp, granularity)
        bucket_ts = self._bucket_timestamp(timestamp, granularity)
        
        if bucket_key not in self._series[series_name]:
            self._series[series_name][bucket_key] = TimeBucket(timestamp=bucket_ts)
        
        self._series[series_name][bucket_key].add(value)
    
    def record_provider_metric(
        self,
        provider: str,
        metric_type: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Record a provider-specific metric.
        
        Args:
            provider: One of 8 supported providers
            metric_type: Type of metric (requests, tokens, cost, latency)
            value: Value to record
            timestamp: Time of the value
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        series_name = f"{metric_type}_{provider}"
        self.record(series_name, value, timestamp)
    
    def _make_bucket_key(self, timestamp: datetime, granularity: str) -> str:
        """Create a bucket key from timestamp."""
        if granularity == "minute":
            return timestamp.strftime("%Y-%m-%d-%H-%M")
        elif granularity == "hour":
            return timestamp.strftime("%Y-%m-%d-%H")
        elif granularity == "day":
            return timestamp.strftime("%Y-%m-%d")
        elif granularity == "week":
            week_start = timestamp - timedelta(days=timestamp.weekday())
            return week_start.strftime("%Y-%m-%d")
        else:
            raise ValueError(f"Unknown granularity: {granularity}")
    
    def _bucket_timestamp(self, timestamp: datetime, granularity: str) -> datetime:
        """Get the start timestamp for a bucket."""
        if granularity == "minute":
            return timestamp.replace(second=0, microsecond=0)
        elif granularity == "hour":
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif granularity == "day":
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == "week":
            week_start = timestamp - timedelta(days=timestamp.weekday())
            return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError(f"Unknown granularity: {granularity}")
    
    def get_series(
        self,
        series_name: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        granularity: str = "hour",
    ) -> List[TimeSeriesPoint]:
        """
        Get time series data.
        
        Args:
            series_name: Name of the series
            start: Start time (default: 24 hours ago)
            end: End time (default: now)
            granularity: Bucket size
            
        Returns:
            List of time series points
        """
        if end is None:
            end = datetime.utcnow()
        if start is None:
            start = end - timedelta(hours=24)
        
        series = self._series.get(series_name, {})
        points: List[TimeSeriesPoint] = []
        
        for bucket_key, bucket in sorted(series.items()):
            if start <= bucket.timestamp <= end:
                points.append(bucket.to_point())
        
        return points
    
    def get_provider_series(
        self,
        provider: str,
        metric_type: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[TimeSeriesPoint]:
        """
        Get time series for a specific provider.
        
        Args:
            provider: One of 8 supported providers
            metric_type: Type of metric
            start: Start time
            end: End time
            
        Returns:
            List of time series points
        """
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        series_name = f"{metric_type}_{provider}"
        return self.get_series(series_name, start, end)
    
    def get_all_providers_series(
        self,
        metric_type: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict[str, List[TimeSeriesPoint]]:
        """
        Get time series for all 8 providers.
        
        Args:
            metric_type: Type of metric
            start: Start time
            end: End time
            
        Returns:
            Dictionary mapping provider to time series
        """
        return {
            provider: self.get_provider_series(provider, metric_type, start, end)
            for provider in SUPPORTED_PROVIDERS
        }
    
    def downsample(
        self,
        series_name: str,
        from_granularity: str,
        to_granularity: str,
    ) -> None:
        """
        Downsample a series to larger buckets.
        
        Used for long-term data retention.
        
        Args:
            series_name: Name of the series
            from_granularity: Current granularity
            to_granularity: Target granularity
        """
        series = self._series.get(series_name, {})
        if not series:
            return
        
        # Group buckets by new granularity
        new_buckets: Dict[str, TimeBucket] = {}
        
        for bucket in series.values():
            new_key = self._make_bucket_key(bucket.timestamp, to_granularity)
            new_ts = self._bucket_timestamp(bucket.timestamp, to_granularity)
            
            if new_key not in new_buckets:
                new_buckets[new_key] = TimeBucket(timestamp=new_ts)
            
            # Aggregate values
            new_buckets[new_key].count += bucket.count
            new_buckets[new_key].sum_value += bucket.sum_value
            
            if bucket.min_value is not None:
                if new_buckets[new_key].min_value is None:
                    new_buckets[new_key].min_value = bucket.min_value
                else:
                    new_buckets[new_key].min_value = min(
                        new_buckets[new_key].min_value, bucket.min_value
                    )
            
            if bucket.max_value is not None:
                if new_buckets[new_key].max_value is None:
                    new_buckets[new_key].max_value = bucket.max_value
                else:
                    new_buckets[new_key].max_value = max(
                        new_buckets[new_key].max_value, bucket.max_value
                    )
        
        self._series[series_name] = new_buckets
    
    def cleanup_old_data(self, max_age_days: int = 90) -> int:
        """
        Remove data older than max_age_days.
        
        Args:
            max_age_days: Maximum age of data to keep
            
        Returns:
            Number of buckets removed
        """
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        removed = 0
        
        for series_name in list(self._series.keys()):
            series = self._series[series_name]
            old_keys = [
                key for key, bucket in series.items()
                if bucket.timestamp < cutoff
            ]
            for key in old_keys:
                del series[key]
                removed += 1
        
        if removed > 0:
            logger.info("Cleaned up %d old time series buckets", removed)
        
        return removed
    
    def get_rolling_average(
        self,
        series_name: str,
        window_hours: int = 24,
    ) -> float:
        """
        Calculate rolling average for a series.
        
        Args:
            series_name: Name of the series
            window_hours: Window size in hours
            
        Returns:
            Rolling average value
        """
        end = datetime.utcnow()
        start = end - timedelta(hours=window_hours)
        
        points = self.get_series(series_name, start, end)
        
        if not points:
            return 0.0
        
        return sum(p.value for p in points) / len(points)
