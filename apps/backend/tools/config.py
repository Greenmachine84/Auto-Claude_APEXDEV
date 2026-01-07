"""
Tools Configuration - Phase 8 Implementation.

Configuration for the tool framework.

World-Class Standards:
- Environment-based config
- Secure defaults
- Validation support
- Hot reload capability
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutorConfig:
    """Configuration for tool executor."""
    default_timeout_seconds: float = 30.0
    max_timeout_seconds: float = 300.0
    max_concurrent_executions: int = 10
    enable_sandboxing: bool = True
    sandbox_type: str = "process"  # process, container, none
    max_output_size_bytes: int = 1024 * 1024  # 1MB
    enable_caching: bool = True
    cache_ttl_seconds: int = 300


@dataclass
class RegistryConfig:
    """Configuration for tool registry."""
    auto_discover: bool = True
    discovery_paths: List[str] = field(default_factory=lambda: ["builtin"])
    enable_custom_tools: bool = True
    custom_tools_path: str = "custom_tools"
    validate_on_register: bool = True


@dataclass
class SecurityConfig:
    """Security configuration for tools."""
    allow_shell_execution: bool = False
    allow_file_write: bool = True
    allow_network_access: bool = True
    allowed_file_extensions: List[str] = field(default_factory=lambda: [
        ".txt", ".md", ".json", ".yaml", ".yml", ".py", ".js", ".ts",
        ".html", ".css", ".csv", ".xml", ".log"
    ])
    blocked_commands: List[str] = field(default_factory=lambda: [
        "rm -rf", "format", "mkfs", "dd", "shutdown", "reboot",
        ":(){", "fork bomb"
    ])
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB
    allowed_domains: List[str] = field(default_factory=list)  # Empty = all allowed
    blocked_domains: List[str] = field(default_factory=lambda: [
        "localhost", "127.0.0.1", "0.0.0.0", "internal"
    ])


@dataclass
class BuiltinToolsConfig:
    """Configuration for builtin tools."""
    enable_file_tools: bool = True
    enable_web_tools: bool = True
    enable_git_tools: bool = True
    enable_search_tools: bool = True
    enable_shell_tools: bool = False  # Disabled by default
    
    # File tools settings
    file_read_max_size: int = 5 * 1024 * 1024  # 5MB
    file_list_max_items: int = 1000
    
    # Web tools settings
    web_request_timeout: float = 30.0
    web_max_response_size: int = 10 * 1024 * 1024  # 10MB
    web_user_agent: str = "Auto-Claude/1.0"
    
    # Git tools settings
    git_max_diff_size: int = 1024 * 1024  # 1MB
    git_max_commits: int = 100
    
    # Search tools settings
    search_max_results: int = 50
    search_context_lines: int = 3


@dataclass
class ToolsConfig:
    """Main tools configuration."""
    executor: ExecutorConfig = field(default_factory=ExecutorConfig)
    registry: RegistryConfig = field(default_factory=RegistryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    builtin: BuiltinToolsConfig = field(default_factory=BuiltinToolsConfig)
    
    # Metrics integration
    enable_metrics: bool = True
    metrics_sample_rate: float = 1.0
    
    @classmethod
    def from_env(cls) -> "ToolsConfig":
        """Create configuration from environment variables."""
        config = cls()
        
        # Executor config
        if timeout := os.getenv("TOOLS_DEFAULT_TIMEOUT"):
            config.executor.default_timeout_seconds = float(timeout)
        if max_concurrent := os.getenv("TOOLS_MAX_CONCURRENT"):
            config.executor.max_concurrent_executions = int(max_concurrent)
        if sandbox := os.getenv("TOOLS_SANDBOX_TYPE"):
            config.executor.sandbox_type = sandbox
        
        # Security config
        if os.getenv("TOOLS_ALLOW_SHELL", "").lower() == "true":
            config.security.allow_shell_execution = True
        if os.getenv("TOOLS_ALLOW_NETWORK", "").lower() == "false":
            config.security.allow_network_access = False
        
        # Builtin tools config
        if os.getenv("TOOLS_ENABLE_SHELL", "").lower() == "true":
            config.builtin.enable_shell_tools = True
        
        # Metrics
        if os.getenv("TOOLS_DISABLE_METRICS", "").lower() == "true":
            config.enable_metrics = False
        
        logger.info("ToolsConfig loaded from environment")
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "executor": {
                "default_timeout_seconds": self.executor.default_timeout_seconds,
                "max_timeout_seconds": self.executor.max_timeout_seconds,
                "max_concurrent_executions": self.executor.max_concurrent_executions,
                "enable_sandboxing": self.executor.enable_sandboxing,
                "sandbox_type": self.executor.sandbox_type,
            },
            "registry": {
                "auto_discover": self.registry.auto_discover,
                "enable_custom_tools": self.registry.enable_custom_tools,
            },
            "security": {
                "allow_shell_execution": self.security.allow_shell_execution,
                "allow_file_write": self.security.allow_file_write,
                "allow_network_access": self.security.allow_network_access,
            },
            "builtin": {
                "file_tools": self.builtin.enable_file_tools,
                "web_tools": self.builtin.enable_web_tools,
                "git_tools": self.builtin.enable_git_tools,
                "search_tools": self.builtin.enable_search_tools,
                "shell_tools": self.builtin.enable_shell_tools,
            },
            "metrics_enabled": self.enable_metrics,
        }


# Default configuration instance
default_tools_config = ToolsConfig()
