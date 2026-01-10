"""Orchestrator configuration.

Defines configuration for the orchestrator system.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator.

    Attributes:
        worker_count: Number of worker tasks
        max_queue_size: Maximum task queue size
        default_timeout: Default task timeout in seconds
        retry_enabled: Enable automatic retries
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries in seconds
        enable_metrics: Enable metrics collection
        enable_persistence: Enable task persistence
    """

    # Worker configuration
    worker_count: int = 4
    max_queue_size: int = 1000

    # Timeout configuration
    default_timeout: float = 300.0  # 5 minutes
    task_timeout: float = 600.0  # 10 minutes

    # Retry configuration
    retry_enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # Feature flags
    enable_metrics: bool = True
    enable_persistence: bool = False
    enable_logging: bool = True

    # Resource limits
    max_concurrent_tasks: int = 10
    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0

    # Custom settings
    custom: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.worker_count < 1:
            raise ValueError("worker_count must be >= 1")
        if self.max_queue_size < 1:
            raise ValueError("max_queue_size must be >= 1")
        if self.default_timeout <= 0:
            raise ValueError("default_timeout must be > 0")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrchestratorConfig":
        """Create config from dictionary."""
        return cls(
            worker_count=data.get("worker_count", 4),
            max_queue_size=data.get("max_queue_size", 1000),
            default_timeout=data.get("default_timeout", 300.0),
            task_timeout=data.get("task_timeout", 600.0),
            retry_enabled=data.get("retry_enabled", True),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 1.0),
            retry_backoff=data.get("retry_backoff", 2.0),
            enable_metrics=data.get("enable_metrics", True),
            enable_persistence=data.get("enable_persistence", False),
            enable_logging=data.get("enable_logging", True),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 10),
            max_memory_mb=data.get("max_memory_mb", 1024),
            max_cpu_percent=data.get("max_cpu_percent", 80.0),
            custom=data.get("custom", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "worker_count": self.worker_count,
            "max_queue_size": self.max_queue_size,
            "default_timeout": self.default_timeout,
            "task_timeout": self.task_timeout,
            "retry_enabled": self.retry_enabled,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "retry_backoff": self.retry_backoff,
            "enable_metrics": self.enable_metrics,
            "enable_persistence": self.enable_persistence,
            "enable_logging": self.enable_logging,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "custom": self.custom,
        }

    def with_overrides(self, **kwargs: Any) -> "OrchestratorConfig":
        """Create new config with overrides."""
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data)
