"""Prompt template with variable substitution.

Part of Phase 2: LLM Architecture
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class VariableType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    OBJECT = "object"


@dataclass
class TemplateVariable:
    """A variable in a prompt template."""

    name: str
    var_type: VariableType = VariableType.STRING
    required: bool = True
    default: Any = None
    description: str = ""
    validator: str | None = None  # Regex pattern

    def validate(self, value: Any) -> bool:
        if value is None and self.required:
            return False
        if self.validator and isinstance(value, str):
            return bool(re.match(self.validator, value))
        return True


@dataclass
class PromptTemplate:
    """A reusable prompt template."""

    id: str
    name: str
    template: str
    variables: list[TemplateVariable] = field(default_factory=list)
    description: str = ""
    category: str = "general"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    _var_pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")

    def render(self, **kwargs) -> str:
        """Render template with provided values."""
        result = self.template

        for var in self.variables:
            value = kwargs.get(var.name, var.default)

            if value is None and var.required:
                raise ValueError(f"Missing required variable: {var.name}")

            if not var.validate(value):
                raise ValueError(f"Invalid value for {var.name}: {value}")

            placeholder = f"{{{{{var.name}}}}}"
            result = result.replace(
                placeholder, str(value) if value is not None else ""
            )

        # Handle any remaining placeholders with kwargs
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))

        return result.strip()

    def extract_variables(self) -> set[str]:
        """Extract variable names from template."""
        return set(self._var_pattern.findall(self.template))

    def validate_complete(self, **kwargs) -> list[str]:
        """Check if all required variables are provided."""
        missing = []
        for var in self.variables:
            if var.required and var.name not in kwargs and var.default is None:
                missing.append(var.name)
        return missing

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "template": self.template,
            "variables": [
                {"name": v.name, "type": v.var_type.value, "required": v.required}
                for v in self.variables
            ],
            "description": self.description,
            "category": self.category,
            "version": self.version,
        }
