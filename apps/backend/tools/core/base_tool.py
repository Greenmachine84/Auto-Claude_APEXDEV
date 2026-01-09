"""Base tool implementation.

Provides the abstract base class for all tools.

Capabilities:
- Define tool interface
- Input/output validation
- Error handling
- Execution lifecycle
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ToolCategory(Enum):
    """Categories of tools."""

    FILESYSTEM = "filesystem"
    GIT = "git"
    TERMINAL = "terminal"
    WEB = "web"
    SEARCH = "search"
    DATABASE = "database"
    UTILITY = "utility"


class ToolStatus(Enum):
    """Status of tool execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ToolContext:
    """Execution context for tools.

    Provides environment and state for tool execution.
    """

    tool_call_id: str
    parameters: dict[str, Any]
    working_directory: str = "."
    environment: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 60
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Result from tool execution.

    Contains output, status, and metadata from execution.
    """

    tool_name: str
    status: ToolStatus
    output: Any
    error: str | None = None
    execution_time_ms: float = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ToolStatus.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: list[str] | None = None


class BaseTool(ABC):
    """Abstract base class for all tools.

    All tools must inherit from this class and implement:
    - name: Unique tool identifier
    - description: Human-readable description
    - execute: Core execution logic

    Example:
        class MyTool(BaseTool):
            name = "my_tool"
            description = "Does something useful"

            def get_parameters(self) -> List[ToolParameter]:
                return [
                    ToolParameter("input", "string", "The input")
                ]

            async def execute(self, context: ToolContext) -> ToolResult:
                # Implementation
                pass
    """

    # Class-level attributes (override in subclasses)
    name: str = "base_tool"
    description: str = "Base tool"
    category: ToolCategory = ToolCategory.UTILITY
    required_permissions: set[str] = set()
    version: str = "1.0.0"

    def __init__(self):
        """Initialize tool."""
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize tool resources."""
        self._initialized = True

    async def cleanup(self) -> None:
        """Clean up tool resources."""
        self._initialized = False

    @abstractmethod
    def get_parameters(self) -> list[ToolParameter]:
        """Get tool parameter definitions.

        Returns:
            List of parameter definitions
        """
        pass

    def validate_parameters(self, parameters: dict[str, Any]) -> str | None:
        """Validate input parameters.

        Args:
            parameters: Parameters to validate

        Returns:
            Error message if invalid, None if valid
        """
        param_defs = {p.name: p for p in self.get_parameters()}

        # Check required parameters
        for name, param in param_defs.items():
            if param.required and name not in parameters:
                return f"Missing required parameter: {name}"

        # Check unknown parameters
        for name in parameters:
            if name not in param_defs:
                return f"Unknown parameter: {name}"

        return None

    async def run(self, context: ToolContext) -> ToolResult:
        """Run the tool with full lifecycle.

        Handles validation, execution, and error handling.

        Args:
            context: Execution context

        Returns:
            Tool execution result
        """
        start_time = datetime.utcnow()

        try:
            # Validate parameters
            validation_error = self.validate_parameters(context.parameters)
            if validation_error:
                return ToolResult(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    output=None,
                    error=validation_error,
                )

            # Execute tool
            result = await self.execute(context)

            # Calculate execution time
            end_time = datetime.utcnow()
            result.execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return result

        except Exception as e:
            end_time = datetime.utcnow()
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
                execution_time_ms=(end_time - start_time).total_seconds() * 1000,
            )

    @abstractmethod
    async def execute(self, context: ToolContext) -> ToolResult:
        """Execute the tool.

        Override in subclasses to implement tool logic.

        Args:
            context: Execution context with parameters

        Returns:
            Tool execution result
        """
        pass

    def get_schema(self) -> dict[str, Any]:
        """Get JSON schema for this tool.

        Returns:
            JSON schema dictionary
        """
        properties = {}
        required = []

        for param in self.get_parameters():
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default

            properties[param.name] = prop

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

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name!r})"
