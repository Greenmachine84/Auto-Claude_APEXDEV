"""Tool executor.

Executes tools with proper context and error handling.

Capabilities:
- Execute single tools
- Execute tool sequences
- Handle tool results
- Manage execution context
"""

import asyncio
import logging
from typing import Any

from tools.core.base_tool import ToolContext, ToolResult, ToolStatus
from tools.core.permissions import PermissionManager
from tools.core.sandbox import Sandbox
from tools.core.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools with context management.

    Handles tool execution including permission checks,
    sandboxing, and result handling.

    Example:
        executor = ToolExecutor(registry)

        result = await executor.execute(
            "file_read",
            {"path": "/path/to/file"}
        )
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        permission_manager: PermissionManager | None = None,
        sandbox: Sandbox | None = None,
    ):
        """Initialize executor.

        Args:
            registry: Tool registry to use
            permission_manager: Permission manager
            sandbox: Sandbox for execution
        """
        self.registry = registry or ToolRegistry()
        self.permission_manager = permission_manager
        self.sandbox = sandbox
        self._execution_count = 0

    async def execute(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: ToolContext | None = None,
        timeout: int | None = None,
    ) -> ToolResult:
        """Execute a tool.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            context: Optional execution context
            timeout: Optional timeout in seconds

        Returns:
            Tool execution result
        """
        self._execution_count += 1

        # Get tool
        tool = self.registry.get(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILED,
                output=None,
                error=f"Tool not found: {tool_name}",
            )

        # Check permissions
        if self.permission_manager:
            for perm in tool.required_permissions:
                if not self.permission_manager.has_permission(perm):
                    return ToolResult(
                        tool_name=tool_name,
                        status=ToolStatus.FAILED,
                        output=None,
                        error=f"Permission denied: {perm}",
                    )

        # Build context
        if context is None:
            context = ToolContext(
                tool_call_id=f"call_{self._execution_count}",
                parameters=parameters,
                timeout_seconds=timeout or 60,
            )
        else:
            context.parameters = parameters

        # Execute with timeout
        try:
            if timeout:
                result = await asyncio.wait_for(
                    tool.run(context),
                    timeout=timeout,
                )
            else:
                result = await tool.run(context)

            logger.info(f"Tool executed: {tool_name}, status={result.status.value}")
            return result

        except asyncio.TimeoutError:
            return ToolResult(
                tool_name=tool_name,
                status=ToolStatus.TIMEOUT,
                output=None,
                error=f"Tool timed out after {timeout}s",
            )
        except Exception as e:
            logger.exception(f"Tool execution failed: {tool_name}")
            return ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
            )

    async def execute_sequence(
        self,
        tool_calls: list[dict[str, Any]],
        stop_on_error: bool = True,
    ) -> list[ToolResult]:
        """Execute a sequence of tools.

        Args:
            tool_calls: List of {"tool": name, "params": {...}}
            stop_on_error: Stop on first error

        Returns:
            List of results
        """
        results = []

        for call in tool_calls:
            tool_name = call.get("tool")
            params = call.get("params", {})

            result = await self.execute(tool_name, params)
            results.append(result)

            if stop_on_error and not result.is_success():
                break

        return results

    async def execute_parallel(
        self,
        tool_calls: list[dict[str, Any]],
        max_concurrent: int = 5,
    ) -> list[ToolResult]:
        """Execute tools in parallel.

        Args:
            tool_calls: List of {"tool": name, "params": {...}}
            max_concurrent: Maximum concurrent executions

        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_limit(call: dict[str, Any]) -> ToolResult:
            async with semaphore:
                return await self.execute(
                    call.get("tool"),
                    call.get("params", {}),
                )

        tasks = [execute_with_limit(call) for call in tool_calls]
        return await asyncio.gather(*tasks)

    def get_execution_count(self) -> int:
        """Get total execution count."""
        return self._execution_count
