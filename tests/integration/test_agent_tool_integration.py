"""
Integration tests for Agent-Tool interactions.

Tests the complete flow of agents using tools, including tool discovery,
execution, validation, and result handling.
"""

import pytest
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable
from unittest.mock import AsyncMock, MagicMock


class ToolType(Enum):
    """Types of tools available to agents."""
    FILE_SYSTEM = "file_system"
    CODE_EXECUTION = "code_execution"
    WEB_SEARCH = "web_search"
    DATABASE = "database"
    API_CALL = "api_call"
    SHELL = "shell"


class AgentType(Enum):
    """Agent types for tool integration testing."""
    CODER = "coder"
    REVIEWER = "reviewer"
    FIXER = "fixer"
    RESEARCHER = "researcher"


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolCall:
    """Represents a tool call request."""
    tool_name: str
    tool_type: ToolType
    parameters: dict
    timeout_seconds: float = 30.0


class MockTool:
    """Mock tool for integration testing."""

    def __init__(self, name: str, tool_type: ToolType):
        self.name = name
        self.tool_type = tool_type
        self.call_count = 0
        self.last_params: dict = {}
        self._results: list[ToolResult] = []
        self._should_fail = False
        self._validator: Optional[Callable[[dict], bool]] = None

    def set_results(self, results: list[ToolResult]) -> None:
        """Set predefined results."""
        self._results = results.copy()

    def set_failure_mode(self, should_fail: bool) -> None:
        """Configure failure behavior."""
        self._should_fail = should_fail

    def set_validator(self, validator: Callable[[dict], bool]) -> None:
        """Set parameter validator."""
        self._validator = validator

    def validate_params(self, params: dict) -> bool:
        """Validate parameters."""
        if self._validator:
            return self._validator(params)
        return True

    async def execute(self, params: dict) -> ToolResult:
        """Execute the tool."""
        self.call_count += 1
        self.last_params = params

        if not self.validate_params(params):
            return ToolResult(
                success=False,
                output=None,
                error="Parameter validation failed"
            )

        if self._should_fail:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool {self.name} execution failed"
            )

        if self._results:
            return self._results.pop(0)

        return ToolResult(
            success=True,
            output=f"Default output from {self.name}",
            execution_time_ms=10.0
        )


