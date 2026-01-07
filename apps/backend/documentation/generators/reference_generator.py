"""
Reference documentation generator.

Generates reference documentation for configuration,
schemas, and other structured data.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, get_type_hints

from ..config import DocumentationConfig
from .base import BaseGenerator
from ..models import (
    CodeExample,
    DocumentationEntry,
)


class FieldType(Enum):
    """Types of configuration fields."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"


@dataclass
class ConfigField:
    """A configuration field definition."""
    name: str
    field_type: FieldType
    description: str = ""
    required: bool = False
    default: Any = None
    enum_values: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    examples: list[Any] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = []
        lines.append(f"### `{self.name}`")
        lines.append("")
        lines.append(f"**Type:** `{self.field_type.value}`")

        if self.required:
            lines.append("**Required:** Yes")
        else:
            lines.append("**Required:** No")

        if self.default is not None:
            lines.append(f"**Default:** `{self.default}`")

        lines.append("")
        lines.append(self.description)

        if self.enum_values:
            lines.append("\n**Allowed values:**")
            for val in self.enum_values:
                lines.append(f"- `{val}`")

        if self.constraints:
            lines.append("\n**Constraints:**")
            for key, val in self.constraints.items():
                lines.append(f"- {key}: `{val}`")

        if self.examples:
            lines.append("\n**Examples:**")
            for ex in self.examples:
                lines.append(f"- `{ex}`")

        return "\n".join(lines)


@dataclass
class ConfigSchema:
    """A configuration schema definition."""
    id: str
    title: str
    description: str
    fields: list[ConfigField] = field(default_factory=list)
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)


