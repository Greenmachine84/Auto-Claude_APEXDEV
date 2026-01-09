"""Tool type definitions.

Defines core types for the tools system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolCategory(str, Enum):
    """Tool category classification."""

    FILESYSTEM = "filesystem"
    GIT = "git"
    TERMINAL = "terminal"
    WEB = "web"
    SEARCH = "search"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    UTILITY = "utility"


class ToolCapability(str, Enum):
    """Tool capability flags."""

    # File operations
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    DELETE_FILES = "delete_files"

    # Directory operations
    LIST_DIRS = "list_dirs"
    CREATE_DIRS = "create_dirs"

    # Git operations
    GIT_READ = "git_read"
    GIT_WRITE = "git_write"

    # Terminal operations
    EXEC_COMMANDS = "exec_commands"
    SPAWN_PROCESSES = "spawn_processes"

    # Web operations
    HTTP_REQUESTS = "http_requests"
    WEB_SCRAPE = "web_scrape"

    # Search operations
    CODE_SEARCH = "code_search"
    SEMANTIC_SEARCH = "semantic_search"

    # LLM operations
    LLM_ACCESS = "llm_access"


@dataclass
class ToolMetadata:
    """Metadata about a tool."""

    name: str
    version: str
    description: str
    category: ToolCategory
    capabilities: set[ToolCapability]
    author: str = "Auto-Claude"
    deprecated: bool = False
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category.value,
            "capabilities": [c.value for c in self.capabilities],
            "author": self.author,
            "deprecated": self.deprecated,
            "tags": self.tags,
        }


@dataclass
class ToolParameter:
    """Tool parameter definition."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: list[str] | None = None
    min_value: float | None = None
    max_value: float | None = None
    pattern: str | None = None

    def to_schema(self) -> dict[str, Any]:
        """Convert to JSON schema."""
        schema = {
            "type": self.type,
            "description": self.description,
        }

        if self.default is not None:
            schema["default"] = self.default
        if self.enum:
            schema["enum"] = self.enum
        if self.min_value is not None:
            schema["minimum"] = self.min_value
        if self.max_value is not None:
            schema["maximum"] = self.max_value
        if self.pattern:
            schema["pattern"] = self.pattern

        return schema


@dataclass
class ToolDefinition:
    """Complete tool definition."""

    name: str
    description: str
    category: ToolCategory
    parameters: list[ToolParameter]
    capabilities: set[ToolCapability]
    version: str = "1.0.0"
    deprecated: bool = False

    def to_schema(self) -> dict[str, Any]:
        """Convert to JSON schema."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def get_metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        return ToolMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            category=self.category,
            capabilities=self.capabilities,
            deprecated=self.deprecated,
        )
