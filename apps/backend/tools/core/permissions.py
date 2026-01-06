"""Permission management for tools.

Manages permissions for tool execution.

Capabilities:
- Define permissions
- Grant/revoke permissions
- Check permission requirements
- Permission inheritance
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import threading


class PermissionLevel(Enum):
    """Permission levels."""
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    ADMIN = 4


@dataclass
class Permission:
    """A tool permission."""
    name: str
    description: str
    level: PermissionLevel = PermissionLevel.READ
    resource: Optional[str] = None  # Optional resource constraint
    expires_at: Optional[str] = None  # Optional expiration


# Standard permissions
STANDARD_PERMISSIONS = {
    # Filesystem
    "read_files": Permission("read_files", "Read files", PermissionLevel.READ),
    "write_files": Permission("write_files", "Write files", PermissionLevel.WRITE),
    "delete_files": Permission("delete_files", "Delete files", PermissionLevel.WRITE),
    "create_dirs": Permission("create_dirs", "Create directories", PermissionLevel.WRITE),
    
    # Git
    "git_read": Permission("git_read", "Read git info", PermissionLevel.READ),
    "git_write": Permission("git_write", "Write git changes", PermissionLevel.WRITE),
    
    # Terminal
    "execute_commands": Permission("execute_commands", "Execute commands", PermissionLevel.EXECUTE),
    "spawn_processes": Permission("spawn_processes", "Spawn processes", PermissionLevel.EXECUTE),
    
    # Web
    "http_requests": Permission("http_requests", "Make HTTP requests", PermissionLevel.READ),
    
    # LLM
    "llm_access": Permission("llm_access", "Access LLM", PermissionLevel.READ),
}


class PermissionManager:
    """Manages permissions for tool execution.
    
    Thread-safe permission management with grant/revoke
    and inheritance support.
    
    Example:
        manager = PermissionManager()
        manager.grant("read_files")
        
        if manager.has_permission("read_files"):
            # Can read files
            pass
    """
    
    def __init__(self):
        """Initialize permission manager."""
        self._granted: Set[str] = set()
        self._denied: Set[str] = set()
        self._lock = threading.Lock()
    
    def grant(self, permission: str) -> None:
        """Grant a permission.
        
        Args:
            permission: Permission name to grant
        """
        with self._lock:
            self._granted.add(permission)
            self._denied.discard(permission)
    
    def grant_all(self, permissions: List[str]) -> None:
        """Grant multiple permissions.
        
        Args:
            permissions: Permission names to grant
        """
        for perm in permissions:
            self.grant(perm)
    
    def revoke(self, permission: str) -> None:
        """Revoke a permission.
        
        Args:
            permission: Permission name to revoke
        """
        with self._lock:
            self._granted.discard(permission)
    
    def deny(self, permission: str) -> None:
        """Explicitly deny a permission.
        
        Args:
            permission: Permission name to deny
        """
        with self._lock:
            self._denied.add(permission)
            self._granted.discard(permission)
    
    def has_permission(self, permission: str) -> bool:
        """Check if permission is granted.
        
        Args:
            permission: Permission name to check
            
        Returns:
            True if granted and not denied
        """
        with self._lock:
            if permission in self._denied:
                return False
            return permission in self._granted
    
    def check_permissions(self, required: Set[str]) -> List[str]:
        """Check multiple permissions.
        
        Args:
            required: Set of required permissions
            
        Returns:
            List of missing permissions
        """
        missing = []
        for perm in required:
            if not self.has_permission(perm):
                missing.append(perm)
        return missing
    
    def list_granted(self) -> List[str]:
        """List all granted permissions.
        
        Returns:
            List of granted permission names
        """
        with self._lock:
            return list(self._granted)
    
    def list_denied(self) -> List[str]:
        """List all denied permissions.
        
        Returns:
            List of denied permission names
        """
        with self._lock:
            return list(self._denied)
    
    def clear(self) -> None:
        """Clear all permissions."""
        with self._lock:
            self._granted.clear()
            self._denied.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "granted": self.list_granted(),
            "denied": self.list_denied(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionManager":
        """Create from dictionary."""
        manager = cls()
        manager.grant_all(data.get("granted", []))
        for perm in data.get("denied", []):
            manager.deny(perm)
        return manager
    
    def create_restricted(self, allowed: Set[str]) -> "PermissionManager":
        """Create restricted manager with subset of permissions.
        
        Args:
            allowed: Allowed permissions to inherit
            
        Returns:
            New PermissionManager with restricted permissions
        """
        manager = PermissionManager()
        for perm in self._granted:
            if perm in allowed:
                manager.grant(perm)
        return manager
