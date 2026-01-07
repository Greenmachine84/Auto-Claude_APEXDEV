"""
Documentation data models.

Provides data models for documentation entities including
entries, endpoints, examples, and cross-references.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class Visibility(Enum):
    """Visibility levels for documentation."""
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"


class HttpMethod(Enum):
    """HTTP methods for API endpoints."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ParameterLocation(Enum):
    """Parameter locations for API endpoints."""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"


class ExampleType(Enum):
    """Types of code examples."""
    BASIC = "basic"
    ADVANCED = "advanced"
    ERROR_HANDLING = "error_handling"
    INTEGRATION = "integration"


@dataclass
class Parameter:
    """API parameter definition."""
    name: str
    type: str
    description: str = ""
    location: ParameterLocation = ParameterLocation.BODY
    required: bool = False
    default: Any = None
    examples: list[Any] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    """API response definition."""
    status_code: int
    description: str
    content_type: str = "application/json"
    schema: Optional[dict] = None
    examples: list[dict] = field(default_factory=list)


@dataclass
class CodeExample:
    """Code example in documentation."""
    id: str
    title: str
    code: str
    language: str = "python"
    description: str = ""
    example_type: ExampleType = ExampleType.BASIC
    output: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = []
        if self.title:
            lines.append(f"### {self.title}")
        if self.description:
            lines.append(f"\n{self.description}\n")
        lines.append(f"```{self.language}")
        lines.append(self.code)
        lines.append("```")
        if self.output:
            lines.append("\n**Output:**")
            lines.append("```")
            lines.append(self.output)
            lines.append("```")
        return "\n".join(lines)


@dataclass
class CrossReference:
    """Cross-reference to another documentation entry."""
    target_id: str
    target_title: str
    reference_type: str = "see_also"
    description: str = ""
    url: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert to Markdown link."""
        if self.url:
            return f"[{self.target_title}]({self.url})"
        return f"[{self.target_title}](#{self.target_id})"


@dataclass
class ApiEndpoint:
    """API endpoint documentation."""
    id: str
    path: str
    method: HttpMethod
    summary: str
    description: str = ""
    parameters: list[Parameter] = field(default_factory=list)
    request_body: Optional[dict] = None
    responses: list[Response] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    deprecated: bool = False
    security: list[str] = field(default_factory=list)
    examples: list[CodeExample] = field(default_factory=list)
    rate_limit: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = []

        # Header
        lines.append(f"## {self.method.value} {self.path}")
        lines.append("")

        if self.deprecated:
            lines.append("> ⚠️ **Deprecated**: This endpoint is deprecated.")
            lines.append("")

        lines.append(f"**{self.summary}**")
        lines.append("")

        if self.description:
            lines.append(self.description)
            lines.append("")

        # Parameters
        if self.parameters:
            lines.append("### Parameters")
            lines.append("")
            lines.append("| Name | Type | Location | Required | Description |")
            lines.append("|------|------|----------|----------|-------------|")
            for param in self.parameters:
                req = "Yes" if param.required else "No"
                lines.append(
                    f"| `{param.name}` | `{param.type}` | "
                    f"{param.location.value} | {req} | {param.description} |"
                )
            lines.append("")

        # Responses
        if self.responses:
            lines.append("### Responses")
            lines.append("")
            for resp in self.responses:
                lines.append(f"**{resp.status_code}**: {resp.description}")
                lines.append("")

        # Examples
        if self.examples:
            lines.append("### Examples")
            lines.append("")
            for example in self.examples:
                lines.append(example.to_markdown())
                lines.append("")

        return "\n".join(lines)


@dataclass
class DocumentationEntry:
    """A documentation entry (page or section)."""
    id: str
    title: str
    content: str
    entry_type: str = "page"
    visibility: Visibility = Visibility.PUBLIC
    source_file: Optional[Path] = None
    source_line: Optional[int] = None
    parent_id: Optional[str] = None
    children: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    examples: list[CodeExample] = field(default_factory=list)
    cross_refs: list[CrossReference] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "entry_type": self.entry_type,
            "visibility": self.visibility.value,
            "source_file": str(self.source_file) if self.source_file else None,
            "source_line": self.source_line,
            "parent_id": self.parent_id,
            "children": self.children,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = []

        # Title
        lines.append(f"# {self.title}")
        lines.append("")

        # Metadata
        if self.tags:
            lines.append(f"**Tags:** {', '.join(self.tags)}")
            lines.append("")

        # Content
        lines.append(self.content)
        lines.append("")

        # Examples
        if self.examples:
            lines.append("## Examples")
            lines.append("")
            for example in self.examples:
                lines.append(example.to_markdown())
                lines.append("")

        # Cross-references
        if self.cross_refs:
            lines.append("## See Also")
            lines.append("")
            for ref in self.cross_refs:
                lines.append(f"- {ref.to_markdown()}")
            lines.append("")

        return "\n".join(lines)


@dataclass
class DocumentationIndex:
    """Index of all documentation entries."""
    entries: dict[str, DocumentationEntry] = field(default_factory=dict)
    categories: dict[str, list[str]] = field(default_factory=dict)
    tags: dict[str, list[str]] = field(default_factory=dict)
    version: str = "1.0.0"
    generated_at: datetime = field(default_factory=datetime.now)

    def add_entry(self, entry: DocumentationEntry) -> None:
        """Add an entry to the index."""
        self.entries[entry.id] = entry

        # Index by type
        if entry.entry_type not in self.categories:
            self.categories[entry.entry_type] = []
        self.categories[entry.entry_type].append(entry.id)

        # Index by tags
        for tag in entry.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(entry.id)

    def get_by_tag(self, tag: str) -> list[DocumentationEntry]:
        """Get entries by tag."""
        entry_ids = self.tags.get(tag, [])
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]

    def get_by_category(self, category: str) -> list[DocumentationEntry]:
        """Get entries by category."""
        entry_ids = self.categories.get(category, [])
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]

    def search(self, query: str) -> list[DocumentationEntry]:
        """Search entries by title or content."""
        query_lower = query.lower()
        results = []
        for entry in self.entries.values():
            if (query_lower in entry.title.lower() or
                query_lower in entry.content.lower()):
                results.append(entry)
        return results