class MockToolRegistry:
    """Registry for tools available to agents."""

    def __init__(self):
        self._tools: dict[str, MockTool] = {}
        self._type_index: dict[ToolType, list[str]] = {}

    def register(self, tool: MockTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        if tool.tool_type not in self._type_index:
            self._type_index[tool.tool_type] = []
        self._type_index[tool.tool_type].append(tool.name)

    def get(self, name: str) -> MockTool:
        """Get a tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool {name} not found")
        return self._tools[name]

    def get_by_type(self, tool_type: ToolType) -> list[MockTool]:
        """Get all tools of a specific type."""
        names = self._type_index.get(tool_type, [])
        return [self._tools[name] for name in names]

    def list_all(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


class MockToolExecutor:
    """Executor for running tools with sandboxing and validation."""

    def __init__(self, registry: MockToolRegistry):
        self.registry = registry
        self.execution_history: list[tuple[str, dict, ToolResult]] = []
        self._sandbox_enabled = True
        self._max_concurrent = 5
        self._current_concurrent = 0

    def enable_sandbox(self, enabled: bool) -> None:
        """Enable or disable sandbox mode."""
        self._sandbox_enabled = enabled

    async def execute(self, call: ToolCall) -> ToolResult:
        """Execute a tool call."""
        if self._current_concurrent >= self._max_concurrent:
            return ToolResult(
                success=False,
                output=None,
                error="Max concurrent executions reached"
            )

        self._current_concurrent += 1
        try:
            tool = self.registry.get(call.tool_name)

            # Sandbox check
            if self._sandbox_enabled and tool.tool_type == ToolType.SHELL:
                return ToolResult(
                    success=False,
                    output=None,
                    error="Shell execution blocked in sandbox mode"
                )

            result = await tool.execute(call.parameters)
            self.execution_history.append((call.tool_name, call.parameters, result))
            return result
        except KeyError as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )
        finally:
            self._current_concurrent -= 1

    async def execute_batch(self, calls: list[ToolCall]) -> list[ToolResult]:
        """Execute multiple tool calls."""
        results = []
        for call in calls:
            result = await self.execute(call)
            results.append(result)
        return results


class MockAgentWithTools:
    """Mock agent that can use tools."""

    def __init__(self, agent_type: AgentType, executor: MockToolExecutor):
        self.agent_type = agent_type
        self.executor = executor
        self.tool_calls_made: list[ToolCall] = []
        self._tool_permissions: set[ToolType] = set()

    def grant_permission(self, tool_type: ToolType) -> None:
        """Grant permission to use a tool type."""
        self._tool_permissions.add(tool_type)

    def revoke_permission(self, tool_type: ToolType) -> None:
        """Revoke permission for a tool type."""
        self._tool_permissions.discard(tool_type)

    def has_permission(self, tool_type: ToolType) -> bool:
        """Check if agent has permission for tool type."""
        return tool_type in self._tool_permissions

    async def use_tool(self, call: ToolCall) -> ToolResult:
        """Use a tool if permitted."""
        if not self.has_permission(call.tool_type):
            return ToolResult(
                success=False,
                output=None,
                error=f"No permission to use {call.tool_type.value} tools"
            )

        self.tool_calls_made.append(call)
        return await self.executor.execute(call)

    async def discover_tools(self) -> list[str]:
        """Discover available tools based on permissions."""
        available = []
        for tool_type in self._tool_permissions:
            tools = self.executor.registry.get_by_type(tool_type)
            available.extend([t.name for t in tools])
        return available


# ============================================================================
# Test Classes
# ============================================================================

class TestToolDiscovery:
    """Tests for agent tool discovery."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create tool registry with various tools."""
        registry = MockToolRegistry()
        registry.register(MockTool("read_file", ToolType.FILE_SYSTEM))
        registry.register(MockTool("write_file", ToolType.FILE_SYSTEM))
        registry.register(MockTool("run_python", ToolType.CODE_EXECUTION))
        registry.register(MockTool("search_web", ToolType.WEB_SEARCH))
        registry.register(MockTool("run_shell", ToolType.SHELL))
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create tool executor."""
        return MockToolExecutor(registry)

    @pytest.fixture
    def agent(self, executor: MockToolExecutor) -> MockAgentWithTools:
        """Create agent with tools."""
        return MockAgentWithTools(AgentType.CODER, executor)

    def test_discover_no_tools_without_permission(self, agent: MockAgentWithTools):
        """Test agent discovers no tools without permissions."""
        import asyncio
        tools = asyncio.get_event_loop().run_until_complete(agent.discover_tools())
        assert len(tools) == 0

    @pytest.mark.asyncio
    async def test_discover_permitted_tools(self, agent: MockAgentWithTools):
        """Test agent discovers only permitted tools."""
        agent.grant_permission(ToolType.FILE_SYSTEM)
        tools = await agent.discover_tools()

        assert "read_file" in tools
        assert "write_file" in tools
        assert "run_shell" not in tools

    @pytest.mark.asyncio
    async def test_discover_multiple_tool_types(self, agent: MockAgentWithTools):
        """Test discovering multiple tool types."""
        agent.grant_permission(ToolType.FILE_SYSTEM)
        agent.grant_permission(ToolType.CODE_EXECUTION)
        tools = await agent.discover_tools()

        assert len(tools) == 3
        assert "run_python" in tools


class TestToolExecution:
    """Tests for tool execution through agents."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create tool registry."""
        registry = MockToolRegistry()
        registry.register(MockTool("read_file", ToolType.FILE_SYSTEM))
        registry.register(MockTool("run_python", ToolType.CODE_EXECUTION))
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create tool executor."""
        return MockToolExecutor(registry)

    @pytest.fixture
    def agent(self, executor: MockToolExecutor) -> MockAgentWithTools:
        """Create agent with permissions."""
        agent = MockAgentWithTools(AgentType.CODER, executor)
        agent.grant_permission(ToolType.FILE_SYSTEM)
        agent.grant_permission(ToolType.CODE_EXECUTION)
        return agent

    @pytest.mark.asyncio
    async def test_successful_tool_execution(self, agent: MockAgentWithTools):
        """Test successful tool execution."""
        call = ToolCall(
            tool_name="read_file",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"path": "/test/file.txt"}
        )

        result = await agent.use_tool(call)
        assert result.success is True
        assert len(agent.tool_calls_made) == 1

    @pytest.mark.asyncio
    async def test_tool_execution_without_permission(self, agent: MockAgentWithTools):
        """Test tool execution fails without permission."""
        agent.revoke_permission(ToolType.FILE_SYSTEM)

        call = ToolCall(
            tool_name="read_file",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"path": "/test/file.txt"}
        )

        result = await agent.use_tool(call)
        assert result.success is False
        assert "permission" in result.error.lower()

    @pytest.mark.asyncio
    async def test_tool_not_found(self, agent: MockAgentWithTools):
        """Test execution of non-existent tool."""
        call = ToolCall(
            tool_name="unknown_tool",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={}
        )

        result = await agent.use_tool(call)
        assert result.success is False


class TestSandboxing:
    """Tests for tool sandboxing."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create registry with shell tool."""
        registry = MockToolRegistry()
        registry.register(MockTool("run_shell", ToolType.SHELL))
        registry.register(MockTool("read_file", ToolType.FILE_SYSTEM))
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create sandboxed executor."""
        executor = MockToolExecutor(registry)
        executor.enable_sandbox(True)
        return executor

    @pytest.fixture
    def agent(self, executor: MockToolExecutor) -> MockAgentWithTools:
        """Create agent with all permissions."""
        agent = MockAgentWithTools(AgentType.CODER, executor)
        agent.grant_permission(ToolType.SHELL)
        agent.grant_permission(ToolType.FILE_SYSTEM)
        return agent

    @pytest.mark.asyncio
    async def test_shell_blocked_in_sandbox(self, agent: MockAgentWithTools):
        """Test shell commands blocked in sandbox mode."""
        call = ToolCall(
            tool_name="run_shell",
            tool_type=ToolType.SHELL,
            parameters={"command": "rm -rf /"}
        )

        result = await agent.use_tool(call)
        assert result.success is False
        assert "sandbox" in result.error.lower()

    @pytest.mark.asyncio
    async def test_file_access_allowed_in_sandbox(self, agent: MockAgentWithTools):
        """Test file access works in sandbox."""
        call = ToolCall(
            tool_name="read_file",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"path": "/safe/file.txt"}
        )

        result = await agent.use_tool(call)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_sandbox_can_be_disabled(
        self,
        agent: MockAgentWithTools,
        executor: MockToolExecutor
    ):
        """Test sandbox can be disabled for privileged operations."""
        executor.enable_sandbox(False)

        call = ToolCall(
            tool_name="run_shell",
            tool_type=ToolType.SHELL,
            parameters={"command": "echo hello"}
        )

        result = await agent.use_tool(call)
        assert result.success is True


class TestToolValidation:
    """Tests for tool parameter validation."""

    @pytest.fixture
    def tool_with_validator(self) -> MockTool:
        """Create tool with validator."""
        tool = MockTool("validated_tool", ToolType.FILE_SYSTEM)
        tool.set_validator(lambda p: "path" in p and p["path"].startswith("/"))
        return tool

    @pytest.fixture
    def registry(self, tool_with_validator: MockTool) -> MockToolRegistry:
        """Create registry with validated tool."""
        registry = MockToolRegistry()
        registry.register(tool_with_validator)
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create executor."""
        return MockToolExecutor(registry)

    @pytest.fixture
    def agent(self, executor: MockToolExecutor) -> MockAgentWithTools:
        """Create agent."""
        agent = MockAgentWithTools(AgentType.CODER, executor)
        agent.grant_permission(ToolType.FILE_SYSTEM)
        return agent

    @pytest.mark.asyncio
    async def test_valid_parameters_accepted(self, agent: MockAgentWithTools):
        """Test valid parameters are accepted."""
        call = ToolCall(
            tool_name="validated_tool",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"path": "/valid/path"}
        )

        result = await agent.use_tool(call)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_invalid_parameters_rejected(self, agent: MockAgentWithTools):
        """Test invalid parameters are rejected."""
        call = ToolCall(
            tool_name="validated_tool",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"path": "relative/path"}
        )

        result = await agent.use_tool(call)
        assert result.success is False
        assert "validation" in result.error.lower()


