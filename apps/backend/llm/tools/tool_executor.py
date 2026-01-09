"""Tool executor for running tools.

Part of Phase 2: LLM Architecture
"""

import asyncio
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..types import ToolCall
from .tool_registry import RegisteredTool, ToolRegistry
from .tool_result import ResultType, ToolError, ToolResult

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Context for tool execution."""

    session_id: str
    user_id: str | None = None
    agent_id: str | None = None
    timeout: float = 30.0
    max_retries: int = 0
    allow_dangerous: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetrics:
    """Metrics for a tool execution."""

    tool_name: str
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None
    retry_count: int = 0


class ToolExecutor:
    """Executes tools with validation and error handling."""

    def __init__(self, registry: ToolRegistry | None = None, max_workers: int = 4):
        self._registry = registry or ToolRegistry()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._metrics: list[ExecutionMetrics] = []

    async def execute(
        self, tool_call: ToolCall, context: ExecutionContext
    ) -> ToolResult:
        """Execute a tool call."""
        metrics = ExecutionMetrics(
            tool_name=tool_call.name, start_time=datetime.utcnow()
        )

        try:
            # Get tool
            tool = self._registry.get(tool_call.name)
            if not tool:
                raise ToolError(
                    f"Tool not found: {tool_call.name}", code="TOOL_NOT_FOUND"
                )

            if not tool.enabled:
                raise ToolError(
                    f"Tool disabled: {tool_call.name}", code="TOOL_DISABLED"
                )

            # Check confirmation requirement
            if tool.requires_confirmation and not context.allow_dangerous:
                raise ToolError(
                    f"Tool requires confirmation: {tool_call.name}",
                    code="CONFIRMATION_REQUIRED",
                )

            # Validate arguments
            errors = tool.schema.validate_arguments(tool_call.arguments)
            if errors:
                raise ToolError(
                    f"Invalid arguments: {'; '.join(errors)}", code="INVALID_ARGUMENTS"
                )

            # Execute with retry
            result = await self._execute_with_retry(
                tool, tool_call.arguments, context, metrics
            )

            # Record metrics
            metrics.end_time = datetime.utcnow()
            metrics.duration_ms = (
                metrics.end_time - metrics.start_time
            ).total_seconds() * 1000
            metrics.success = True
            self._metrics.append(metrics)
            self._registry.record_call(tool_call.name)

            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                result=result,
                result_type=ResultType.SUCCESS,
                duration_ms=metrics.duration_ms,
            )

        except ToolError as e:
            metrics.error = str(e)
            metrics.end_time = datetime.utcnow()
            metrics.duration_ms = (
                metrics.end_time - metrics.start_time
            ).total_seconds() * 1000
            self._metrics.append(metrics)

            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                error=str(e),
                result_type=ResultType.ERROR,
                error_code=e.code,
            )

        except Exception as e:
            logger.error("Tool execution failed: %s", e)
            metrics.error = str(e)
            metrics.end_time = datetime.utcnow()
            metrics.duration_ms = (
                metrics.end_time - metrics.start_time
            ).total_seconds() * 1000
            self._metrics.append(metrics)

            return ToolResult(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
                error=str(e),
                result_type=ResultType.ERROR,
                error_code="EXECUTION_ERROR",
            )

    async def _execute_with_retry(
        self,
        tool: RegisteredTool,
        arguments: dict[str, Any],
        context: ExecutionContext,
        metrics: ExecutionMetrics,
    ) -> Any:
        """Execute with retry logic."""
        last_error = None

        for attempt in range(context.max_retries + 1):
            try:
                return await self._execute_handler(
                    tool.handler, arguments, context.timeout
                )
            except Exception as e:
                last_error = e
                metrics.retry_count = attempt + 1
                if attempt < context.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))

        raise last_error or ToolError("Execution failed", code="EXECUTION_ERROR")

    async def _execute_handler(
        self, handler: Callable, arguments: dict[str, Any], timeout: float
    ) -> Any:
        """Execute handler with timeout."""
        if asyncio.iscoroutinefunction(handler):
            return await asyncio.wait_for(handler(**arguments), timeout=timeout)
        else:
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(self._executor, lambda: handler(**arguments)),
                timeout=timeout,
            )

    async def execute_batch(
        self,
        tool_calls: list[ToolCall],
        context: ExecutionContext,
        parallel: bool = False,
    ) -> list[ToolResult]:
        """Execute multiple tool calls."""
        if parallel:
            tasks = [self.execute(tc, context) for tc in tool_calls]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for tc in tool_calls:
                result = await self.execute(tc, context)
                results.append(result)
            return results

    def get_metrics(self, tool_name: str | None = None) -> list[ExecutionMetrics]:
        """Get execution metrics."""
        if tool_name:
            return [m for m in self._metrics if m.tool_name == tool_name]
        return self._metrics.copy()

    def clear_metrics(self) -> None:
        """Clear metrics."""
        self._metrics.clear()
