"""
Mock tools for testing.

Provides mock implementations of tool types with configurable
execution behavior, validation, and sandboxing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import asyncio


class ToolType(Enum):
    """Tool types."""
    FILE_SYSTEM = "file_system"
    SEARCH = "search"
    CODE = "code"
    WEB = "web"
    DATABASE = "database"
    SHELL = "shell"


class ToolStatus(Enum):
    """Tool execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PermissionLevel(Enum):
    """Tool permission levels."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class ToolDefinition:
    """Tool definition."""
    name: str
    description: str
    tool_type: ToolType
    parameters: dict = field(default_factory=dict)
    required_permissions: list[PermissionLevel] = field(default_factory=list)
    timeout: float = 30.0
    sandboxed: bool = False


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


class MockTool:
    """Base mock tool implementation."""

    def __init__(self, definition: ToolDefinition):
        self.definition = definition
        self.name = definition.name
        self.tool_type = definition.tool_type
        self._handler: Optional[Callable] = None
        self._responses: dict[str, Any] = {}
        self._error_mode = False
        self._error: Optional[Exception] = None
        self.execution_count = 0
        self.execution_history: list[dict] = []

    def set_handler(self, handler: Callable) -> None:
        """Set execution handler."""
        self._handler = handler

    def set_response(self, input_key: str, response: Any) -> None:
        """Set canned response for input."""
        self._responses[input_key] = response

    def set_error(self, error: Exception) -> None:
        """Set error mode."""
        self._error_mode = True
        self._error = error

    def clear_error(self) -> None:
        """Clear error mode."""
        self._error_mode = False
        self._error = None

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        import time
        start = time.time()
        self.execution_count += 1

        record = {
            "tool": self.name,
            "input": kwargs,
            "timestamp": datetime.now().isoformat()
        }

        try:
            if self._error_mode and self._error:
                raise self._error

            # Check canned responses
            for key, response in self._responses.items():
                if key in str(kwargs):
                    output = response
                    break
            else:
                # Use handler or default
                if self._handler:
                    output = await self._handler(**kwargs)
                else:
                    output = f"Executed {self.name} with {kwargs}"

            duration = (time.time() - start) * 1000
            record["success"] = True
            record["output"] = output
            self.execution_history.append(record)

            return ToolResult(
                success=True,
                output=output,
                duration_ms=duration
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            record["success"] = False
            record["error"] = str(e)
            self.execution_history.append(record)

            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate input parameters."""
        params = self.definition.parameters
        required = params.get("required", [])

        for req in required:
            if req not in kwargs:
                return False, f"Missing required parameter: {req}"

        return True, None


class MockSandboxedTool(MockTool):
    """Mock tool with sandboxing support."""

    def __init__(self, definition: ToolDefinition):
        definition.sandboxed = True
        super().__init__(definition)
        self._sandbox_violations: list[str] = []
        self._allowed_paths: list[str] = []

    def set_allowed_paths(self, paths: list[str]) -> None:
        """Set allowed file paths."""
        self._allowed_paths = paths

    async def execute(self, **kwargs) -> ToolResult:
        """Execute with sandbox checks."""
        # Check sandbox rules
        path = kwargs.get("path", "")
        if path and self._allowed_paths:
            allowed = any(path.startswith(p) for p in self._allowed_paths)
            if not allowed:
                self._sandbox_violations.append(path)
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Sandbox violation: {path} not allowed"
                )

        return await super().execute(**kwargs)

    def get_violations(self) -> list[str]:
        """Get sandbox violations."""
        return self._sandbox_violations.copy()


