"""
Type parser.

Parses Python type hints for documentation.
"""

import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, get_args, get_origin


class TypeCategory(Enum):
    """Categories of types."""
    PRIMITIVE = "primitive"
    COLLECTION = "collection"
    MAPPING = "mapping"
    UNION = "union"
    OPTIONAL = "optional"
    CALLABLE = "callable"
    GENERIC = "generic"
    CLASS = "class"
    LITERAL = "literal"
    ANY = "any"


@dataclass
class ParsedType:
    """Parsed type information."""
    name: str
    category: TypeCategory
    description: str = ""
    args: list["ParsedType"] = field(default_factory=list)
    is_optional: bool = False
    default: Any = None
    origin: Optional[type] = None
    raw_type: Any = None


class TypeParser:
    """Parses Python type hints."""

    # Primitive types
    PRIMITIVES = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        bytes: "bytes",
        type(None): "null",
    }

    # Collection types
    COLLECTIONS = {
        list: "array",
        tuple: "tuple",
        set: "set",
        frozenset: "frozenset",
    }

    # Mapping types
    MAPPINGS = {
        dict: "object",
    }

    def __init__(self):
        """Initialize type parser."""
        pass

    def parse(self, type_hint: Any) -> ParsedType:
        """
        Parse a type hint.

        Args:
            type_hint: The type hint to parse

        Returns:
            Parsed type information
        """
        if type_hint is None or type_hint is type(None):
            return ParsedType(name="null", category=TypeCategory.PRIMITIVE)

        if type_hint is Any:
            return ParsedType(name="any", category=TypeCategory.ANY)

        # Get origin for generic types
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        # Handle Union types
        if origin is Union:
            return self._parse_union(type_hint, args)

        # Handle Optional (Union[X, None])
        if self._is_optional(type_hint):
            return self._parse_optional(type_hint, args)

        # Handle primitive types
        if type_hint in self.PRIMITIVES:
            return ParsedType(
                name=self.PRIMITIVES[type_hint],
                category=TypeCategory.PRIMITIVE,
                raw_type=type_hint,
            )

        # Handle collection types
        if origin in self.COLLECTIONS or type_hint in self.COLLECTIONS:
            return self._parse_collection(type_hint, origin, args)

        # Handle mapping types
        if origin in self.MAPPINGS or type_hint in self.MAPPINGS:
            return self._parse_mapping(type_hint, origin, args)

        # Handle Callable
        if origin is type(lambda: None).__class__ or str(type_hint).startswith("typing.Callable"):
            return self._parse_callable(type_hint, args)

        # Handle Literal
        if str(origin).startswith("typing.Literal"):
            return self._parse_literal(type_hint, args)

        # Handle classes
        if isinstance(type_hint, type):
            return self._parse_class(type_hint)

        # Handle generic types
        if origin is not None:
            return self._parse_generic(type_hint, origin, args)

        # Fallback
        return ParsedType(
            name=str(type_hint),
            category=TypeCategory.ANY,
            raw_type=type_hint,
        )

    def _is_optional(self, type_hint: Any) -> bool:
        """Check if type is Optional."""
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is Union and len(args) == 2:
            return type(None) in args

        return False

    def _parse_union(self, type_hint: Any, args: tuple) -> ParsedType:
        """Parse Union type."""
        parsed_args = [self.parse(arg) for arg in args if arg is not type(None)]

        # If only one non-None type, it's Optional
        if len(parsed_args) == 1 and type(None) in args:
            result = parsed_args[0]
            result.is_optional = True
            return result

        return ParsedType(
            name=" | ".join(arg.name for arg in parsed_args),
            category=TypeCategory.UNION,
            args=parsed_args,
            is_optional=type(None) in args,
            raw_type=type_hint,
        )

    def _parse_optional(self, type_hint: Any, args: tuple) -> ParsedType:
        """Parse Optional type."""
        inner_type = [arg for arg in args if arg is not type(None)][0]
        result = self.parse(inner_type)
        result.is_optional = True
        return result

    def _parse_collection(self, type_hint: Any, origin: Any, args: tuple) -> ParsedType:
        """Parse collection type."""
        base_type = origin or type_hint
        type_name = self.COLLECTIONS.get(base_type, "array")

        parsed_args = [self.parse(arg) for arg in args] if args else []

        # Format name with type parameters
        if parsed_args:
            args_str = ", ".join(arg.name for arg in parsed_args)
            name = f"{type_name}[{args_str}]"
        else:
            name = type_name

        return ParsedType(
            name=name,
            category=TypeCategory.COLLECTION,
            args=parsed_args,
            origin=base_type,
            raw_type=type_hint,
        )

    def _parse_mapping(self, type_hint: Any, origin: Any, args: tuple) -> ParsedType:
        """Parse mapping type."""
        base_type = origin or type_hint
        type_name = self.MAPPINGS.get(base_type, "object")

        parsed_args = [self.parse(arg) for arg in args] if args else []

        # Format name with type parameters
        if len(parsed_args) == 2:
            name = f"{type_name}[{parsed_args[0].name}, {parsed_args[1].name}]"
        else:
            name = type_name

        return ParsedType(
            name=name,
            category=TypeCategory.MAPPING,
            args=parsed_args,
            origin=base_type,
            raw_type=type_hint,
        )

    def _parse_callable(self, type_hint: Any, args: tuple) -> ParsedType:
        """Parse Callable type."""
        if args:
            param_types = args[0] if args[0] is not ... else []
            return_type = args[1] if len(args) > 1 else Any

            param_names = [self.parse(t).name for t in param_types] if isinstance(param_types, (list, tuple)) else ["..."]
            return_name = self.parse(return_type).name

            name = f"Callable[[{', '.join(param_names)}], {return_name}]"
        else:
            name = "Callable"

        return ParsedType(
            name=name,
            category=TypeCategory.CALLABLE,
            raw_type=type_hint,
        )

    def _parse_literal(self, type_hint: Any, args: tuple) -> ParsedType:
        """Parse Literal type."""
        values = [repr(arg) for arg in args]
        name = f"Literal[{', '.join(values)}]"

        return ParsedType(
            name=name,
            category=TypeCategory.LITERAL,
            raw_type=type_hint,
        )

    def _parse_class(self, type_hint: type) -> ParsedType:
        """Parse class type."""
        name = type_hint.__name__
        module = type_hint.__module__

        if module != "builtins":
            name = f"{module}.{name}"

        return ParsedType(
            name=name,
            category=TypeCategory.CLASS,
            raw_type=type_hint,
        )

    def _parse_generic(self, type_hint: Any, origin: type, args: tuple) -> ParsedType:
        """Parse generic type."""
        base_name = origin.__name__ if hasattr(origin, "__name__") else str(origin)
        parsed_args = [self.parse(arg) for arg in args]

        if parsed_args:
            args_str = ", ".join(arg.name for arg in parsed_args)
            name = f"{base_name}[{args_str}]"
        else:
            name = base_name

        return ParsedType(
            name=name,
            category=TypeCategory.GENERIC,
            args=parsed_args,
            origin=origin,
            raw_type=type_hint,
        )

    def to_json_schema_type(self, parsed: ParsedType) -> dict:
        """
        Convert parsed type to JSON Schema type.

        Args:
            parsed: Parsed type

        Returns:
            JSON Schema type definition
        """
        type_mapping = {
            "string": {"type": "string"},
            "integer": {"type": "integer"},
            "number": {"type": "number"},
            "boolean": {"type": "boolean"},
            "null": {"type": "null"},
            "any": {},
            "array": {"type": "array"},
            "object": {"type": "object"},
        }

        if parsed.name in type_mapping:
            schema = type_mapping[parsed.name].copy()
        elif parsed.category == TypeCategory.COLLECTION:
            schema = {"type": "array"}
            if parsed.args:
                schema["items"] = self.to_json_schema_type(parsed.args[0])
        elif parsed.category == TypeCategory.MAPPING:
            schema = {"type": "object"}
            if len(parsed.args) == 2:
                schema["additionalProperties"] = self.to_json_schema_type(parsed.args[1])
        elif parsed.category == TypeCategory.UNION:
            schemas = [self.to_json_schema_type(arg) for arg in parsed.args]
            schema = {"oneOf": schemas}
        elif parsed.category == TypeCategory.LITERAL:
            values = get_args(parsed.raw_type) if parsed.raw_type else []
            schema = {"enum": list(values)}
        else:
            schema = {"type": "object", "description": parsed.name}

        if parsed.is_optional:
            if "type" in schema:
                schema["type"] = [schema["type"], "null"]
            else:
                schema = {"oneOf": [schema, {"type": "null"}]}

        return schema

    def format_for_docs(self, parsed: ParsedType) -> str:
        """
        Format type for documentation.

        Args:
            parsed: Parsed type

        Returns:
            Formatted type string
        """
        name = parsed.name

        if parsed.is_optional and not name.endswith("| null"):
            name = f"{name} | null"

        return f"`{name}`"

    def get_type_description(self, parsed: ParsedType) -> str:
        """
        Get human-readable description of type.

        Args:
            parsed: Parsed type

        Returns:
            Type description
        """
        descriptions = {
            TypeCategory.PRIMITIVE: f"A {parsed.name} value",
            TypeCategory.COLLECTION: f"A collection of values",
            TypeCategory.MAPPING: f"A key-value mapping",
            TypeCategory.UNION: f"One of: {parsed.name}",
            TypeCategory.OPTIONAL: f"Optional {parsed.args[0].name if parsed.args else 'value'}",
            TypeCategory.CALLABLE: "A callable function",
            TypeCategory.GENERIC: f"A {parsed.origin.__name__ if parsed.origin else 'generic'} type",
            TypeCategory.CLASS: f"An instance of {parsed.name}",
            TypeCategory.LITERAL: f"One of the literal values: {parsed.name}",
            TypeCategory.ANY: "Any type",
        }

        return descriptions.get(parsed.category, f"A {parsed.name}")
