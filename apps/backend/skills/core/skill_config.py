"""Skill configuration and validation.

Provides:
- Skill-level configuration
- Configuration validation
- Environment-based overrides
- Resource limits

Example:
    config = SkillConfig(
        name="code_generation",
        enabled=True,
        max_tokens=4096,
        timeout_seconds=300,
    )
    
    if config.is_enabled:
        skill = registry.get(config.name)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """Resource limits for skill execution."""
    max_tokens: int = 4096
    max_memory_mb: int = 512
    max_execution_time_seconds: int = 300
    max_retries: int = 3
    max_file_size_kb: int = 1024
    
    def validate(self) -> bool:
        """Validate limits are reasonable."""
        return (
            self.max_tokens > 0 and
            self.max_memory_mb > 0 and
            self.max_execution_time_seconds > 0 and
            self.max_retries >= 0 and
            self.max_file_size_kb > 0
        )


@dataclass
class SkillConfig:
    """Configuration for a skill.
    
    Provides configuration settings for skill execution including
    resource limits, feature flags, and provider settings.
    """
    name: str
    enabled: bool = True
    timeout_seconds: int = 300
    max_tokens: int = 4096
    temperature: float = 0.7
    preferred_provider: Optional[str] = None
    fallback_providers: List[str] = field(default_factory=list)
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    required_tools: Set[str] = field(default_factory=set)
    allowed_file_patterns: List[str] = field(default_factory=lambda: ["*"])
    denied_file_patterns: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_enabled(self) -> bool:
        """Check if skill is enabled (considers env override)."""
        env_key = f"SKILL_{self.name.upper()}_ENABLED"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes")
        return self.enabled
    
    @property
    def effective_timeout(self) -> int:
        """Get effective timeout (considers env override)."""
        env_key = f"SKILL_{self.name.upper()}_TIMEOUT"
        env_value = os.getenv(env_key)
        if env_value is not None:
            try:
                return int(env_value)
            except ValueError:
                pass
        return self.timeout_seconds
    
    def get_provider(self) -> Optional[str]:
        """Get the preferred provider (considers env override)."""
        env_key = f"SKILL_{self.name.upper()}_PROVIDER"
        env_value = os.getenv(env_key)
        if env_value:
            return env_value
        return self.preferred_provider
    
    def validate(self) -> List[str]:
        """Validate configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors: List[str] = []
        
        if not self.name:
            errors.append("Skill name is required")
        
        if self.timeout_seconds <= 0:
            errors.append("Timeout must be positive")
        
        if self.max_tokens <= 0:
            errors.append("Max tokens must be positive")
        
        if not 0.0 <= self.temperature <= 2.0:
            errors.append("Temperature must be between 0.0 and 2.0")
        
        if not self.resource_limits.validate():
            errors.append("Invalid resource limits")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "is_enabled": self.is_enabled,
            "timeout_seconds": self.timeout_seconds,
            "effective_timeout": self.effective_timeout,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "preferred_provider": self.preferred_provider,
            "fallback_providers": self.fallback_providers,
            "resource_limits": {
                "max_tokens": self.resource_limits.max_tokens,
                "max_memory_mb": self.resource_limits.max_memory_mb,
                "max_execution_time_seconds": self.resource_limits.max_execution_time_seconds,
                "max_retries": self.resource_limits.max_retries,
                "max_file_size_kb": self.resource_limits.max_file_size_kb,
            },
            "required_tools": list(self.required_tools),
            "allowed_file_patterns": self.allowed_file_patterns,
            "denied_file_patterns": self.denied_file_patterns,
            "custom_settings": self.custom_settings,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillConfig":
        """Create from dictionary."""
        resource_data = data.get("resource_limits", {})
        resource_limits = ResourceLimits(
            max_tokens=resource_data.get("max_tokens", 4096),
            max_memory_mb=resource_data.get("max_memory_mb", 512),
            max_execution_time_seconds=resource_data.get("max_execution_time_seconds", 300),
            max_retries=resource_data.get("max_retries", 3),
            max_file_size_kb=resource_data.get("max_file_size_kb", 1024),
        )
        
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            timeout_seconds=data.get("timeout_seconds", 300),
            max_tokens=data.get("max_tokens", 4096),
            temperature=data.get("temperature", 0.7),
            preferred_provider=data.get("preferred_provider"),
            fallback_providers=data.get("fallback_providers", []),
            resource_limits=resource_limits,
            required_tools=set(data.get("required_tools", [])),
            allowed_file_patterns=data.get("allowed_file_patterns", ["*"]),
            denied_file_patterns=data.get("denied_file_patterns", []),
            custom_settings=data.get("custom_settings", {}),
        )


class SkillConfigManager:
    """Manage configurations for multiple skills."""
    
    def __init__(self) -> None:
        """Initialize the config manager."""
        self._configs: Dict[str, SkillConfig] = {}
    
    def register(self, config: SkillConfig) -> None:
        """Register a skill configuration."""
        if config.is_valid():
            self._configs[config.name] = config
            logger.debug(f"Registered config for skill: {config.name}")
        else:
            errors = config.validate()
            logger.error(f"Invalid config for {config.name}: {errors}")
    
    def get(self, name: str) -> Optional[SkillConfig]:
        """Get configuration for a skill."""
        return self._configs.get(name)
    
    def get_or_default(self, name: str) -> SkillConfig:
        """Get configuration or create default."""
        if name not in self._configs:
            self._configs[name] = SkillConfig(name=name)
        return self._configs[name]
    
    def list_enabled(self) -> List[str]:
        """List enabled skill names."""
        return [name for name, cfg in self._configs.items() if cfg.is_enabled]
    
    def list_disabled(self) -> List[str]:
        """List disabled skill names."""
        return [name for name, cfg in self._configs.items() if not cfg.is_enabled]
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Export all configs as dictionary."""
        return {name: cfg.to_dict() for name, cfg in self._configs.items()}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> "SkillConfigManager":
        """Create from dictionary."""
        manager = cls()
        for name, cfg_data in data.items():
            cfg_data["name"] = name
            config = SkillConfig.from_dict(cfg_data)
            manager.register(config)
        return manager
