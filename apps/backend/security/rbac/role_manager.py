"""Role management for RBAC system.

World-Class Standards:
- Hierarchical role support
- Provider-specific permissions for all 8 LLM providers
- Role inheritance
- Dynamic role assignment
"""
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict

from ..models import Role, PermissionScope, SUPPORTED_PROVIDERS
from .role_definitions import DefaultRoles, Permission, RoleDefinition


@dataclass
class UserRole:
    """User role assignment."""
    user_id: str
    role_id: str
    assigned_at: str
    assigned_by: str
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RoleManager:
    """Manages roles and user role assignments.
    
    Supports:
    - Role hierarchy with inheritance
    - Provider-specific permissions
    - Dynamic role creation
    - Role assignment with expiration
    
    Example:
        manager = RoleManager()
        await manager.initialize()
        
        # Assign developer role to user
        await manager.assign_role("user123", DefaultRoles.DEVELOPER.value, "admin")
        
        # Check role
        roles = await manager.get_user_roles("user123")
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize role manager.
        
        Args:
            storage_path: Path for role data storage
        """
        self._storage_path = storage_path or Path.home() / ".autoclaudedev" / "rbac"
        self._roles: Dict[str, RoleDefinition] = {}
        self._user_roles: Dict[str, List[UserRole]] = {}  # user_id -> roles
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize role manager with default roles."""
        if self._initialized:
            return
        
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load default roles
        self._load_default_roles()
        
        # Load persisted data
        await self._load_data()
        
        self._initialized = True
    
    def _load_default_roles(self) -> None:
        """Load built-in role definitions."""
        for role_enum in DefaultRoles:
            role_def = RoleDefinition.from_default(role_enum)
            self._roles[role_def.id] = role_def
    
    async def _load_data(self) -> None:
        """Load persisted role data."""
        # Load custom roles
        roles_file = self._storage_path / "roles.json"
        if roles_file.exists():
            try:
                data = json.loads(roles_file.read_text())
                for role_data in data.get("roles", []):
                    role_def = RoleDefinition(
                        id=role_data["id"],
                        name=role_data["name"],
                        description=role_data.get("description", ""),
                        permissions=set(Permission(p) for p in role_data.get("permissions", [])),
                        provider_access=set(role_data.get("provider_access", [])),
                        inherits_from=role_data.get("inherits_from"),
                        is_system=role_data.get("is_system", False),
                    )
                    self._roles[role_def.id] = role_def
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Load user role assignments
        assignments_file = self._storage_path / "assignments.json"
        if assignments_file.exists():
            try:
                data = json.loads(assignments_file.read_text())
                for user_id, roles in data.get("assignments", {}).items():
                    self._user_roles[user_id] = [
                        UserRole(
                            user_id=user_id,
                            role_id=r["role_id"],
                            assigned_at=r["assigned_at"],
                            assigned_by=r["assigned_by"],
                            expires_at=r.get("expires_at"),
                            metadata=r.get("metadata", {}),
                        )
                        for r in roles
                    ]
            except (json.JSONDecodeError, KeyError):
                pass
    
    async def _save_data(self) -> None:
        """Save role data to storage."""
        # Save custom roles
        custom_roles = [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": [p.value for p in role.permissions],
                "provider_access": list(role.provider_access),
                "inherits_from": role.inherits_from,
                "is_system": role.is_system,
            }
            for role in self._roles.values()
            if not role.is_system
        ]
        
        roles_file = self._storage_path / "roles.json"
        roles_file.write_text(json.dumps({"roles": custom_roles}, indent=2))
        
        # Save user assignments
        assignments = {
            user_id: [
                {
                    "role_id": r.role_id,
                    "assigned_at": r.assigned_at,
                    "assigned_by": r.assigned_by,
                    "expires_at": r.expires_at,
                    "metadata": r.metadata,
                }
                for r in roles
            ]
            for user_id, roles in self._user_roles.items()
        }
        
        assignments_file = self._storage_path / "assignments.json"
        assignments_file.write_text(json.dumps({"assignments": assignments}, indent=2))
    
    async def create_role(
        self,
        name: str,
        permissions: Set[Permission],
        provider_access: Optional[Set[str]] = None,
        description: str = "",
        inherits_from: Optional[str] = None,
    ) -> RoleDefinition:
        """Create a new custom role.
        
        Args:
            name: Role display name
            permissions: Set of permissions to grant
            provider_access: Set of provider names to grant access
            description: Role description
            inherits_from: ID of parent role to inherit from
            
        Returns:
            Created role definition
        """
        if not self._initialized:
            await self.initialize()
        
        # Validate provider access
        if provider_access:
            invalid = provider_access - set(SUPPORTED_PROVIDERS)
            if invalid:
                raise ValueError(f"Invalid providers: {invalid}")
        
        # Validate parent role
        if inherits_from and inherits_from not in self._roles:
            raise ValueError(f"Parent role not found: {inherits_from}")
        
        role_def = RoleDefinition(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            permissions=permissions,
            provider_access=provider_access or set(),
            inherits_from=inherits_from,
            is_system=False,
        )
        
        self._roles[role_def.id] = role_def
        await self._save_data()
        
        return role_def
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete a custom role.
        
        System roles cannot be deleted.
        
        Args:
            role_id: ID of role to delete
            
        Returns:
            True if deleted
        """
        if not self._initialized:
            await self.initialize()
        
        role = self._roles.get(role_id)
        if not role:
            return False
        
        if role.is_system:
            raise ValueError("Cannot delete system roles")
        
        del self._roles[role_id]
        
        # Remove assignments for this role
        for user_id in list(self._user_roles.keys()):
            self._user_roles[user_id] = [
                r for r in self._user_roles[user_id]
                if r.role_id != role_id
            ]
        
        await self._save_data()
        return True
    
    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str,
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UserRole:
        """Assign a role to a user.
        
        Args:
            user_id: User to assign role to
            role_id: Role to assign
            assigned_by: Who is assigning the role
            expires_at: Optional expiration timestamp
            metadata: Optional metadata
            
        Returns:
            User role assignment
        """
        if not self._initialized:
            await self.initialize()
        
        if role_id not in self._roles:
            raise ValueError(f"Role not found: {role_id}")
        
        # Check if already assigned
        if user_id in self._user_roles:
            for existing in self._user_roles[user_id]:
                if existing.role_id == role_id:
                    raise ValueError(f"Role already assigned to user")
        
        assignment = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_at=datetime.utcnow().isoformat() + "Z",
            assigned_by=assigned_by,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        
        self._user_roles[user_id].append(assignment)
        await self._save_data()
        
        return assignment
    
    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke a role from a user.
        
        Args:
            user_id: User to revoke from
            role_id: Role to revoke
            
        Returns:
            True if revoked
        """
        if not self._initialized:
            await self.initialize()
        
        if user_id not in self._user_roles:
            return False
        
        original_count = len(self._user_roles[user_id])
        self._user_roles[user_id] = [
            r for r in self._user_roles[user_id]
            if r.role_id != role_id
        ]
        
        if len(self._user_roles[user_id]) < original_count:
            await self._save_data()
            return True
        
        return False
    
    async def get_user_roles(self, user_id: str) -> List[UserRole]:
        """Get all roles assigned to a user.
        
        Filters out expired roles.
        
        Args:
            user_id: User to get roles for
            
        Returns:
            List of active role assignments
        """
        if not self._initialized:
            await self.initialize()
        
        if user_id not in self._user_roles:
            return []
        
        now = datetime.utcnow().isoformat()
        active_roles = []
        
        for role in self._user_roles[user_id]:
            # Check expiration
            if role.expires_at and role.expires_at < now:
                continue
            active_roles.append(role)
        
        return active_roles
    
    async def get_role(self, role_id: str) -> Optional[RoleDefinition]:
        """Get a role definition by ID."""
        if not self._initialized:
            await self.initialize()
        
        return self._roles.get(role_id)
    
    async def get_effective_permissions(
        self,
        user_id: str,
    ) -> Set[Permission]:
        """Get all effective permissions for a user.
        
        Includes inherited permissions from role hierarchy.
        
        Args:
            user_id: User to get permissions for
            
        Returns:
            Set of effective permissions
        """
        if not self._initialized:
            await self.initialize()
        
        permissions = set()
        
        for user_role in await self.get_user_roles(user_id):
            role_def = self._roles.get(user_role.role_id)
            if role_def:
                permissions.update(self._get_role_permissions(role_def))
        
        return permissions
    
    async def get_effective_providers(
        self,
        user_id: str,
    ) -> Set[str]:
        """Get all providers a user has access to.
        
        Includes inherited access from role hierarchy.
        
        Args:
            user_id: User to get provider access for
            
        Returns:
            Set of accessible provider names
        """
        if not self._initialized:
            await self.initialize()
        
        providers = set()
        
        for user_role in await self.get_user_roles(user_id):
            role_def = self._roles.get(user_role.role_id)
            if role_def:
                providers.update(self._get_role_providers(role_def))
        
        return providers
    
    def _get_role_permissions(
        self,
        role: RoleDefinition,
        visited: Optional[Set[str]] = None,
    ) -> Set[Permission]:
        """Get all permissions for a role including inherited."""
        if visited is None:
            visited = set()
        
        if role.id in visited:
            return set()  # Prevent cycles
        
        visited.add(role.id)
        permissions = role.permissions.copy()
        
        if role.inherits_from and role.inherits_from in self._roles:
            parent = self._roles[role.inherits_from]
            permissions.update(self._get_role_permissions(parent, visited))
        
        return permissions
    
    def _get_role_providers(
        self,
        role: RoleDefinition,
        visited: Optional[Set[str]] = None,
    ) -> Set[str]:
        """Get all provider access for a role including inherited."""
        if visited is None:
            visited = set()
        
        if role.id in visited:
            return set()
        
        visited.add(role.id)
        providers = role.provider_access.copy()
        
        if role.inherits_from and role.inherits_from in self._roles:
            parent = self._roles[role.inherits_from]
            providers.update(self._get_role_providers(parent, visited))
        
        return providers
    
    async def list_roles(self) -> List[RoleDefinition]:
        """List all defined roles."""
        if not self._initialized:
            await self.initialize()
        
        return list(self._roles.values())
    
    async def list_users_with_role(self, role_id: str) -> List[str]:
        """List all users with a specific role."""
        if not self._initialized:
            await self.initialize()
        
        return [
            user_id for user_id, roles in self._user_roles.items()
            if any(r.role_id == role_id for r in roles)
        ]
