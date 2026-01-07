"""
Tool Validator - Phase 8 Implementation.

Comprehensive tool validation.

World-Class Standards:
- Schema validation
- Security checks
- Compatibility verification
- Detailed error reporting
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import re
import logging

from ..models import Tool, ToolCategory, ToolParameter, ParameterType

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Detailed validation error."""
    field: str
    message: str
    severity: str  # error, warning
    
    def __str__(self) -> str:
        return f"[{self.severity}] {self.field}: {self.message}"


class ToolValidator:
    """
    Comprehensive tool validation.
    
    Features:
    - Schema validation
    - Security checks
    - Naming conventions
    - Parameter validation
    """
    
    # Valid tool name pattern
    NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
    
    # Reserved names
    RESERVED_NAMES = {
        "help", "exit", "quit", "config", "settings", "admin",
        "system", "internal", "private", "test", "debug"
    }
    
    # Dangerous patterns in descriptions
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",
        r"format\s+[a-z]:",
        r"delete\s+\*",
        r"drop\s+database",
    ]
    
    def __init__(
        self,
        strict: bool = True,
        allow_reserved: bool = False,
    ) -> None:
        """Initialize validator."""
        self.strict = strict
        self.allow_reserved = allow_reserved
        logger.info("ToolValidator initialized (strict=%s)", strict)
    
    def validate(self, tool: Tool) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a tool definition.
        
        Args:
            tool: Tool to validate
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors: List[ValidationError] = []
        
        # Validate name
        errors.extend(self._validate_name(tool.name))
        
        # Validate description
        errors.extend(self._validate_description(tool.description))
        
        # Validate category
        errors.extend(self._validate_category(tool.category))
        
        # Validate parameters
        errors.extend(self._validate_parameters(tool.parameters))
        
        # Validate handler
        errors.extend(self._validate_handler(tool))
        
        # Validate version
        errors.extend(self._validate_version(tool.version))
        
        # Security checks
        errors.extend(self._security_check(tool))
        
        # Determine overall validity
        has_errors = any(e.severity == "error" for e in errors)
        
        return not has_errors, errors
    
    def _validate_name(self, name: str) -> List[ValidationError]:
        """Validate tool name."""
        errors = []
        
        if not name:
            errors.append(ValidationError(
                field="name",
                message="Tool name is required",
                severity="error",
            ))
            return errors
        
        if not self.NAME_PATTERN.match(name):
            errors.append(ValidationError(
                field="name",
                message=(
                    "Name must start with lowercase letter and contain "
                    "only lowercase letters, numbers, and underscores"
                ),
                severity="error",
            ))
        
        if len(name) < 3:
            errors.append(ValidationError(
                field="name",
                message="Name should be at least 3 characters",
                severity="warning",
            ))
        
        if len(name) > 64:
            errors.append(ValidationError(
                field="name",
                message="Name should not exceed 64 characters",
                severity="error",
            ))
        
        if not self.allow_reserved and name in self.RESERVED_NAMES:
            errors.append(ValidationError(
                field="name",
                message=f"'{name}' is a reserved name",
                severity="error",
            ))
        
        return errors
    
    def _validate_description(self, description: str) -> List[ValidationError]:
        """Validate tool description."""
        errors = []
        
        if not description:
            errors.append(ValidationError(
                field="description",
                message="Tool description is required",
                severity="error",
            ))
            return errors
        
        if len(description) < 10:
            errors.append(ValidationError(
                field="description",
                message="Description should be at least 10 characters",
                severity="warning",
            ))
        
        if len(description) > 1000:
            errors.append(ValidationError(
                field="description",
                message="Description should not exceed 1000 characters",
                severity="warning",
            ))
        
        return errors
    
    def _validate_category(self, category: ToolCategory) -> List[ValidationError]:
        """Validate tool category."""
        errors = []
        
        if not isinstance(category, ToolCategory):
            errors.append(ValidationError(
                field="category",
                message=f"Invalid category: {category}",
                severity="error",
            ))
        
        return errors
    
    def _validate_parameters(
        self, parameters: List[ToolParameter]
    ) -> List[ValidationError]:
        """Validate tool parameters."""
        errors = []
        seen_names = set()
        
        for i, param in enumerate(parameters):
            prefix = f"parameters[{i}]"
            
            # Check name
            if not param.name:
                errors.append(ValidationError(
                    field=f"{prefix}.name",
                    message="Parameter name is required",
                    severity="error",
                ))
            elif param.name in seen_names:
                errors.append(ValidationError(
                    field=f"{prefix}.name",
                    message=f"Duplicate parameter name: {param.name}",
                    severity="error",
                ))
            else:
                seen_names.add(param.name)
            
            # Check description
            if not param.description:
                errors.append(ValidationError(
                    field=f"{prefix}.description",
                    message="Parameter description is required",
                    severity="warning",
                ))
            
            # Check type
            if not isinstance(param.type, ParameterType):
                errors.append(ValidationError(
                    field=f"{prefix}.type",
                    message=f"Invalid parameter type: {param.type}",
                    severity="error",
                ))
            
            # Check default value type
            if param.default is not None:
                type_valid = self._check_value_type(param.default, param.type)
                if not type_valid:
                    errors.append(ValidationError(
                        field=f"{prefix}.default",
                        message=(
                            f"Default value type mismatch: expected {param.type.value}"
                        ),
                        severity="error",
                    ))
            
            # Check enum values
            if param.enum:
                for enum_val in param.enum:
                    if not self._check_value_type(enum_val, param.type):
                        errors.append(ValidationError(
                            field=f"{prefix}.enum",
                            message=f"Enum value type mismatch: {enum_val}",
                            severity="error",
                        ))
        
        return errors
    
    def _validate_handler(self, tool: Tool) -> List[ValidationError]:
        """Validate tool handler."""
        errors = []
        
        if tool.handler is None:
            if self.strict:
                errors.append(ValidationError(
                    field="handler",
                    message="Tool handler is required",
                    severity="error",
                ))
            else:
                errors.append(ValidationError(
                    field="handler",
                    message="Tool has no handler",
                    severity="warning",
                ))
        elif not callable(tool.handler):
            errors.append(ValidationError(
                field="handler",
                message="Handler must be callable",
                severity="error",
            ))
        
        return errors
    
    def _validate_version(self, version: str) -> List[ValidationError]:
        """Validate version string."""
        errors = []
        
        # Simple semver check
        version_pattern = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$")
        if not version_pattern.match(version):
            errors.append(ValidationError(
                field="version",
                message="Version should follow semver (e.g., 1.0.0)",
                severity="warning",
            ))
        
        return errors
    
    def _security_check(self, tool: Tool) -> List[ValidationError]:
        """Check for security issues."""
        errors = []
        
        # Check for dangerous patterns in description
        full_text = f"{tool.name} {tool.description}"
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, full_text, re.IGNORECASE):
                errors.append(ValidationError(
                    field="security",
                    message=f"Potentially dangerous pattern found: {pattern}",
                    severity="warning",
                ))
        
        # Check for shell category without confirmation
        if tool.category == ToolCategory.SHELL and not tool.requires_confirmation:
            errors.append(ValidationError(
                field="security",
                message="Shell tools should require confirmation",
                severity="warning",
            ))
        
        return errors
    
    def _check_value_type(self, value: Any, expected: ParameterType) -> bool:
        """Check if value matches expected type."""
        if expected == ParameterType.STRING:
            return isinstance(value, str)
        elif expected == ParameterType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected == ParameterType.FLOAT:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected == ParameterType.BOOLEAN:
            return isinstance(value, bool)
        elif expected == ParameterType.ARRAY:
            return isinstance(value, list)
        elif expected == ParameterType.OBJECT:
            return isinstance(value, dict)
        elif expected in (ParameterType.FILE_PATH, ParameterType.URL):
            return isinstance(value, str)
        return True
