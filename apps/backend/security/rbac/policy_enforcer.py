"""Policy enforcement for RBAC.

World-Class Standards:
- Declarative policy definitions
- Context-aware enforcement
- Rate limiting integration
- Comprehensive audit logging
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..models import SUPPORTED_PROVIDERS
from .permission_checker import PermissionChecker
from .role_definitions import Permission


@dataclass
class PolicyRule:
    """A policy enforcement rule."""

    id: str
    name: str
    description: str
    permissions_required: list[Permission]
    providers_required: list[str] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)
    deny_message: str = "Access denied"
    enabled: bool = True


@dataclass
class EnforcementResult:
    """Result of policy enforcement."""

    allowed: bool
    rule_id: str | None = None
    reason: str = ""
    missing_permissions: list[str] = field(default_factory=list)
    missing_providers: list[str] = field(default_factory=list)


class PolicyEnforcer:
    """Enforces access policies based on rules.

    Provides:
    - Declarative policy rules
    - Context-aware evaluation
    - Extensible condition checking
    - Audit integration

    Example:
        enforcer = PolicyEnforcer(permission_checker)

        # Add custom policy rule
        await enforcer.add_rule(PolicyRule(
            id="require_openai_for_review",
            name="Require OpenAI Access for Code Review",
            permissions_required=[Permission.LLM_EXECUTE],
            providers_required=["openai"],
        ))

        # Enforce policy
        result = await enforcer.enforce("user123", "require_openai_for_review")
    """

    def __init__(
        self,
        permission_checker: PermissionChecker,
        audit_callback: Callable[[str, str, bool], Awaitable[None]] | None = None,
    ):
        """Initialize policy enforcer.

        Args:
            permission_checker: Permission checker instance
            audit_callback: Optional callback for audit logging
        """
        self._checker = permission_checker
        self._audit_callback = audit_callback
        self._rules: dict[str, PolicyRule] = {}
        self._condition_handlers: dict[str, Callable] = {}

        # Register built-in condition handlers
        self._register_builtin_conditions()

    def _register_builtin_conditions(self) -> None:
        """Register built-in condition handlers."""
        self._condition_handlers["time_range"] = self._check_time_range
        self._condition_handlers["ip_whitelist"] = self._check_ip_whitelist
        self._condition_handlers["max_requests"] = self._check_max_requests

    async def add_rule(self, rule: PolicyRule) -> None:
        """Add a policy rule.

        Args:
            rule: Policy rule to add
        """
        # Validate providers
        for provider in rule.providers_required:
            if provider not in SUPPORTED_PROVIDERS:
                raise ValueError(f"Invalid provider: {provider}")

        self._rules[rule.id] = rule

    async def remove_rule(self, rule_id: str) -> bool:
        """Remove a policy rule.

        Args:
            rule_id: ID of rule to remove

        Returns:
            True if removed
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    async def enforce(
        self,
        user_id: str,
        rule_id: str,
        context: dict[str, Any] | None = None,
    ) -> EnforcementResult:
        """Enforce a specific policy rule.

        Args:
            user_id: User to check
            rule_id: Rule to enforce
            context: Additional context for conditions

        Returns:
            Enforcement result
        """
        rule = self._rules.get(rule_id)
        if not rule:
            return EnforcementResult(
                allowed=False,
                reason=f"Policy rule not found: {rule_id}",
            )

        if not rule.enabled:
            return EnforcementResult(
                allowed=True,
                rule_id=rule_id,
                reason="Rule is disabled",
            )

        result = await self._evaluate_rule(user_id, rule, context or {})

        # Audit callback
        if self._audit_callback:
            await self._audit_callback(user_id, rule_id, result.allowed)

        return result

    async def enforce_all(
        self,
        user_id: str,
        context: dict[str, Any] | None = None,
    ) -> list[EnforcementResult]:
        """Enforce all enabled policy rules.

        Args:
            user_id: User to check
            context: Additional context

        Returns:
            List of enforcement results
        """
        results = []

        for rule_id in self._rules:
            result = await self.enforce(user_id, rule_id, context)
            results.append(result)

        return results

    async def _evaluate_rule(
        self,
        user_id: str,
        rule: PolicyRule,
        context: dict[str, Any],
    ) -> EnforcementResult:
        """Evaluate a single rule."""
        # Check permissions
        missing_permissions = []
        for permission in rule.permissions_required:
            if not await self._checker.has_permission(user_id, permission):
                missing_permissions.append(permission.value)

        if missing_permissions:
            return EnforcementResult(
                allowed=False,
                rule_id=rule.id,
                reason=rule.deny_message,
                missing_permissions=missing_permissions,
            )

        # Check providers
        missing_providers = []
        for provider in rule.providers_required:
            if not await self._checker.can_access_provider(user_id, provider):
                missing_providers.append(provider)

        if missing_providers:
            return EnforcementResult(
                allowed=False,
                rule_id=rule.id,
                reason=rule.deny_message,
                missing_providers=missing_providers,
            )

        # Check conditions
        for condition_type, condition_value in rule.conditions.items():
            handler = self._condition_handlers.get(condition_type)
            if handler:
                if not await handler(user_id, condition_value, context):
                    return EnforcementResult(
                        allowed=False,
                        rule_id=rule.id,
                        reason=f"Condition failed: {condition_type}",
                    )

        return EnforcementResult(
            allowed=True,
            rule_id=rule.id,
            reason="Access granted",
        )

    async def _check_time_range(
        self,
        user_id: str,
        value: dict[str, str],
        context: dict[str, Any],
    ) -> bool:
        """Check if current time is within allowed range."""
        now = datetime.utcnow()
        current_hour = now.hour

        start_hour = int(value.get("start", 0))
        end_hour = int(value.get("end", 24))

        return start_hour <= current_hour < end_hour

    async def _check_ip_whitelist(
        self,
        user_id: str,
        value: list[str],
        context: dict[str, Any],
    ) -> bool:
        """Check if request IP is in whitelist."""
        request_ip = context.get("ip_address", "")
        return request_ip in value

    async def _check_max_requests(
        self,
        user_id: str,
        value: dict[str, int],
        context: dict[str, Any],
    ) -> bool:
        """Check if user is within request limit."""
        # This would integrate with rate limiting
        max_requests = value.get("limit", 100)
        current_requests = context.get("request_count", 0)
        return current_requests < max_requests

    def register_condition_handler(
        self,
        condition_type: str,
        handler: Callable,
    ) -> None:
        """Register a custom condition handler.

        Args:
            condition_type: Condition type name
            handler: Async handler function(user_id, value, context) -> bool
        """
        self._condition_handlers[condition_type] = handler

    async def get_applicable_rules(
        self,
        user_id: str,
        action: str,
    ) -> list[PolicyRule]:
        """Get all rules that apply to an action.

        Args:
            user_id: User performing action
            action: Action being performed

        Returns:
            List of applicable rules
        """
        applicable = []

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            # Check if any required permission matches the action
            for perm in rule.permissions_required:
                if action.lower() in perm.value.lower():
                    applicable.append(rule)
                    break

        return applicable

    async def export_rules(self) -> str:
        """Export all rules as JSON."""
        rules_data = []
        for rule in self._rules.values():
            rules_data.append(
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "permissions_required": [
                        p.value for p in rule.permissions_required
                    ],
                    "providers_required": rule.providers_required,
                    "conditions": rule.conditions,
                    "deny_message": rule.deny_message,
                    "enabled": rule.enabled,
                }
            )

        return json.dumps(rules_data, indent=2)

    async def import_rules(self, rules_json: str) -> int:
        """Import rules from JSON.

        Args:
            rules_json: JSON string with rules

        Returns:
            Number of rules imported
        """
        rules_data = json.loads(rules_json)
        imported = 0

        for rule_data in rules_data:
            try:
                rule = PolicyRule(
                    id=rule_data["id"],
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    permissions_required=[
                        Permission(p) for p in rule_data.get("permissions_required", [])
                    ],
                    providers_required=rule_data.get("providers_required", []),
                    conditions=rule_data.get("conditions", {}),
                    deny_message=rule_data.get("deny_message", "Access denied"),
                    enabled=rule_data.get("enabled", True),
                )
                await self.add_rule(rule)
                imported += 1
            except (KeyError, ValueError):
                continue

        return imported