class MockToolRegistry:
    """Registry for mock tools."""

    def __init__(self):
        self._tools: dict[str, MockTool] = {}
        self._type_index: dict[ToolType, list[str]] = {t: [] for t in ToolType}

    def register(self, tool: MockTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self._type_index[tool.tool_type].append(tool.name)

    def get(self, name: str) -> Optional[MockTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_by_type(self, tool_type: ToolType) -> list[MockTool]:
        """Get tools by type."""
        names = self._type_index.get(tool_type, [])
        return [self._tools[n] for n in names if n in self._tools]

    def list_all(self) -> list[str]:
        """List all tool names."""
        return list(self._tools.keys())

    def clear(self) -> None:
        """Clear all tools."""
        self._tools.clear()
        self._type_index = {t: [] for t in ToolType}


class MockToolExecutor:
    """Executor for running tools."""

    def __init__(self, registry: MockToolRegistry):
        self.registry = registry
        self._permissions: dict[str, list[PermissionLevel]] = {}
        self._execution_log: list[dict] = []
        self._concurrent_limit = 5
        self._semaphore: Optional[asyncio.Semaphore] = None

    def set_permissions(
        self,
        user_id: str,
        permissions: list[PermissionLevel]
    ) -> None:
        """Set user permissions."""
        self._permissions[user_id] = permissions

    def set_concurrent_limit(self, limit: int) -> None:
        """Set concurrent execution limit."""
        self._concurrent_limit = limit
        self._semaphore = asyncio.Semaphore(limit)

    def check_permission(
        self,
        user_id: str,
        tool: MockTool
    ) -> bool:
        """Check if user has permission for tool."""
        user_perms = set(self._permissions.get(user_id, []))
        required = set(tool.definition.required_permissions)
        return required.issubset(user_perms)

    async def execute(
        self,
        tool_name: str,
        user_id: str,
        **kwargs
    ) -> ToolResult:
        """Execute a tool."""
        tool = self.registry.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool not found: {tool_name}"
            )

        # Permission check
        if not self.check_permission(user_id, tool):
            return ToolResult(
                success=False,
                output=None,
                error="Permission denied"
            )

        # Validation
        valid, error = tool.validate_input(**kwargs)
        if not valid:
            return ToolResult(
                success=False,
                output=None,
                error=error
            )

        # Execute with concurrency control
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._concurrent_limit)

        async with self._semaphore:
            result = await tool.execute(**kwargs)

        self._execution_log.append({
            "tool": tool_name,
            "user": user_id,
            "success": result.success,
            "timestamp": datetime.now().isoformat()
        })

        return result

    async def execute_batch(
        self,
        executions: list[dict],
        user_id: str
    ) -> list[ToolResult]:
        """Execute multiple tools."""
        tasks = [
            self.execute(ex["tool"], user_id, **ex.get("kwargs", {}))
            for ex in executions
        ]
        return await asyncio.gather(*tasks)

    def get_execution_log(self) -> list[dict]:
        """Get execution log."""
        return self._execution_log.copy()


# Factory functions
def create_file_tool() -> MockTool:
    """Create a file system tool."""
    definition = ToolDefinition(
        name="read_file",
        description="Read file contents",
        tool_type=ToolType.FILE_SYSTEM,
        parameters={
            "required": ["path"],
            "properties": {"path": {"type": "string"}}
        },
        required_permissions=[PermissionLevel.READ]
    )
    tool = MockTool(definition)
    tool.set_response("test.txt", "Test file content")
    return tool


def create_search_tool() -> MockTool:
    """Create a search tool."""
    definition = ToolDefinition(
        name="search",
        description="Search for information",
        tool_type=ToolType.SEARCH,
        parameters={
            "required": ["query"],
            "properties": {"query": {"type": "string"}}
        }
    )
    tool = MockTool(definition)
    tool.set_response("python", [{"title": "Python docs", "url": "python.org"}])
    return tool


def create_shell_tool() -> MockSandboxedTool:
    """Create a sandboxed shell tool."""
    definition = ToolDefinition(
        name="shell",
        description="Execute shell commands",
        tool_type=ToolType.SHELL,
        parameters={
            "required": ["command"],
            "properties": {"command": {"type": "string"}}
        },
        required_permissions=[PermissionLevel.EXECUTE],
        sandboxed=True
    )
    return MockSandboxedTool(definition)
