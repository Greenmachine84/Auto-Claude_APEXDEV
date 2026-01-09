"""Role and permission definitions.

World-Class Standards:
- Comprehensive permission set
- Provider-aware roles for all 8 LLM providers
- Hierarchical role definitions
- Sensible defaults

Supported Providers (Equal Treatment):
- copilot (GitHub Copilot)
- openrouter
- ollama (local)
- lmstudio (local)
- gemini (Google)
- openai
- anthropic
- azure (Azure OpenAI)
"""

from dataclasses import dataclass, field
from enum import Enum

from ..models import SUPPORTED_PROVIDERS


class Permission(Enum):
    """System permissions."""

    # Credential permissions
    CREDENTIAL_READ = "credential:read"
    CREDENTIAL_WRITE = "credential:write"
    CREDENTIAL_DELETE = "credential:delete"
    CREDENTIAL_ROTATE = "credential:rotate"

    # LLM permissions
    LLM_EXECUTE = "llm:execute"
    LLM_CONFIGURE = "llm:configure"
    LLM_MONITOR = "llm:monitor"

    # Security permissions
    SECURITY_SCAN = "security:scan"
    SECURITY_CONFIGURE = "security:configure"
    SECURITY_BYPASS = "security:bypass"  # For emergency use only

    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    AUDIT_MANAGE = "audit:manage"

    # Role permissions
    ROLE_READ = "role:read"
    ROLE_WRITE = "role:write"
    ROLE_ASSIGN = "role:assign"

    # System permissions
    SYSTEM_CONFIGURE = "system:configure"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_ADMIN = "system:admin"

    # Data permissions
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_EXPORT = "data:export"


class DefaultRoles(Enum):
    """Default role identifiers."""

    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    SECURITY_ADMIN = "security_admin"
    SERVICE_ACCOUNT = "service_account"


# Provider-specific permission sets
PROVIDER_PERMISSIONS = {
    "copilot": {
        Permission.LLM_EXECUTE,
        Permission.LLM_MONITOR,
    },
    "openrouter": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
    "ollama": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
    "lmstudio": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
    "gemini": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
    "openai": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
    "anthropic": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
    "azure": {
        Permission.LLM_EXECUTE,
        Permission.LLM_CONFIGURE,
        Permission.LLM_MONITOR,
    },
}


@dataclass
class RoleDefinition:
    """Definition of a role with permissions."""

    id: str
    name: str
    description: str
    permissions: set[Permission]
    provider_access: set[str] = field(default_factory=set)
    inherits_from: str | None = None
    is_system: bool = False

    @classmethod
    def from_default(cls, default_role: DefaultRoles) -> "RoleDefinition":
        """Create role definition from default role."""
        definitions = {
            DefaultRoles.ADMIN: cls(
                id="admin",
                name="Administrator",
                description="Full system access including all providers",
                permissions=set(Permission),  # All permissions
                provider_access=set(SUPPORTED_PROVIDERS),  # All providers
                is_system=True,
            ),
            DefaultRoles.DEVELOPER: cls(
                id="developer",
                name="Developer",
                description="Standard developer access with LLM execution",
                permissions={
                    Permission.CREDENTIAL_READ,
                    Permission.LLM_EXECUTE,
                    Permission.LLM_MONITOR,
                    Permission.SECURITY_SCAN,
                    Permission.AUDIT_READ,
                    Permission.DATA_READ,
                    Permission.DATA_WRITE,
                },
                provider_access=set(SUPPORTED_PROVIDERS),  # All providers
                is_system=True,
            ),
            DefaultRoles.VIEWER: cls(
                id="viewer",
                name="Viewer",
                description="Read-only access",
                permissions={
                    Permission.AUDIT_READ,
                    Permission.DATA_READ,
                    Permission.LLM_MONITOR,
                    Permission.SYSTEM_MONITOR,
                },
                provider_access=set(),  # No provider access
                is_system=True,
            ),
            DefaultRoles.SECURITY_ADMIN: cls(
                id="security_admin",
                name="Security Administrator",
                description="Security configuration and monitoring",
                permissions={
                    Permission.CREDENTIAL_READ,
                    Permission.CREDENTIAL_WRITE,
                    Permission.CREDENTIAL_ROTATE,
                    Permission.SECURITY_SCAN,
                    Permission.SECURITY_CONFIGURE,
                    Permission.AUDIT_READ,
                    Permission.AUDIT_EXPORT,
                    Permission.AUDIT_MANAGE,
                    Permission.ROLE_READ,
                    Permission.ROLE_WRITE,
                    Permission.ROLE_ASSIGN,
                },
                provider_access=set(SUPPORTED_PROVIDERS),
                is_system=True,
            ),
            DefaultRoles.SERVICE_ACCOUNT: cls(
                id="service_account",
                name="Service Account",
                description="Automated service access",
                permissions={
                    Permission.CREDENTIAL_READ,
                    Permission.LLM_EXECUTE,
                    Permission.SECURITY_SCAN,
                    Permission.DATA_READ,
                    Permission.DATA_WRITE,
                },
                provider_access=set(SUPPORTED_PROVIDERS),
                is_system=True,
            ),
        }

        return definitions[default_role]

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a specific permission."""
        return permission in self.permissions

    def can_access_provider(self, provider: str) -> bool:
        """Check if role can access a provider."""
        return provider in self.provider_access or "*" in self.provider_access


# Pre-built role definitions for quick access
ADMIN_ROLE = RoleDefinition.from_default(DefaultRoles.ADMIN)
DEVELOPER_ROLE = RoleDefinition.from_default(DefaultRoles.DEVELOPER)
VIEWER_ROLE = RoleDefinition.from_default(DefaultRoles.VIEWER)
SECURITY_ADMIN_ROLE = RoleDefinition.from_default(DefaultRoles.SECURITY_ADMIN)
SERVICE_ACCOUNT_ROLE = RoleDefinition.from_default(DefaultRoles.SERVICE_ACCOUNT)
