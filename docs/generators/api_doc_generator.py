"""
API Documentation Generator - Phase 10 Implementation.

World-Class Standards:
- OpenAPI 3.1 specification
- Automatic endpoint discovery
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import re


@dataclass
class Endpoint:
    """API endpoint definition."""
    path: str
    method: str
    summary: str
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class APIDocGenerator:
    """Generate API documentation."""

    def __init__(
        self,
        title: str = "Auto-Claude API",
        version: str = "1.0.0",
        base_url: str = "http://localhost:8000",
    ):
        self.title = title
        self.version = version
        self.base_url = base_url
        self.endpoints: List[Endpoint] = []

    def add_endpoint(self, endpoint: Endpoint) -> None:
        """Add endpoint to documentation."""
        self.endpoints.append(endpoint)

    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.1 specification."""
        spec = {
            "openapi": "3.1.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": "Auto-Claude APEX Development API",
            },
            "servers": [
                {"url": self.base_url},
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                    }
                }
            },
        }

        for endpoint in self.endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}

            spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "parameters": endpoint.parameters,
                "responses": endpoint.responses or {
                    "200": {"description": "Success"}
                },
                "tags": endpoint.tags,
            }

            if endpoint.request_body:
                spec["paths"][endpoint.path][endpoint.method.lower()][
                    "requestBody"
                ] = endpoint.request_body

        return spec

    def generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        lines = [
            f"# {self.title}",
            "",
            f"**Version:** {self.version}",
            f"**Base URL:** {self.base_url}",
            "",
            "## Endpoints",
            "",
        ]

        # Group by tags
        tagged_endpoints: Dict[str, List[Endpoint]] = {}
        for endpoint in self.endpoints:
            for tag in endpoint.tags or ["General"]:
                if tag not in tagged_endpoints:
                    tagged_endpoints[tag] = []
                tagged_endpoints[tag].append(endpoint)

        for tag, endpoints in sorted(tagged_endpoints.items()):
            lines.append(f"### {tag}")
            lines.append("")

            for endpoint in endpoints:
                lines.append(f"#### `{endpoint.method} {endpoint.path}`")
                lines.append("")
                lines.append(endpoint.summary)
                lines.append("")

                if endpoint.description:
                    lines.append(endpoint.description)
                    lines.append("")

                if endpoint.parameters:
                    lines.append("**Parameters:**")
                    lines.append("")
                    for param in endpoint.parameters:
                        lines.append(
                            f"- `{param['name']}` ({param.get('in', 'query')}): "
                            f"{param.get('description', '')}"
                        )
                    lines.append("")

        return "\n".join(lines)

    def export_json(self, filepath: str) -> None:
        """Export OpenAPI spec as JSON."""
        spec = self.generate_openapi_spec()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)

    def export_markdown(self, filepath: str) -> None:
        """Export documentation as Markdown."""
        content = self.generate_markdown()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