class TestBatchExecution:
    """Tests for batch tool execution."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create registry with multiple tools."""
        registry = MockToolRegistry()
        for i in range(5):
            registry.register(MockTool(f"tool_{i}", ToolType.FILE_SYSTEM))
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create executor."""
        return MockToolExecutor(registry)

    @pytest.mark.asyncio
    async def test_batch_execution(self, executor: MockToolExecutor):
        """Test batch execution of multiple tools."""
        calls = [
            ToolCall(tool_name=f"tool_{i}", tool_type=ToolType.FILE_SYSTEM, parameters={})
            for i in range(3)
        ]

        results = await executor.execute_batch(calls)
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_batch_partial_failure(
        self,
        executor: MockToolExecutor,
        registry: MockToolRegistry
    ):
        """Test batch execution with partial failures."""
        registry.get("tool_1").set_failure_mode(True)

        calls = [
            ToolCall(tool_name=f"tool_{i}", tool_type=ToolType.FILE_SYSTEM, parameters={})
            for i in range(3)
        ]

        results = await executor.execute_batch(calls)
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True


class TestExecutionHistory:
    """Tests for tool execution history tracking."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create registry."""
        registry = MockToolRegistry()
        registry.register(MockTool("tracked_tool", ToolType.FILE_SYSTEM))
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create executor."""
        return MockToolExecutor(registry)

    @pytest.mark.asyncio
    async def test_history_recorded(self, executor: MockToolExecutor):
        """Test execution history is recorded."""
        call = ToolCall(
            tool_name="tracked_tool",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"key": "value"}
        )

        await executor.execute(call)

        assert len(executor.execution_history) == 1
        name, params, result = executor.execution_history[0]
        assert name == "tracked_tool"
        assert params == {"key": "value"}
        assert result.success is True

    @pytest.mark.asyncio
    async def test_multiple_executions_tracked(self, executor: MockToolExecutor):
        """Test multiple executions are tracked."""
        for i in range(5):
            call = ToolCall(
                tool_name="tracked_tool",
                tool_type=ToolType.FILE_SYSTEM,
                parameters={"iteration": i}
            )
            await executor.execute(call)

        assert len(executor.execution_history) == 5


class TestConcurrencyLimits:
    """Tests for concurrent execution limits."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create registry."""
        registry = MockToolRegistry()
        registry.register(MockTool("concurrent_tool", ToolType.FILE_SYSTEM))
        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create executor with low concurrency limit."""
        executor = MockToolExecutor(registry)
        executor._max_concurrent = 2
        return executor

    @pytest.mark.asyncio
    async def test_concurrency_respected(self, executor: MockToolExecutor):
        """Test concurrency limit is respected."""
        # Simulate max concurrent by manually setting
        executor._current_concurrent = 2

        call = ToolCall(
            tool_name="concurrent_tool",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={}
        )

        result = await executor.execute(call)
        assert result.success is False
        assert "concurrent" in result.error.lower()


class TestToolChaining:
    """Tests for chaining multiple tool calls."""

    @pytest.fixture
    def registry(self) -> MockToolRegistry:
        """Create registry with chainable tools."""
        registry = MockToolRegistry()
        read_tool = MockTool("read_file", ToolType.FILE_SYSTEM)
        read_tool.set_results([
            ToolResult(success=True, output="file content")
        ])
        registry.register(read_tool)

        process_tool = MockTool("process_content", ToolType.CODE_EXECUTION)
        process_tool.set_results([
            ToolResult(success=True, output="processed content")
        ])
        registry.register(process_tool)

        return registry

    @pytest.fixture
    def executor(self, registry: MockToolRegistry) -> MockToolExecutor:
        """Create executor."""
        return MockToolExecutor(registry)

    @pytest.fixture
    def agent(self, executor: MockToolExecutor) -> MockAgentWithTools:
        """Create agent with permissions."""
        agent = MockAgentWithTools(AgentType.CODER, executor)
        agent.grant_permission(ToolType.FILE_SYSTEM)
        agent.grant_permission(ToolType.CODE_EXECUTION)
        return agent

    @pytest.mark.asyncio
    async def test_chain_tool_calls(self, agent: MockAgentWithTools):
        """Test chaining tool calls using output from previous call."""
        # Read file
        read_call = ToolCall(
            tool_name="read_file",
            tool_type=ToolType.FILE_SYSTEM,
            parameters={"path": "/input.txt"}
        )
        read_result = await agent.use_tool(read_call)
        assert read_result.success is True

        # Process content using output from read
        process_call = ToolCall(
            tool_name="process_content",
            tool_type=ToolType.CODE_EXECUTION,
            parameters={"content": read_result.output}
        )
        process_result = await agent.use_tool(process_call)
        assert process_result.success is True
        assert process_result.output == "processed content"
