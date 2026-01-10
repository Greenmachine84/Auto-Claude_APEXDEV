"""
Analytics Configuration - Phase 8 Implementation.

Configuration settings for the analytics module.

World-Class Standards:
- Environment-aware configuration
- Sensible defaults
- Type-safe settings
"""

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""

    # Collection settings
    batch_size: int = 100
    flush_interval_seconds: int = 5
    max_queue_size: int = 10000

    # Retention settings
    retention_days: int = 90
    downsample_after_days: int = 7

    # Performance settings
    enable_async: bool = True
    thread_pool_size: int = 4


@dataclass
class CostConfig:
    """Configuration for cost tracking."""

    # Budget settings
    default_monthly_limit: float = 100.0
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95

    # Pricing update settings
    auto_update_pricing: bool = True
    pricing_cache_hours: int = 24

    # Calculation settings
    precision_digits: int = 6


@dataclass
class DashboardConfig:
    """Configuration for dashboard API."""

    # API settings
    default_period_days: int = 30
    max_period_days: int = 365

    # Chart settings
    time_series_points: int = 100
    max_export_rows: int = 1000000

    # Caching settings
    cache_ttl_seconds: int = 60
    enable_caching: bool = True


@dataclass
class StorageConfig:
    """Configuration for analytics storage."""

    # Storage backend
    storage_type: str = "sqlite"  # sqlite, postgres, mongodb

    # SQLite settings
    sqlite_path: str = "analytics.db"
    sqlite_wal_mode: bool = True

    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30


@dataclass
class AnalyticsConfig:
    """
    Main analytics configuration.

    Aggregates all analytics-related settings.
    Supports environment variable overrides.
    """

    # Sub-configurations
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)

    # Global settings
    enabled: bool = True
    debug: bool = False
    log_level: str = "INFO"

    # Feature flags
    enable_cost_tracking: bool = True
    enable_provider_comparison: bool = True
    enable_budget_alerts: bool = True
    enable_recommendations: bool = True

    @classmethod
    def from_env(cls) -> "AnalyticsConfig":
        """
        Create configuration from environment variables.

        Environment variables:
        - ANALYTICS_ENABLED: Enable/disable analytics
        - ANALYTICS_DEBUG: Enable debug mode
        - ANALYTICS_RETENTION_DAYS: Metrics retention period
        - ANALYTICS_BUDGET_LIMIT: Default monthly budget
        - ANALYTICS_STORAGE_TYPE: Storage backend type
        - ANALYTICS_SQLITE_PATH: SQLite database path
        """
        config = cls()

        # Global settings
        if os.getenv("ANALYTICS_ENABLED"):
            config.enabled = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
        if os.getenv("ANALYTICS_DEBUG"):
            config.debug = os.getenv("ANALYTICS_DEBUG", "false").lower() == "true"
        if os.getenv("ANALYTICS_LOG_LEVEL"):
            config.log_level = os.getenv("ANALYTICS_LOG_LEVEL", "INFO")

        # Metrics settings
        if os.getenv("ANALYTICS_RETENTION_DAYS"):
            config.metrics.retention_days = int(
                os.getenv("ANALYTICS_RETENTION_DAYS", "90")
            )
        if os.getenv("ANALYTICS_BATCH_SIZE"):
            config.metrics.batch_size = int(os.getenv("ANALYTICS_BATCH_SIZE", "100"))

        # Cost settings
        if os.getenv("ANALYTICS_BUDGET_LIMIT"):
            config.cost.default_monthly_limit = float(
                os.getenv("ANALYTICS_BUDGET_LIMIT", "100.0")
            )

        # Storage settings
        if os.getenv("ANALYTICS_STORAGE_TYPE"):
            config.storage.storage_type = os.getenv("ANALYTICS_STORAGE_TYPE", "sqlite")
        if os.getenv("ANALYTICS_SQLITE_PATH"):
            config.storage.sqlite_path = os.getenv(
                "ANALYTICS_SQLITE_PATH", "analytics.db"
            )

        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enabled": self.enabled,
            "debug": self.debug,
            "log_level": self.log_level,
            "metrics": {
                "batch_size": self.metrics.batch_size,
                "flush_interval_seconds": self.metrics.flush_interval_seconds,
                "retention_days": self.metrics.retention_days,
            },
            "cost": {
                "default_monthly_limit": self.cost.default_monthly_limit,
                "warning_threshold": self.cost.warning_threshold,
            },
            "dashboard": {
                "default_period_days": self.dashboard.default_period_days,
                "cache_ttl_seconds": self.dashboard.cache_ttl_seconds,
            },
            "storage": {
                "storage_type": self.storage.storage_type,
                "sqlite_path": self.storage.sqlite_path,
            },
        }


# Default configuration instance
default_config = AnalyticsConfig.from_env()
