"""
Schema parser.

Parses JSON Schema and OpenAPI specifications for documentation.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class SchemaProperty:
    """A property in a schema."""
    name: str
    schema_type: str
    description: str = ""
    required: bool = False
    default: Any = None
    enum: list[Any] = field(default_factory=list)
    format: str = ""
    pattern: str = ""
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    items: Optional["SchemaProperty"] = None
    properties: list["SchemaProperty"] = field(default_factory=list)
    ref: str = ""


@dataclass
class SchemaDefinition:
    """A schema definition."""
    name: str
    schema_type: str
    description: str = ""
    properties: list[SchemaProperty] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    additional_properties: bool = True
    examples: list[Any] = field(default_factory=list)


@dataclass
class ApiOperation:
    """An API operation from OpenAPI spec."""
    path: str
    method: str
    operation_id: str = ""
    summary: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    parameters: list[SchemaProperty] = field(default_factory=list)
    request_body: Optional[SchemaDefinition] = None
    responses: dict[str, SchemaDefinition] = field(default_factory=dict)
    security: list[dict] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class ParsedSchema:
    """Parsed schema result."""
    title: str = ""
    version: str = ""
    description: str = ""
    definitions: list[SchemaDefinition] = field(default_factory=list)
    operations: list[ApiOperation] = field(default_factory=list)
    servers: list[dict] = field(default_factory=list)
    security_schemes: dict[str, dict] = field(default_factory=dict)


class SchemaParser:
    """Parses JSON Schema and OpenAPI specifications."""

    def __init__(self):
        """Initialize parser."""
        self._refs: dict[str, Any] = {}

    def parse_file(self, file_path: Path) -> ParsedSchema:
        """
        Parse a schema file.

        Args:
            file_path: Path to schema file

        Returns:
            Parsed schema
        """
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix == ".json":
                data = json.load(f)
            else:
                import yaml
                data = yaml.safe_load(f)

        return self.parse(data)

    def parse(self, schema: dict) -> ParsedSchema:
        """
        Parse a schema dictionary.

        Args:
            schema: Schema dictionary

        Returns:
            Parsed schema
        """
        result = ParsedSchema()

        # Detect schema type
        if "openapi" in schema or "swagger" in schema:
            return self._parse_openapi(schema)
        elif "$schema" in schema or "type" in schema:
            return self._parse_json_schema(schema)

        return result

    def _parse_openapi(self, schema: dict) -> ParsedSchema:
        """Parse OpenAPI specification."""
        result = ParsedSchema()

        # Info
        info = schema.get("info", {})
        result.title = info.get("title", "")
        result.version = info.get("version", "")
        result.description = info.get("description", "")

        # Servers
        result.servers = schema.get("servers", [])

        # Store refs for resolution
        self._refs = {}
        components = schema.get("components", {})
        for name, definition in components.get("schemas", {}).items():
            self._refs[f"#/components/schemas/{name}"] = definition

        # Parse component schemas
        for name, definition in components.get("schemas", {}).items():
            result.definitions.append(self._parse_schema_definition(name, definition))

        # Security schemes
        result.security_schemes = components.get("securitySchemes", {})

        # Parse paths
        for path, methods in schema.get("paths", {}).items():
            for method, operation in methods.items():
                if method in ("get", "post", "put", "patch", "delete", "options", "head"):
                    result.operations.append(self._parse_operation(path, method, operation))

        return result

    def _parse_json_schema(self, schema: dict) -> ParsedSchema:
        """Parse JSON Schema."""
        result = ParsedSchema()

        result.title = schema.get("title", "")
        result.description = schema.get("description", "")

        # Parse definitions
        for name, definition in schema.get("definitions", {}).items():
            result.definitions.append(self._parse_schema_definition(name, definition))

        # Parse root schema as definition
        if "type" in schema or "properties" in schema:
            root_def = self._parse_schema_definition(
                schema.get("title", "Root"),
                schema
            )
            result.definitions.insert(0, root_def)

        return result

    def _parse_schema_definition(self, name: str, schema: dict) -> SchemaDefinition:
        """Parse a schema definition."""
        definition = SchemaDefinition(
            name=name,
            schema_type=schema.get("type", "object"),
            description=schema.get("description", ""),
            required=schema.get("required", []),
            additional_properties=schema.get("additionalProperties", True),
            examples=schema.get("examples", []),
        )

        # Parse properties
        for prop_name, prop_schema in schema.get("properties", {}).items():
            prop = self._parse_property(prop_name, prop_schema)
            prop.required = prop_name in definition.required
            definition.properties.append(prop)

        return definition

    def _parse_property(self, name: str, schema: dict) -> SchemaProperty:
        """Parse a schema property."""
        prop = SchemaProperty(
            name=name,
            schema_type=schema.get("type", "any"),
            description=schema.get("description", ""),
            default=schema.get("default"),
            enum=schema.get("enum", []),
            format=schema.get("format", ""),
            pattern=schema.get("pattern", ""),
            minimum=schema.get("minimum"),
            maximum=schema.get("maximum"),
            min_length=schema.get("minLength"),
            max_length=schema.get("maxLength"),
        )

        # Handle $ref
        if "$ref" in schema:
            prop.ref = schema["$ref"]
            ref_schema = self._resolve_ref(schema["$ref"])
            if ref_schema:
                prop.schema_type = ref_schema.get("type", "object")

        # Handle array items
        if prop.schema_type == "array" and "items" in schema:
            prop.items = self._parse_property("items", schema["items"])

        # Handle nested properties
        if "properties" in schema:
            for sub_name, sub_schema in schema["properties"].items():
                prop.properties.append(self._parse_property(sub_name, sub_schema))

        return prop

    def _parse_operation(self, path: str, method: str, operation: dict) -> ApiOperation:
        """Parse an API operation."""
        op = ApiOperation(
            path=path,
            method=method.upper(),
            operation_id=operation.get("operationId", ""),
            summary=operation.get("summary", ""),
            description=operation.get("description", ""),
            tags=operation.get("tags", []),
            security=operation.get("security", []),
            deprecated=operation.get("deprecated", False),
        )

        # Parse parameters
        for param in operation.get("parameters", []):
            op.parameters.append(self._parse_parameter(param))

        # Parse request body
        if "requestBody" in operation:
            op.request_body = self._parse_request_body(operation["requestBody"])

        # Parse responses
        for status, response in operation.get("responses", {}).items():
            op.responses[status] = self._parse_response(response)

        return op

    def _parse_parameter(self, param: dict) -> SchemaProperty:
        """Parse an API parameter."""
        schema = param.get("schema", {})
        return SchemaProperty(
            name=param.get("name", ""),
            schema_type=schema.get("type", "string"),
            description=param.get("description", ""),
            required=param.get("required", False),
            default=schema.get("default"),
            enum=schema.get("enum", []),
            format=schema.get("format", ""),
        )

    def _parse_request_body(self, body: dict) -> SchemaDefinition:
        """Parse request body."""
        content = body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        return self._parse_schema_definition("RequestBody", schema)

    def _parse_response(self, response: dict) -> SchemaDefinition:
        """Parse response."""
        content = response.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        definition = self._parse_schema_definition("Response", schema)
        definition.description = response.get("description", "")

        return definition

    def _resolve_ref(self, ref: str) -> Optional[dict]:
        """Resolve a $ref reference."""
        return self._refs.get(ref)

    def to_markdown(self, parsed: ParsedSchema) -> str:
        """
        Convert parsed schema to Markdown.

        Args:
            parsed: Parsed schema

        Returns:
            Markdown documentation
        """
        lines = []

        # Title
        lines.append(f"# {parsed.title}")
        lines.append("")
        if parsed.version:
            lines.append(f"**Version:** {parsed.version}")
            lines.append("")
        if parsed.description:
            lines.append(parsed.description)
            lines.append("")

        # Servers
        if parsed.servers:
            lines.append("## Servers")
            lines.append("")
            for server in parsed.servers:
                lines.append(f"- **{server.get('url', '')}** - {server.get('description', '')}")
            lines.append("")

        # Schemas
        if parsed.definitions:
            lines.append("## Schemas")
            lines.append("")
            for definition in parsed.definitions:
                lines.append(f"### {definition.name}")
                lines.append("")
                if definition.description:
                    lines.append(definition.description)
                    lines.append("")

                if definition.properties:
                    lines.append("| Property | Type | Required | Description |")
                    lines.append("|----------|------|----------|-------------|")
                    for prop in definition.properties:
                        req = "Yes" if prop.required else "No"
                        lines.append(f"| `{prop.name}` | `{prop.schema_type}` | {req} | {prop.description} |")
                    lines.append("")

        # Operations
        if parsed.operations:
            lines.append("## Endpoints")
            lines.append("")
            for op in parsed.operations:
                lines.append(f"### {op.method} {op.path}")
                lines.append("")
                if op.deprecated:
                    lines.append("> ⚠️ **Deprecated**")
                    lines.append("")
                if op.summary:
                    lines.append(f"**{op.summary}**")
                    lines.append("")
                if op.description:
                    lines.append(op.description)
                    lines.append("")

        return "\n".join(lines)
