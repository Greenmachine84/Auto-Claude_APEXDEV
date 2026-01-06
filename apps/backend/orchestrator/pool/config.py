"""Pool configuration.

Configuration for agent pool.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PoolConfig:
    """Configuration for agent pool.
    
    Attributes:
        min_agents: Minimum number of agents
        max_agents: Maximum number of agents
        acquire_timeout: Timeout for acquiring agent
        health_check_interval: Health check interval in seconds
    """
    
    # Pool size
    min_agents: int = 2
    max_agents: int = 10
    
    # Timeouts
    acquire_timeout: float = 30.0
    max_idle_time: float = 300.0  # 5 minutes
    
    # Health checks
    health_check_interval: float = 60.0
    health_check_timeout: float = 5.0
    
    # Scaling
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.2
    scale_cooldown: float = 60.0
    
    # Agent defaults
    default_max_concurrent: int = 1
    default_capabilities: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.min_agents < 0:
            raise ValueError("min_agents must be >= 0")
        if self.max_agents < self.min_agents:
            raise ValueError("max_agents must be >= min_agents")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PoolConfig":
        """Create config from dictionary."""
        return cls(
            min_agents=data.get("min_agents", 2),
            max_agents=data.get("max_agents", 10),
            acquire_timeout=data.get("acquire_timeout", 30.0),
            max_idle_time=data.get("max_idle_time", 300.0),
            health_check_interval=data.get("health_check_interval", 60.0),
            health_check_timeout=data.get("health_check_timeout", 5.0),
            scale_up_threshold=data.get("scale_up_threshold", 0.8),
            scale_down_threshold=data.get("scale_down_threshold", 0.2),
            scale_cooldown=data.get("scale_cooldown", 60.0),
            default_max_concurrent=data.get("default_max_concurrent", 1),
            default_capabilities=data.get("default_capabilities", {}),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "min_agents": self.min_agents,
            "max_agents": self.max_agents,
            "acquire_timeout": self.acquire_timeout,
            "max_idle_time": self.max_idle_time,
            "health_check_interval": self.health_check_interval,
            "health_check_timeout": self.health_check_timeout,
            "scale_up_threshold": self.scale_up_threshold,
            "scale_down_threshold": self.scale_down_threshold,
            "scale_cooldown": self.scale_cooldown,
            "default_max_concurrent": self.default_max_concurrent,
            "default_capabilities": self.default_capabilities,
        }
