"""Tool parameter validator.

Part of Phase 2: LLM Architecture
"""

import logging
from dataclasses import dataclass
from typing import Any

from .tool_schema import ParameterType, ToolParameter, ToolSchema

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """A validation error."""

    field: str
    message: str
    expected: str | None = None
    actual: str | None = None


@dataclass
class ValidationResult:
    """Result of validation."""

    valid: bool
    errors: list[ValidationError]
    coerced_values: dict[str, Any]

    @property
    def error_messages(self) -> list[str]:
        return [f"{e.field}: {e.message}" for e in self.errors]


class ToolValidator:
    """Validate tool parameters against schema.

    Features:
    - JSON Schema validation
    - Type coercion
    - Custom validators
    - Detailed error messages
    """

    def __init__(self, coerce_types: bool = True):
        self._coerce_types = coerce_types
        self._custom_validators: dict[str, callable] = {}

    def validate(self, schema: ToolSchema, params: dict[str, Any]) -> ValidationResult:
        """Validate parameters against schema."""
        errors = []
        coerced = {}

        param_map = {p.name: p for p in schema.parameters}

        # Check required parameters
        for param in schema.parameters:
            if param.required and param.name not in params:
                errors.append(
                    ValidationError(
                        field=param.name, message="Required parameter missing"
                    )
                )

        # Validate each provided parameter
        for key, value in params.items():
            if key not in param_map:
                # Unknown parameter - could be warning or error
                logger.debug("Unknown parameter: %s", key)
                coerced[key] = value
                continue

            param = param_map[key]

            # Type validation and coercion
            type_result = self._validate_type(param, value)
            if type_result[0] is False:
                errors.append(
                    ValidationError(
                        field=key,
                        message=f"Invalid type: expected {param.type.value}",
                        expected=param.type.value,
                        actual=type(value).__name__,
                    )
                )
                coerced[key] = value
            else:
                coerced[key] = type_result[1]

            # Enum validation
            if param.enum and coerced[key] not in param.enum:
                errors.append(
                    ValidationError(
                        field=key,
                        message=f"Value not in allowed values: {param.enum}",
                        expected=str(param.enum),
                        actual=str(coerced[key]),
                    )
                )

            # Custom validators
            if key in self._custom_validators:
                try:
                    self._custom_validators[key](coerced[key])
                except Exception as e:
                    errors.append(ValidationError(field=key, message=str(e)))

        # Add defaults for missing optional parameters
        for param in schema.parameters:
            if param.name not in coerced and param.default is not None:
                coerced[param.name] = param.default

        return ValidationResult(
            valid=len(errors) == 0, errors=errors, coerced_values=coerced
        )

    def _validate_type(self, param: ToolParameter, value: Any) -> tuple[bool, Any]:
        """Validate and optionally coerce type."""
        target_type = param.type

        # Check if already correct type
        if self._is_correct_type(value, target_type):
            return (True, value)

        # Try coercion if enabled
        if self._coerce_types:
            try:
                coerced = self._coerce_type(value, target_type)
                return (True, coerced)
            except (ValueError, TypeError):
                pass

        return (False, value)

    def _is_correct_type(self, value: Any, expected: ParameterType) -> bool:
        """Check if value matches expected type."""
        type_checks = {
            ParameterType.STRING: lambda v: isinstance(v, str),
            ParameterType.NUMBER: lambda v: isinstance(v, (int, float))
            and not isinstance(v, bool),
            ParameterType.INTEGER: lambda v: isinstance(v, int)
            and not isinstance(v, bool),
            ParameterType.BOOLEAN: lambda v: isinstance(v, bool),
            ParameterType.ARRAY: lambda v: isinstance(v, list),
            ParameterType.OBJECT: lambda v: isinstance(v, dict),
            ParameterType.NULL: lambda v: v is None,
        }

        check = type_checks.get(expected, lambda v: True)
        return check(value)

    def _coerce_type(self, value: Any, target: ParameterType) -> Any:
        """Attempt to coerce value to target type."""
        if target == ParameterType.STRING:
            return str(value)

        elif target == ParameterType.NUMBER:
            return float(value)

        elif target == ParameterType.INTEGER:
            return int(value)

        elif target == ParameterType.BOOLEAN:
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes"):
                    return True
                elif value.lower() in ("false", "0", "no"):
                    return False
            return bool(value)

        elif target == ParameterType.ARRAY:
            if isinstance(value, (list, tuple)):
                return list(value)
            return [value]

        elif target == ParameterType.OBJECT:
            if isinstance(value, dict):
                return value
            raise TypeError("Cannot coerce to object")

        elif target == ParameterType.NULL:
            return None

        return value

    def add_validator(self, field: str, validator: callable) -> None:
        """Add a custom validator for a field."""
        self._custom_validators[field] = validator

    def remove_validator(self, field: str) -> None:
        """Remove a custom validator."""
        self._custom_validators.pop(field, None)


def validate_tool_call(
    schema: ToolSchema, params: dict[str, Any], coerce: bool = True
) -> ValidationResult:
    """Convenience function to validate a tool call."""
    validator = ToolValidator(coerce_types=coerce)
    return validator.validate(schema, params)
