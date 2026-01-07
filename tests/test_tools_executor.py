"""
Tools Executor Tests - Phase 8.

Tests for tool executor, sandbox, timeout handler, and result handler.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from apps.backend.tools.models import (
    Tool, ToolParameter, ToolResult, ToolCategory,
    ParameterType, ToolExecutionContext
)
from apps.backend.tools.executor.tool_executor import ToolExecutor, ExecutorConfig
from apps.backend.tools.executor.sandbox import Sandbox, SandboxConfig
from apps.backend.tools.executor.timeout_handler import TimeoutHandler
from apps.backend.tools.executor.result_handler import ResultHandler


class TestToolExecutor:
    """Test ToolExecutor."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        config = ExecutorConfig(
            max_concurrent=5,
            default_timeout_ms=5000,
            enable_sandbox=False,  # Disable for unit tests
        )
        return ToolExecutor(config=config)
    
    @pytest.mark.asyncio
    async def test_execute_simple_tool(self, executor):
        """Test executing a simple tool."""
        async def handler(ctx, message: str):
            return {"echo": message}
        
        tool = Tool(
            name="echo",
            description="Echo tool",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="message",
                    type=ParameterType.STRING,
                    description="Message to echo",
                    required=True,
                )
            ],
            handler=handler,
        )
        
        await executor.registry.register(tool)
        
        result = await executor.execute(
            tool_name="echo",
            arguments={"message": "hello"},
        )
        
        assert result.success
        assert result.output["echo"] == "hello"
    
    @pytest.mark.asyncio
    async def test_execute_missing_tool(self, executor):
        """Test executing non-existent tool."""
        result = await executor.execute(
            tool_name="nonexistent_tool",
            arguments={},
        )
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_invalid_arguments(self, executor):
        """Test executing with invalid arguments."""
        async def handler(ctx, required_arg: str):
            return required_arg
        
        tool = Tool(
            name="requires_arg",
            description="Needs an argument",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="required_arg",
                    type=ParameterType.STRING,
                    description="Required",
                    required=True,
                )
            ],
            handler=handler,
        )
        
        await executor.registry.register(tool)
        
        result = await executor.execute(
            tool_name="requires_arg",
            arguments={},  # Missing required arg
        )
        
        assert not result.success
    
    @pytest.mark.asyncio
    async def test_execute_parallel(self, executor):
        """Test parallel execution."""
        async def slow_handler(ctx, id: int):
            await asyncio.sleep(0.1)
            return {"id": id}
        
        tool = Tool(
            name="slow_tool",
            description="Slow tool",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(name="id", type=ParameterType.INTEGER, description="ID")
            ],
            handler=slow_handler,
        )
        
        await executor.registry.register(tool)
        
        executions = [
            {"tool_name": "slow_tool", "arguments": {"id": i}}
            for i in range(5)
        ]
        
        start = datetime.utcnow()
        results = await executor.execute_parallel(executions)
        duration = (datetime.utcnow() - start).total_seconds()
        
        # Parallel should be faster than sequential (5 * 0.1s = 0.5s)
        assert duration < 0.4
        assert len(results) == 5
        assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_execute_sequential(self, executor):
        """Test sequential execution."""
        call_order = []
        
        async def ordered_handler(ctx, id: int):
            call_order.append(id)
            return {"id": id}
        
        tool = Tool(
            name="ordered_tool",
            description="Ordered tool",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(name="id", type=ParameterType.INTEGER, description="ID")
            ],
            handler=ordered_handler,
        )
        
        await executor.registry.register(tool)
        
        executions = [
            {"tool_name": "ordered_tool", "arguments": {"id": i}}
            for i in range(3)
        ]
        
        results = await executor.execute_sequential(executions)
        
        assert call_order == [0, 1, 2]
    
    @pytest.mark.asyncio
    async def test_execution_statistics(self, executor):
        """Test execution statistics."""
        async def handler(ctx):
            return "ok"
        
        tool = Tool(
            name="stats_tool",
            description="For stats",
            category=ToolCategory.UTILITY,
            handler=handler,
        )
        
        await executor.registry.register(tool)
        
        for _ in range(10):
            await executor.execute("stats_tool", {})
        
        stats = executor.get_statistics()
        
        assert stats["total_executions"] >= 10
        assert "avg_duration_ms" in stats


