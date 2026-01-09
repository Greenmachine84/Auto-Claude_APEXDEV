"""Result validator.

Validates task results.

Capabilities:
- Schema validation
- Custom validators
- Error reporting
- Validation rules
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from orchestrator.results.collector import CollectedResult

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """A validation error."""

    field: str
    message: str
    value: Any = None


@dataclass
class ValidationResult:
    """Result of validation."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, field: str, message: str, value: Any = None) -> None:
        """Add validation error."""
        self.errors.append(
            ValidationError(
                field=field,
                message=message,
                value=value,
            )
        )
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "errors": [{"field": e.field, "message": e.message} for e in self.errors],
            "warnings": self.warnings,
        }


class ResultValidator:
    """Validate results.

    Checks results against rules and schemas.

    Example:
        validator = ResultValidator()
        validator.add_rule("required", lambda r: r.result is not None)
        result = validator.validate(collected)
    """

    def __init__(self):
        """Initialize validator."""
        self._rules: dict[str, Callable[[CollectedResult], bool]] = {}
        self._validators: dict[str, Callable[[Any], ValidationResult]] = {}

        logger.debug("ResultValidator initialized")

    def add_rule(
        self,
        name: str,
        rule: Callable[[CollectedResult], bool],
        message: str | None = None,
    ) -> None:
        """Add validation rule."""
        self._rules[name] = (rule, message or f"Failed rule: {name}")

    def add_validator(
        self,
        name: str,
        validator: Callable[[Any], ValidationResult],
    ) -> None:
        """Add custom validator."""
        self._validators[name] = validator

    def validate(
        self,
        result: CollectedResult,
        rules: list[str] | None = None,
    ) -> ValidationResult:
        """Validate a result."""
        validation = ValidationResult(valid=True)

        # Apply specified rules or all rules
        rules_to_apply = rules or list(self._rules.keys())

        for rule_name in rules_to_apply:
            if rule_name not in self._rules:
                continue

            rule, message = self._rules[rule_name]
            try:
                if not rule(result):
                    validation.add_error(
                        field=rule_name,
                        message=message,
                        value=result.result,
                    )
            except Exception as e:
                validation.add_error(
                    field=rule_name,
                    message=f"Rule error: {e}",
                )

        return validation

    def validate_batch(
        self,
        results: list[CollectedResult],
        rules: list[str] | None = None,
    ) -> dict[str, ValidationResult]:
        """Validate multiple results."""
        return {r.task_id: self.validate(r, rules) for r in results}

    def validate_schema(
        self,
        result: CollectedResult,
        schema: dict[str, Any],
    ) -> ValidationResult:
        """Validate result against schema."""
        validation = ValidationResult(valid=True)

        if not isinstance(result.result, dict):
            validation.add_error(
                field="result",
                message="Result must be a dictionary for schema validation",
            )
            return validation

        # Check required fields
        for field_name, field_schema in schema.items():
            if field_schema.get("required") and field_name not in result.result:
                validation.add_error(
                    field=field_name,
                    message=f"Required field missing: {field_name}",
                )

            if field_name in result.result:
                value = result.result[field_name]

                # Type check
                expected_type = field_schema.get("type")
                if expected_type:
                    type_map = {
                        "string": str,
                        "integer": int,
                        "number": (int, float),
                        "boolean": bool,
                        "array": list,
                        "object": dict,
                    }
                    expected = type_map.get(expected_type)
                    if expected and not isinstance(value, expected):
                        validation.add_error(
                            field=field_name,
                            message=f"Expected {expected_type}, got {type(value).__name__}",
                            value=value,
                        )

        return validation


# Built-in rules
def not_none(result: CollectedResult) -> bool:
    """Check result is not None."""
    return result.result is not None


def is_success(result: CollectedResult) -> bool:
    """Check result is successful."""
    return result.success


def is_dict(result: CollectedResult) -> bool:
    """Check result is a dictionary."""
    return isinstance(result.result, dict)


def is_list(result: CollectedResult) -> bool:
    """Check result is a list."""
    return isinstance(result.result, list)
