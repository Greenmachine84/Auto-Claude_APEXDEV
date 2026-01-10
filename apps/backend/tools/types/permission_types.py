"""Permission type definitions.

Defines types for the permission system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PermissionLevel(str, Enum):
    """Permission level classification."""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

    def __ge__(self, other: "PermissionLevel") -> bool:
        """Compare permission levels."""
        order = [self.NONE, self.READ, self.WRITE, self.EXECUTE, self.ADMIN]
        return order.index(self) >= order.index(other)

    def __gt__(self, other: "PermissionLevel") -> bool:
        """Compare permission levels."""
        order = [self.NONE, self.READ, self.WRITE, self.EXECUTE, self.ADMIN]
        return order.index(self) > order.index(other)

    def __le__(self, other: "PermissionLevel") -> bool:
        """Compare permission levels."""
        return not self > other

    def __lt__(self, other: "PermissionLevel") -> bool:
        """Compare permission levels."""
        return not self >= other


class PermissionScope(str, Enum):
    """Permission scope classification."""

    # File scopes
    FILE = "file"
    DIRECTORY = "directory"
    WORKSPACE = "workspace"
    SYSTEM = "system"

    # Operation scopes
    TOOL = "tool"
    SKILL = "skill"
    AGENT = "agent"

    # External scopes
    NETWORK = "network"
    API = "api"


@dataclass
class PermissionGrant:
    """A granted permission."""

    scope: PermissionScope
    level: PermissionLevel
    resource: str  # Path, URL, or resource identifier
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    granted_by: str = "system"
    conditions: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if permission is still valid."""
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True

    def matches(
        self, scope: PermissionScope, resource: str, level: PermissionLevel
    ) -> bool:
        """Check if grant matches request."""
        if not self.is_valid():
            return False

        if self.scope != scope:
            return False

        if self.level < level:
            return False

        # Check resource matching
        if self.resource == "*":
            return True
        if resource.startswith(self.resource):
            return True

        return self.resource == resource

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scope": self.scope.value,
            "level": self.level.value,
            "resource": self.resource,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "granted_by": self.granted_by,
            "conditions": self.conditions,
        }


@dataclass
class PermissionRequest:
    """A request for permission."""

    scope: PermissionScope
    level: PermissionLevel
    resource: str
    reason: str
    requester: str
    requested_at: datetime = field(default_factory=datetime.now)
    auto_approve: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scope": self.scope.value,
            "level": self.level.value,
            "resource": self.resource,
            "reason": self.reason,
            "requester": self.requester,
            "requested_at": self.requested_at.isoformat(),
            "auto_approve": self.auto_approve,
        }


@dataclass
class PermissionPolicy:
    """Permission policy configuration."""

    name: str
    description: str
    default_level: PermissionLevel = PermissionLevel.NONE
    allowed_scopes: set[PermissionScope] = field(default_factory=set)
    denied_scopes: set[PermissionScope] = field(default_factory=set)
    resource_patterns: list[str] = field(default_factory=list)
    max_level: PermissionLevel = PermissionLevel.EXECUTE
    auto_approve_read: bool = True

    def allows(self, scope: PermissionScope, level: PermissionLevel) -> bool:
        """Check if policy allows scope and level."""
        if scope in self.denied_scopes:
            return False
        if self.allowed_scopes and scope not in self.allowed_scopes:
            return False
        if level > self.max_level:
            return False
        return True
