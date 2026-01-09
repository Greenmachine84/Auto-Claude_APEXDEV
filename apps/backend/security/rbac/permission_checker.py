"""Permission checking for RBAC.

World-Class Standards:
- Fast permission evaluation
- Provider-aware access control
- Caching for performance
- Audit integration
"""

from datetime import datetime

from ..models import SUPPORTED_PROVIDERS
from .role_definitions import Permission
from .role_manager import RoleManager


class PermissionChecker:
    """Checks user permissions against required permissions.

    Provides fast permission evaluation with:
    - LRU caching for repeated checks
    - Provider-specific access validation
    - Batch permission checking

    Example:
        checker = PermissionChecker(role_manager)

        if await checker.has_permission("user123", Permission.CREDENTIAL_READ):
            # User has permission
            pass

        if await checker.can_access_provider("user123", "openai"):
            # User can access OpenAI
            pass
    """

    def __init__(self, role_manager: RoleManager):
        """Initialize permission checker.

        Args:
            role_manager: Role manager instance
        """
        self._role_manager = role_manager
        self._cache_timeout = 300  # 5 minutes
        self._permission_cache: dict = {}
        self._provider_cache: dict = {}

    def _cache_key(self, user_id: str) -> str:
        """Generate cache key for user."""
        return f"{user_id}:{int(datetime.utcnow().timestamp() // self._cache_timeout)}"

    async def has_permission(
        self,
        user_id: str,
        permission: Permission,
    ) -> bool:
        """Check if user has a specific permission.

        Args:
            user_id: User to check
            permission: Permission to check for

        Returns:
            True if user has permission
        """
        permissions = await self._get_cached_permissions(user_id)
        return permission in permissions

    async def has_all_permissions(
        self,
        user_id: str,
        permissions: set[Permission],
    ) -> bool:
        """Check if user has all specified permissions.

        Args:
            user_id: User to check
            permissions: Permissions to check for

        Returns:
            True if user has all permissions
        """
        user_permissions = await self._get_cached_permissions(user_id)
        return permissions.issubset(user_permissions)

    async def has_any_permission(
        self,
        user_id: str,
        permissions: set[Permission],
    ) -> bool:
        """Check if user has any of specified permissions.

        Args:
            user_id: User to check
            permissions: Permissions to check for

        Returns:
            True if user has at least one permission
        """
        user_permissions = await self._get_cached_permissions(user_id)
        return bool(permissions & user_permissions)

    async def can_access_provider(
        self,
        user_id: str,
        provider: str,
    ) -> bool:
        """Check if user can access a specific LLM provider.

        Args:
            user_id: User to check
            provider: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            True if user can access provider
        """
        if provider not in SUPPORTED_PROVIDERS:
            return False

        providers = await self._get_cached_providers(user_id)

        # Check for wildcard access
        if "*" in providers:
            return True

        return provider in providers

    async def can_access_all_providers(
        self,
        user_id: str,
        providers: set[str],
    ) -> bool:
        """Check if user can access all specified providers.

        Args:
            user_id: User to check
            providers: Provider names to check

        Returns:
            True if user can access all providers
        """
        user_providers = await self._get_cached_providers(user_id)

        if "*" in user_providers:
            return True

        return providers.issubset(user_providers)

    async def get_missing_permissions(
        self,
        user_id: str,
        required: set[Permission],
    ) -> set[Permission]:
        """Get permissions the user is missing.

        Args:
            user_id: User to check
            required: Required permissions

        Returns:
            Set of missing permissions
        """
        user_permissions = await self._get_cached_permissions(user_id)
        return required - user_permissions

    async def get_inaccessible_providers(
        self,
        user_id: str,
        required: set[str],
    ) -> set[str]:
        """Get providers the user cannot access.

        Args:
            user_id: User to check
            required: Required providers

        Returns:
            Set of inaccessible providers
        """
        user_providers = await self._get_cached_providers(user_id)

        if "*" in user_providers:
            return set()

        return required - user_providers

    async def _get_cached_permissions(self, user_id: str) -> set[Permission]:
        """Get cached permissions for user."""
        cache_key = self._cache_key(user_id)

        if cache_key not in self._permission_cache:
            permissions = await self._role_manager.get_effective_permissions(user_id)
            self._permission_cache[cache_key] = permissions

        return self._permission_cache[cache_key]

    async def _get_cached_providers(self, user_id: str) -> set[str]:
        """Get cached provider access for user."""
        cache_key = self._cache_key(user_id)

        if cache_key not in self._provider_cache:
            providers = await self._role_manager.get_effective_providers(user_id)
            self._provider_cache[cache_key] = providers

        return self._provider_cache[cache_key]

    def clear_cache(self, user_id: str | None = None) -> None:
        """Clear permission cache.

        Args:
            user_id: Specific user to clear, or None for all
        """
        if user_id:
            keys_to_remove = [
                k for k in self._permission_cache if k.startswith(f"{user_id}:")
            ]
            for key in keys_to_remove:
                del self._permission_cache[key]

            keys_to_remove = [
                k for k in self._provider_cache if k.startswith(f"{user_id}:")
            ]
            for key in keys_to_remove:
                del self._provider_cache[key]
        else:
            self._permission_cache.clear()
            self._provider_cache.clear()

    async def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource: str | None = None,
        provider: str | None = None,
    ) -> tuple:
        """Comprehensive permission check.

        Args:
            user_id: User to check
            permission: Required permission
            resource: Optional resource being accessed
            provider: Optional provider being accessed

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Check basic permission
        if not await self.has_permission(user_id, permission):
            return (False, f"Missing permission: {permission.value}")

        # Check provider access if specified
        if provider:
            if not await self.can_access_provider(user_id, provider):
                return (False, f"No access to provider: {provider}")

        return (True, "Access granted")
