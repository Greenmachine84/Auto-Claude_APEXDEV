"""Tool schema definitions for function calling.

Part of Phase 2: LLM Architecture
"""

import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, get_type_hints

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


@dataclass
class ToolParameter:
    """A parameter for a tool."""

    name: str
    type: ParameterType
    description: str = ""
    required: bool = True
    default: Any = None
    enum: list[Any] | None = None
    items: Optional["ToolParameter"] = None  # For array types
    properties: dict[str, "ToolParameter"] | None = None  # For object types

    def to_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format."""
        schema: dict[str, Any] = {"type": self.type.value}

        if self.description:
            schema["description"] = self.description

        if self.default is not None:
            schema["default"] = self.default

        if self.enum:
            schema["enum"] = self.enum

        if self.type == ParameterType.ARRAY and self.items:
            schema["items"] = self.items.to_schema()

        if self.type == ParameterType.OBJECT and self.properties:
            schema["properties"] = {
                k: v.to_schema() for k, v in self.properties.items()
            }

        return schema


@dataclass
class ToolSchema:
    """Schema for a tool/function."""

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    returns: ToolParameter | None = None

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def to_anthropic_schema(self) -> dict[str, Any]:
        """Convert to Anthropic tool format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def validate_arguments(self, args: dict[str, Any]) -> list[str]:
        """Validate arguments against schema. Returns list of errors."""
        errors = []
        param_map = {p.name: p for p in self.parameters}

        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in args:
                errors.append(f"Missing required parameter: {param.name}")

        # Check types (basic validation)
        for key, value in args.items():
            if key not in param_map:
                continue
            param = param_map[key]
            if not self._check_type(value, param.type):
                errors.append(
                    f"Parameter '{key}' has wrong type. "
                    f"Expected {param.type.value}, got {type(value).__name__}"
                )

        return errors

    def _check_type(self, value: Any, expected: ParameterType) -> bool:
        """Check if value matches expected type."""
        type_map = {
            ParameterType.STRING: str,
            ParameterType.NUMBER: (int, float),
            ParameterType.INTEGER: int,
            ParameterType.BOOLEAN: bool,
            ParameterType.ARRAY: list,
            ParameterType.OBJECT: dict,
            ParameterType.NULL: type(None),
        }
        expected_types = type_map.get(expected)
        if expected_types is None:
            return True
        return isinstance(value, expected_types)


def create_tool_schema(func: Callable) -> ToolSchema:
    """Create ToolSchema from a function's signature and docstring."""
    sig = inspect.signature(func)
    hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}

    # Parse docstring for descriptions
    doc = inspect.getdoc(func) or ""
    param_docs = _parse_docstring_params(doc)

    parameters = []
    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        # Determine type
        param_type = ParameterType.STRING  # default
        if name in hints:
            param_type = _python_type_to_param_type(hints[name])

        # Determine if required
        required = param.default == inspect.Parameter.empty
        default = None if required else param.default

        parameters.append(
            ToolParameter(
                name=name,
                type=param_type,
                description=param_docs.get(name, ""),
                required=required,
                default=default,
            )
        )

    return ToolSchema(
        name=func.__name__,
        description=doc.split("\n\n")[0] if doc else "",
        parameters=parameters,
    )


def _parse_docstring_params(doc: str) -> dict[str, str]:
    """Parse parameter descriptions from docstring."""
    params = {}
    lines = doc.split("\n")
    current_param = None

    for line in lines:
        line = line.strip()
        if line.startswith(":param "):
            parts = line[7:].split(":", 1)
            if len(parts) == 2:
                current_param = parts[0].strip()
                params[current_param] = parts[1].strip()
        elif line.startswith("Args:"):
            continue
        elif ":" in line and current_param is None:
            # Google-style docstring
            parts = line.split(":", 1)
            if len(parts) == 2 and not parts[0].startswith(" "):
                params[parts[0].strip()] = parts[1].strip()

    return params


def _python_type_to_param_type(py_type: type) -> ParameterType:
    """Convert Python type to ParameterType."""
    if py_type == str:
        return ParameterType.STRING
    elif py_type == int:
        return ParameterType.INTEGER
    elif py_type in (float, complex):
        return ParameterType.NUMBER
    elif py_type == bool:
        return ParameterType.BOOLEAN
    elif py_type == list:
        return ParameterType.ARRAY
    elif py_type == dict:
        return ParameterType.OBJECT
    elif py_type is None or py_type == type(None):
        return ParameterType.NULL
    return ParameterType.STRING
