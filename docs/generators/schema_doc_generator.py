"""
Schema Documentation Generator - Phase 10 Implementation.

World-Class Standards:
- JSON Schema documentation
- Pydantic model extraction
"""

from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
import json


@dataclass
class SchemaField:
    """Schema field definition."""
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Optional[Any] = None
    examples: List[Any] = field(default_factory=list)


@dataclass
class Schema:
    """Schema definition."""
    name: str
    description: str = ""
    fields: List[SchemaField] = field(default_factory=list)


class SchemaDocGenerator:
    """Generate schema documentation."""

    def __init__(self):
        self.schemas: List[Schema] = []

    def add_schema(self, schema: Schema) -> None:
        """Add schema to documentation."""
        self.schemas.append(schema)

    def extract_from_pydantic(self, model_class: Type) -> Schema:
        """Extract schema from Pydantic model."""
        json_schema = getattr(model_class, "model_json_schema", None)
        if json_schema is None:
            # Fallback for older Pydantic
            json_schema = getattr(model_class, "schema", lambda: {})

        schema_dict = json_schema()
        properties = schema_dict.get("properties", {})
        required_fields = set(schema_dict.get("required", []))

        fields = []
        for field_name, field_info in properties.items():
            fields.append(SchemaField(
                name=field_name,
                type=field_info.get("type", "any"),
                description=field_info.get("description", ""),
                required=field_name in required_fields,
                default=field_info.get("default"),
                examples=field_info.get("examples", []),
            ))

        return Schema(
            name=model_class.__name__,
            description=schema_dict.get("description", model_class.__doc__ or ""),
            fields=fields,
        )

    def generate_json_schema(self, schema: Schema) -> Dict[str, Any]:
        """Generate JSON Schema for a schema."""
        properties = {}
        required = []

        for field in schema.fields:
            properties[field.name] = {
                "type": field.type,
                "description": field.description,
            }
            if field.default is not None:
                properties[field.name]["default"] = field.default
            if field.examples:
                properties[field.name]["examples"] = field.examples
            if field.required:
                required.append(field.name)

        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": schema.name,
            "description": schema.description,
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def generate_markdown(self) -> str:
        """Generate Markdown documentation for all schemas."""
        lines = [
            "# Schema Documentation",
            "",
            "Auto-Claude APEX Development data schemas.",
            "",
        ]

        for schema in self.schemas:
            lines.append(f"## {schema.name}")
            lines.append("")
            if schema.description:
                lines.append(schema.description)
                lines.append("")

            lines.append("| Field | Type | Required | Description |")
            lines.append("|-------|------|----------|-------------|")

            for field in schema.fields:
                required = "Yes" if field.required else "No"
                lines.append(
                    f"| `{field.name}` | `{field.type}` | {required} | "
                    f"{field.description} |"
                )
            lines.append("")

        return "\n".join(lines)

    def export_json_schemas(self, directory: str) -> List[str]:
        """Export all schemas as JSON files."""
        import os
        os.makedirs(directory, exist_ok=True)

        exported = []
        for schema in self.schemas:
            filepath = os.path.join(directory, f"{schema.name}.schema.json")
            json_schema = self.generate_json_schema(schema)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_schema, f, indent=2)
            exported.append(filepath)

        return exported

    def export_markdown(self, filepath: str) -> None:
        """Export schema documentation as Markdown."""
        content = self.generate_markdown()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
