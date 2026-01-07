"""
Rule Definitions - Phase 9 Implementation.

Rule parsing, validation, and DSL support for governance policies.

World-Class Standards:
- Declarative rule language
- Type-safe rule validation
- Hot-reload support
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import yaml
import logging

from ..models import (
    PolicyRule,
    Policy,
    PolicyAction,
    RuleOperator,
    SUPPORTED_PROVIDERS,
)


logger = logging.getLogger(__name__)


class RuleParser:
    """
    Parses rule definitions from various formats.
    
    Supports JSON, YAML, and dictionary formats.
    """
    
    VALID_OPERATORS = [op.value for op in RuleOperator]
    VALID_ACTIONS = [act.value for act in PolicyAction]
    
    def parse_rule(self, data: Dict[str, Any]) -> PolicyRule:
        """Parse a single rule from dictionary."""
        # Validate required fields
        if "id" not in data:
            raise ValueError("Rule must have an 'id'")
        if "name" not in data:
            raise ValueError("Rule must have a 'name'")
        
        # Parse operator
        operator_str = data.get("operator", "eq")
        try:
            operator = RuleOperator(operator_str)
        except ValueError:
            raise ValueError(
                f"Invalid operator: {operator_str}. "
                f"Must be one of: {self.VALID_OPERATORS}"
            )
        
        # Parse action
        action_str = data.get("action", "allow")
        try:
            action = PolicyAction(action_str)
        except ValueError:
            raise ValueError(
                f"Invalid action: {action_str}. "
                f"Must be one of: {self.VALID_ACTIONS}"
            )
        
        # Validate provider if specified
        provider = data.get("provider")
        if provider and provider not in SUPPORTED_PROVIDERS:
            logger.warning(f"Unknown provider in rule: {provider}")
        
        return PolicyRule(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            field=data.get("field", ""),
            operator=operator,
            value=data.get("value"),
            action=action,
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True),
            provider=provider,
        )
    
    def parse_policy(self, data: Dict[str, Any]) -> Policy:
        """Parse a policy from dictionary."""
        if "id" not in data:
            raise ValueError("Policy must have an 'id'")
        if "name" not in data:
            raise ValueError("Policy must have a 'name'")
        
        # Parse default action
        default_action_str = data.get("default_action", "allow")
        try:
            default_action = PolicyAction(default_action_str)
        except ValueError:
            raise ValueError(
                f"Invalid default_action: {default_action_str}. "
                f"Must be one of: {self.VALID_ACTIONS}"
            )
        
        # Parse rules
        rules = []
        for rule_data in data.get("rules", []):
            rules.append(self.parse_rule(rule_data))
        
        return Policy(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            rules=rules,
            default_action=default_action,
            enabled=data.get("enabled", True),
            applies_to=data.get("applies_to", []),
        )
    
    def parse_json(self, json_str: str) -> Policy:
        """Parse policy from JSON string."""
        data = json.loads(json_str)
        return self.parse_policy(data)
    
    def parse_yaml(self, yaml_str: str) -> Policy:
        """Parse policy from YAML string."""
        data = yaml.safe_load(yaml_str)
        return self.parse_policy(data)


class RuleValidator:
    """
    Validates rules for correctness and consistency.
    """
    
    def validate_rule(self, rule: PolicyRule) -> List[str]:
        """
        Validate a single rule.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        # ID validation
        if not rule.id or not rule.id.strip():
            errors.append("Rule ID cannot be empty")
        
        # Name validation
        if not rule.name or not rule.name.strip():
            errors.append("Rule name cannot be empty")
        
        # Field validation for non-catch-all rules
        if rule.action != PolicyAction.ALLOW and not rule.field:
            errors.append("Non-allow rules should specify a field")
        
        # Provider validation
        if rule.provider and rule.provider not in SUPPORTED_PROVIDERS:
            errors.append(
                f"Invalid provider: {rule.provider}. "
                f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        
        # Priority validation
        if rule.priority < 0:
            errors.append("Priority must be non-negative")
        
        return errors
    
    def validate_policy(self, policy: Policy) -> List[str]:
        """
        Validate a policy and all its rules.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        # Policy ID validation
        if not policy.id or not policy.id.strip():
            errors.append("Policy ID cannot be empty")
        
        # Policy name validation
        if not policy.name or not policy.name.strip():
            errors.append("Policy name cannot be empty")
        
        # Check for duplicate rule IDs
        rule_ids = [r.id for r in policy.rules]
        if len(rule_ids) != len(set(rule_ids)):
            errors.append("Policy contains duplicate rule IDs")
        
        # Validate each rule
        for rule in policy.rules:
            rule_errors = self.validate_rule(rule)
            for error in rule_errors:
                errors.append(f"Rule '{rule.id}': {error}")
        
        return errors


class RuleBuilder:
    """
    Fluent builder for creating rules.
    
    Provides a clean API for programmatic rule creation.
    """
    
    def __init__(self) -> None:
        self._id: str = ""
        self._name: str = ""
        self._description: str = ""
        self._field: str = ""
        self._operator: RuleOperator = RuleOperator.EQ
        self._value: Any = None
        self._action: PolicyAction = PolicyAction.ALLOW
        self._priority: int = 0
        self._enabled: bool = True
        self._provider: Optional[str] = None
    
    def with_id(self, rule_id: str) -> "RuleBuilder":
        self._id = rule_id
        return self
    
    def with_name(self, name: str) -> "RuleBuilder":
        self._name = name
        return self
    
    def with_description(self, description: str) -> "RuleBuilder":
        self._description = description
        return self
    
    def when_field(self, field: str) -> "RuleBuilder":
        self._field = field
        return self
    
    def equals(self, value: Any) -> "RuleBuilder":
        self._operator = RuleOperator.EQ
        self._value = value
        return self
    
    def not_equals(self, value: Any) -> "RuleBuilder":
        self._operator = RuleOperator.NE
        self._value = value
        return self
    
    def greater_than(self, value: Any) -> "RuleBuilder":
        self._operator = RuleOperator.GT
        self._value = value
        return self
    
    def less_than(self, value: Any) -> "RuleBuilder":
        self._operator = RuleOperator.LT
        self._value = value
        return self
    
    def is_in(self, values: List[Any]) -> "RuleBuilder":
        self._operator = RuleOperator.IN
        self._value = values
        return self
    
    def not_in(self, values: List[Any]) -> "RuleBuilder":
        self._operator = RuleOperator.NOT_IN
        self._value = values
        return self
    
    def contains(self, value: str) -> "RuleBuilder":
        self._operator = RuleOperator.CONTAINS
        self._value = value
        return self
    
    def matches(self, pattern: str) -> "RuleBuilder":
        self._operator = RuleOperator.MATCHES
        self._value = pattern
        return self
    
    def then_allow(self) -> "RuleBuilder":
        self._action = PolicyAction.ALLOW
        return self
    
    def then_deny(self) -> "RuleBuilder":
        self._action = PolicyAction.DENY
        return self
    
    def then_require_approval(self) -> "RuleBuilder":
        self._action = PolicyAction.REQUIRE_APPROVAL
        return self
    
    def then_log(self) -> "RuleBuilder":
        self._action = PolicyAction.LOG
        return self
    
    def with_priority(self, priority: int) -> "RuleBuilder":
        self._priority = priority
        return self
    
    def for_provider(self, provider: str) -> "RuleBuilder":
        self._provider = provider
        return self
    
    def disabled(self) -> "RuleBuilder":
        self._enabled = False
        return self
    
    def build(self) -> PolicyRule:
        """Build the rule."""
        if not self._id:
            raise ValueError("Rule ID is required")
        if not self._name:
            raise ValueError("Rule name is required")
        
        return PolicyRule(
            id=self._id,
            name=self._name,
            description=self._description,
            field=self._field,
            operator=self._operator,
            value=self._value,
            action=self._action,
            priority=self._priority,
            enabled=self._enabled,
            provider=self._provider,
        )
