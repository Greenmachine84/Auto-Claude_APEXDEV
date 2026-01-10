"""API documentation generation skill.

Generates API documentation.

Capabilities:
- Generate OpenAPI/Swagger docs
- Document REST endpoints
- Create API references
- Support multiple output formats
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from skills.core.base_skill import (
    BaseSkill,
    SkillCategory,
    SkillContext,
    SkillResult,
    SkillStatus,
)


class ApiDocFormat(Enum):
    """Supported API doc formats."""

    OPENAPI = "openapi"
    SWAGGER = "swagger"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class ApiEndpoint:
    """An API endpoint."""

    path: str
    method: str
    summary: str
    description: str
    parameters: list[dict[str, Any]] = field(default_factory=list)
    request_body: dict[str, Any] | None = None
    responses: dict[str, dict[str, Any]] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


class ApiDocGenerationSkill(BaseSkill):
    """Generate API documentation.

    Analyzes API code and generates comprehensive documentation
    in various formats including OpenAPI.

    Example:
        skill = ApiDocGenerationSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "@app.get('/users')...",
                "format": "openapi",
            }
        )
        result = await skill.run(context)
    """

    name = "api_doc_generation"
    description = "Generate API documentation"
    category = SkillCategory.DOCUMENTATION
    required_tools = ["file_read"]
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data and "files" not in input_data:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute API documentation generation.

        Args:
            context: Execution context with API code

        Returns:
            SkillResult with generated docs
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        format_str = input_data.get("format", "openapi")
        doc_format = ApiDocFormat(format_str)
        title = input_data.get("title", "API Documentation")
        version = input_data.get("version", "1.0.0")

        # Extract endpoints from code
        endpoints = self._extract_endpoints(code)

        # Generate documentation
        if doc_format == ApiDocFormat.OPENAPI:
            docs = self._generate_openapi(title, version, endpoints)
        else:
            docs = self._generate_markdown(title, endpoints)

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "documentation": docs,
                "format": doc_format.value,
                "endpoint_count": len(endpoints),
                "endpoints": [self._endpoint_to_dict(e) for e in endpoints],
            },
            tokens_used=0,
        )

    def _extract_endpoints(self, code: str) -> list[ApiEndpoint]:
        """Extract API endpoints from code."""
        endpoints = []
        # Placeholder - will parse decorators
        return endpoints

    def _generate_openapi(
        self,
        title: str,
        version: str,
        endpoints: list[ApiEndpoint],
    ) -> dict[str, Any]:
        """Generate OpenAPI spec."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
            },
            "paths": {},
        }

        for endpoint in endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}

            spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "parameters": endpoint.parameters,
                "responses": endpoint.responses or {"200": {"description": "Success"}},
            }

        return spec

    def _generate_markdown(self, title: str, endpoints: list[ApiEndpoint]) -> str:
        """Generate Markdown documentation."""
        lines = [f"# {title}\n"]

        for endpoint in endpoints:
            lines.append(f"\n## {endpoint.method.upper()} {endpoint.path}\n")
            lines.append(f"{endpoint.description}\n")

        return "\n".join(lines)

    def _endpoint_to_dict(self, endpoint: ApiEndpoint) -> dict[str, Any]:
        """Convert ApiEndpoint to dictionary."""
        return {
            "path": endpoint.path,
            "method": endpoint.method,
            "summary": endpoint.summary,
            "tags": endpoint.tags,
        }
