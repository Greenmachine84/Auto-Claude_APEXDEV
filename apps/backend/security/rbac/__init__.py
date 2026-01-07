"""Role-Based Access Control (RBAC) module.

Provides enterprise-grade RBAC with:
- Provider-aware permissions for all 8 LLM providers
- Hierarchical role management
- Policy enforcement
- Audit integration
"""
from .role_manager import RoleManager
from .permission_checker import PermissionChecker
from .policy_enforcer import PolicyEnforcer
from .role_definitions import (
    DefaultRoles,
    Permission,
    RoleDefinition,
    PROVIDER_PERMISSIONS,
)

__all__ = [
    "RoleManager",
    "PermissionChecker",
    "PolicyEnforcer",
    "DefaultRoles",
    "Permission",
    "RoleDefinition",
    "PROVIDER_PERMISSIONS",
]
