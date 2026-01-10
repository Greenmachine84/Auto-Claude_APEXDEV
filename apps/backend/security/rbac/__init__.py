"""Role-Based Access Control (RBAC) module.

Provides enterprise-grade RBAC with:
- Provider-aware permissions for all 8 LLM providers
- Hierarchical role management
- Policy enforcement
- Audit integration
"""

from .permission_checker import PermissionChecker
from .policy_enforcer import PolicyEnforcer
from .role_definitions import (
    PROVIDER_PERMISSIONS,
    DefaultRoles,
    Permission,
    RoleDefinition,
)
from .role_manager import RoleManager

__all__ = [
    "RoleManager",
    "PermissionChecker",
    "PolicyEnforcer",
    "DefaultRoles",
    "Permission",
    "RoleDefinition",
    "PROVIDER_PERMISSIONS",
]