class TestSandbox:
    """Test Sandbox."""
    
    @pytest.fixture
    def sandbox(self):
        """Create sandbox."""
        config = SandboxConfig(
            allowed_paths=["/tmp", "/home"],
            denied_paths=["/etc", "/usr/bin"],
        )
        return Sandbox(config)
    
    @pytest.mark.asyncio
    async def test_execute_allowed(self, sandbox):
        """Test execution in sandbox."""
        async def handler(ctx):
            return {"status": "ok"}
        
        context = ToolExecutionContext(
            user_id="user-001",
            session_id="session-001",
        )
        
        result = await sandbox.execute(handler, {}, context)
        
        assert result.success
        assert result.output["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_path_denied(self, sandbox):
        """Test denied path access."""
        result = sandbox._check_path("/etc/passwd")
        
        assert result is not None
        assert result.violation_type == "path_denied"
    
    @pytest.mark.asyncio
    async def test_audit_logging(self, sandbox):
        """Test audit log is recorded."""
        async def handler(ctx):
            return "done"
        
        context = ToolExecutionContext(
            user_id="audited_user",
            session_id="audited_session",
        )
        
        await sandbox.execute(handler, {}, context)
        
        log = sandbox.get_audit_log()
        assert len(log) > 0


class TestTimeoutHandler:
    """Test TimeoutHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create timeout handler."""
        return TimeoutHandler(default_timeout_ms=1000)
    
    @pytest.mark.asyncio
    async def test_execute_within_timeout(self, handler):
        """Test execution completes within timeout."""
        async def fast_coro():
            await asyncio.sleep(0.1)
            return "done"
        
        result = await handler.execute_with_timeout(fast_coro(), timeout_ms=1000)
        assert result == "done"
    
    @pytest.mark.asyncio
    async def test_execute_timeout_exceeded(self, handler):
        """Test timeout exception raised."""
        async def slow_coro():
            await asyncio.sleep(10)
            return "never"
        
        with pytest.raises(asyncio.TimeoutError):
            await handler.execute_with_timeout(slow_coro(), timeout_ms=100)
    
    @pytest.mark.asyncio
    async def test_execute_with_deadline(self, handler):
        """Test deadline-based execution."""
        from datetime import timedelta
        
        async def quick():
            return "quick"
        
        deadline = datetime.utcnow() + timedelta(seconds=5)
        result = await handler.execute_with_deadline(quick(), deadline)
        
        assert result == "quick"
    
    @pytest.mark.asyncio
    async def test_timeout_statistics(self, handler):
        """Test timeout statistics."""
        async def fast():
            return "ok"
        
        for _ in range(5):
            await handler.execute_with_timeout(fast(), timeout_ms=1000)
        
        stats = handler.get_stats()
        assert stats.total_executions == 5
        assert stats.timeout_count == 0


class TestResultHandler:
    """Test ResultHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create result handler."""
        return ResultHandler()
    
    def test_normalize_dict(self, handler):
        """Test normalizing dict output."""
        output = {"key": "value"}
        result = handler.normalize(output, "test_tool")
        
        assert result.success
        assert result.output == {"key": "value"}
    
    def test_normalize_error_dict(self, handler):
        """Test normalizing error dict."""
        output = {"error": "Something went wrong"}
        result = handler.normalize(output, "test_tool")
        
        assert not result.success
        assert result.error == "Something went wrong"
    
    def test_normalize_exception(self, handler):
        """Test normalizing exception."""
        output = ValueError("Bad value")
        result = handler.normalize(output, "test_tool")
        
        assert not result.success
        assert "Bad value" in result.error
    
    def test_to_json(self, handler):
        """Test JSON conversion."""
        result = ToolResult(
            output={"data": "test"},
            error=None,
            metadata={"tool_name": "test"},
        )
        
        json_str = handler.to_json(result)
        
        assert "data" in json_str
        assert "test" in json_str
    
    def test_to_openai_message(self, handler):
        """Test OpenAI message format."""
        result = ToolResult(
            output={"result": "success"},
            error=None,
            metadata={"tool_call_id": "call_123"},
        )
        
        msg = handler.to_openai_message(result)
        
        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_123"
    
    def test_to_anthropic_result(self, handler):
        """Test Anthropic result format."""
        result = ToolResult(
            output="success",
            error=None,
            metadata={"tool_use_id": "use_456"},
        )
        
        res = handler.to_anthropic_result(result)
        
        assert res["type"] == "tool_result"
        assert res["tool_use_id"] == "use_456"
        assert res["is_error"] is False
    
    def test_merge_results(self, handler):
        """Test merging multiple results."""
        results = [
            ToolResult(output="a", error=None, metadata={}),
            ToolResult(output="b", error=None, metadata={}),
            ToolResult(output="c", error=None, metadata={}),
        ]
        
        merged = handler.merge_results(results)
        
        assert merged.success
        assert len(merged.output) == 3
        assert merged.metadata["count"] == 3
    
    def test_enrich_error(self, handler):
        """Test error enrichment."""
        result = ToolResult(
            output=None,
            error="Permission denied",
            metadata={},
        )
        
        enriched = handler.enrich_error(result, {"path": "/etc/passwd"})
        
        assert "suggestions" in enriched.metadata
        assert len(enriched.metadata["suggestions"]) > 0