class ReferenceGenerator(BaseGenerator):
    """Generates reference documentation."""

    def __init__(self, config: DocumentationConfig):
        """Initialize reference generator."""
        super().__init__(config)

    def generate(self, source: Any) -> list[DocumentationEntry]:
        """
        Generate reference documentation.

        Args:
            source: Schema, dataclass, or Pydantic model

        Returns:
            List of documentation entries
        """
        entries = []

        if isinstance(source, ConfigSchema):
            entries.append(self._generate_from_schema(source))
        elif hasattr(source, "__dataclass_fields__"):
            entries.append(self._generate_from_dataclass(source))
        elif hasattr(source, "__fields__"):  # Pydantic model
            entries.append(self._generate_from_pydantic(source))
        elif isinstance(source, dict):
            entries.append(self._generate_from_dict(source))

        return entries

    def generate_from_file(self, file_path: Path) -> list[DocumentationEntry]:
        """
        Generate reference documentation from a file.

        Args:
            file_path: Path to schema file (JSON, YAML)

        Returns:
            List of documentation entries
        """
        entries = []

        if file_path.suffix == ".json":
            entries.extend(self._parse_json_schema(file_path))
        elif file_path.suffix in (".yaml", ".yml"):
            entries.extend(self._parse_yaml_schema(file_path))

        return entries

    def _generate_from_schema(self, schema: ConfigSchema) -> DocumentationEntry:
        """Generate documentation from ConfigSchema."""
        lines = []

        # Header
        lines.append(f"# {schema.title}")
        lines.append("")
        lines.append(schema.description)
        lines.append("")
        lines.append(f"**Version:** {schema.version}")
        lines.append("")

        # Table of contents
        if schema.fields:
            lines.append("## Fields")
            lines.append("")
            lines.append("| Field | Type | Required | Default |")
            lines.append("|-------|------|----------|---------|")
            for fld in schema.fields:
                req = "Yes" if fld.required else "No"
                default = f"`{fld.default}`" if fld.default is not None else "-"
                lines.append(f"| [`{fld.name}`](#{fld.name}) | `{fld.field_type.value}` | {req} | {default} |")
            lines.append("")

            # Field details
            lines.append("## Field Details")
            lines.append("")
            for fld in schema.fields:
                lines.append(fld.to_markdown())
                lines.append("")

        content = "\n".join(lines)

        return DocumentationEntry(
            id=schema.id,
            title=schema.title,
            content=content,
            entry_type="reference",
            tags=["reference", "config"] + schema.tags,
        )

    def _generate_from_dataclass(self, cls: type) -> DocumentationEntry:
        """Generate documentation from a dataclass."""
        import dataclasses

        fields = []
        type_hints = get_type_hints(cls) if hasattr(cls, "__annotations__") else {}

        for fld in dataclasses.fields(cls):
            field_type = self._python_type_to_field_type(type_hints.get(fld.name, str))

            config_field = ConfigField(
                name=fld.name,
                field_type=field_type,
                default=fld.default if fld.default is not dataclasses.MISSING else None,
                required=fld.default is dataclasses.MISSING,
            )
            fields.append(config_field)

        schema = ConfigSchema(
            id=self.get_entry_id(cls.__name__),
            title=cls.__name__,
            description=cls.__doc__ or "",
            fields=fields,
        )

        return self._generate_from_schema(schema)

    def _generate_from_pydantic(self, cls: type) -> DocumentationEntry:
        """Generate documentation from a Pydantic model."""
        fields = []

        for field_name, field_info in cls.__fields__.items():
            field_type = self._python_type_to_field_type(field_info.outer_type_)

            config_field = ConfigField(
                name=field_name,
                field_type=field_type,
                description=field_info.field_info.description or "",
                default=field_info.default if field_info.default is not None else None,
                required=field_info.required,
            )
            fields.append(config_field)

        schema = ConfigSchema(
            id=self.get_entry_id(cls.__name__),
            title=cls.__name__,
            description=cls.__doc__ or "",
            fields=fields,
        )

        return self._generate_from_schema(schema)

    def _generate_from_dict(self, data: dict) -> DocumentationEntry:
        """Generate documentation from a dictionary schema."""
        fields = []

        for name, info in data.get("properties", {}).items():
            field_type = FieldType(info.get("type", "string"))
            config_field = ConfigField(
                name=name,
                field_type=field_type,
                description=info.get("description", ""),
                default=info.get("default"),
                enum_values=info.get("enum", []),
            )
            fields.append(config_field)

        schema = ConfigSchema(
            id=data.get("id", "unknown"),
            title=data.get("title", "Configuration"),
            description=data.get("description", ""),
            fields=fields,
        )

        return self._generate_from_schema(schema)

    def _python_type_to_field_type(self, python_type: type) -> FieldType:
        """Convert Python type to FieldType."""
        type_name = getattr(python_type, "__name__", str(python_type))

        type_mapping = {
            "str": FieldType.STRING,
            "int": FieldType.INTEGER,
            "float": FieldType.FLOAT,
            "bool": FieldType.BOOLEAN,
            "list": FieldType.ARRAY,
            "dict": FieldType.OBJECT,
        }

        return type_mapping.get(type_name, FieldType.STRING)

    def _parse_json_schema(self, file_path: Path) -> list[DocumentationEntry]:
        """Parse a JSON schema file."""
        import json

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [self._generate_from_dict(data)]

    def _parse_yaml_schema(self, file_path: Path) -> list[DocumentationEntry]:
        """Parse a YAML schema file."""
        import yaml

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return [self._generate_from_dict(data)]

    def generate_enum_reference(self, enum_cls: type) -> DocumentationEntry:
        """
        Generate reference documentation for an Enum.

        Args:
            enum_cls: Enum class to document

        Returns:
            Documentation entry
        """
        lines = []

        lines.append(f"# {enum_cls.__name__}")
        lines.append("")
        lines.append(enum_cls.__doc__ or "Enumeration type.")
        lines.append("")
        lines.append("## Values")
        lines.append("")
        lines.append("| Name | Value |")
        lines.append("|------|-------|")

        for member in enum_cls:
            lines.append(f"| `{member.name}` | `{member.value}` |")

        content = "\n".join(lines)

        return DocumentationEntry(
            id=self.get_entry_id(enum_cls.__name__),
            title=enum_cls.__name__,
            content=content,
            entry_type="enum",
            tags=["reference", "enum"],
        )

    def generate_constants_reference(
        self,
        constants: dict[str, Any],
        title: str = "Constants"
    ) -> DocumentationEntry:
        """
        Generate reference documentation for constants.

        Args:
            constants: Dictionary of constant names and values
            title: Reference title

        Returns:
            Documentation entry
        """
        lines = []

        lines.append(f"# {title}")
        lines.append("")
        lines.append("## Defined Constants")
        lines.append("")
        lines.append("| Name | Value | Type |")
        lines.append("|------|-------|------|")

        for name, value in constants.items():
            value_type = type(value).__name__
            lines.append(f"| `{name}` | `{value}` | `{value_type}` |")

        content = "\n".join(lines)

        return DocumentationEntry(
            id=self.get_entry_id(title),
            title=title,
            content=content,
            entry_type="constants",
            tags=["reference", "constants"],
        )
