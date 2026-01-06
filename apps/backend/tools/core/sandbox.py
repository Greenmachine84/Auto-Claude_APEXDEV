"""Sandbox for tool execution.

Provides isolated execution environment for tools.

Capabilities:
- Resource isolation
- Filesystem restrictions
- Network restrictions
- Execution limits
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
import os


@dataclass
class SandboxConfig:
    """Configuration for sandbox."""
    # Filesystem
    allowed_paths: List[str] = field(default_factory=list)
    denied_paths: List[str] = field(default_factory=list)
    read_only_paths: List[str] = field(default_factory=list)
    max_file_size_bytes: int = 100 * 1024 * 1024  # 100MB
    
    # Network
    allow_network: bool = False
    allowed_hosts: List[str] = field(default_factory=list)
    denied_hosts: List[str] = field(default_factory=list)
    
    # Execution
    max_execution_time_seconds: int = 300
    max_memory_bytes: int = 512 * 1024 * 1024  # 512MB
    max_processes: int = 10
    
    # Commands
    allowed_commands: List[str] = field(default_factory=list)
    denied_commands: List[str] = field(default_factory=list)


class Sandbox:
    """Isolated execution environment.
    
    Provides restrictions and validation for tool execution
    to ensure safety.
    
    Example:
        config = SandboxConfig(
            allowed_paths=["/workspace"],
            allow_network=False,
        )
        sandbox = Sandbox(config)
        
        if sandbox.can_access_path("/workspace/file.txt"):
            # Path is allowed
            pass
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        """Initialize sandbox.
        
        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()
        self._active = False
    
    def activate(self) -> None:
        """Activate the sandbox."""
        self._active = True
    
    def deactivate(self) -> None:
        """Deactivate the sandbox."""
        self._active = False
    
    @property
    def is_active(self) -> bool:
        """Check if sandbox is active."""
        return self._active
    
    def can_access_path(self, path: str, write: bool = False) -> bool:
        """Check if path access is allowed.
        
        Args:
            path: Path to check
            write: Whether write access is needed
            
        Returns:
            True if access is allowed
        """
        if not self._active:
            return True
        
        abs_path = os.path.abspath(path)
        
        # Check denied paths first
        for denied in self.config.denied_paths:
            if abs_path.startswith(os.path.abspath(denied)):
                return False
        
        # Check if in allowed paths
        if self.config.allowed_paths:
            allowed = False
            for allow in self.config.allowed_paths:
                if abs_path.startswith(os.path.abspath(allow)):
                    allowed = True
                    break
            if not allowed:
                return False
        
        # Check read-only for write operations
        if write:
            for readonly in self.config.read_only_paths:
                if abs_path.startswith(os.path.abspath(readonly)):
                    return False
        
        return True
    
    def can_access_network(self, host: Optional[str] = None) -> bool:
        """Check if network access is allowed.
        
        Args:
            host: Optional host to check
            
        Returns:
            True if access is allowed
        """
        if not self._active:
            return True
        
        if not self.config.allow_network:
            return False
        
        if host:
            # Check denied hosts
            for denied in self.config.denied_hosts:
                if host == denied or host.endswith(f".{denied}"):
                    return False
            
            # Check allowed hosts if specified
            if self.config.allowed_hosts:
                allowed = False
                for allow in self.config.allowed_hosts:
                    if host == allow or host.endswith(f".{allow}"):
                        allowed = True
                        break
                return allowed
        
        return True
    
    def can_execute_command(self, command: str) -> bool:
        """Check if command execution is allowed.
        
        Args:
            command: Command to check (first word)
            
        Returns:
            True if allowed
        """
        if not self._active:
            return True
        
        # Extract command name
        cmd = command.split()[0] if command else ""
        
        # Check denied commands
        for denied in self.config.denied_commands:
            if cmd == denied:
                return False
        
        # Check allowed commands if specified
        if self.config.allowed_commands:
            return cmd in self.config.allowed_commands
        
        return True
    
    def validate_file_size(self, size_bytes: int) -> bool:
        """Validate file size is within limits.
        
        Args:
            size_bytes: File size to check
            
        Returns:
            True if within limits
        """
        if not self._active:
            return True
        
        return size_bytes <= self.config.max_file_size_bytes
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get current sandbox constraints.
        
        Returns:
            Dictionary of constraints
        """
        return {
            "active": self._active,
            "allowed_paths": self.config.allowed_paths,
            "allow_network": self.config.allow_network,
            "max_execution_time": self.config.max_execution_time_seconds,
            "max_memory_mb": self.config.max_memory_bytes // (1024 * 1024),
        }
    
    def __enter__(self) -> "Sandbox":
        """Context manager entry."""
        self.activate()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.deactivate()
