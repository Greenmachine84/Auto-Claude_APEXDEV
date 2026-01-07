"""
Enhanced Tool Executor - Phase 8 Implementation.

High-performance tool execution with comprehensive features.

World-Class Standards:
- Async execution
- Parallel execution support
- Comprehensive error handling
- Performance monitoring
- Event-driven architecture
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import time
import logging

from ..models import Tool, ToolResult, ToolExecutionContext
from ..registry.tool_registry import ToolRegistry
from .sandbox import Sandbox, SandboxConfig
from .timeout_handler import TimeoutHandler
from .result_handler import ResultHandler

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Execution performance metrics."""
    tool_name: str
    start_time: str
    end_time: str
    duration_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class ExecutorConfig:
    """Executor configuration."""
    max_concurrent: int = 10
    default_timeout_ms: int = 30000
    enable_sandbox: bool = True
    enable_metrics: bool = True
    retry_attempts: int = 3
    retry_delay_ms: int = 1000


class ToolExecutor:
    """
    High-performance tool executor.
    
    Features:
    - Async execution
    - Parallel execution
    - Sandboxing
    - Timeout management
    - Retry logic
    - Metrics collection
    """
    
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        config: Optional[ExecutorConfig] = None,
    ) -> None:
        """Initialize executor."""
        self.registry = registry or ToolRegistry()
        self.config = config or ExecutorConfig()
        
        self.sandbox = Sandbox(SandboxConfig()) if self.config.enable_sandbox else None
        self.timeout_handler = TimeoutHandler()
        self.result_handler = ResultHandler()
        
        # Execution tracking
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self._metrics: List[ExecutionMetrics] = []
        self._callbacks: List[Callable] = []
        
        logger.info(
            "ToolExecutor initialized (max_concurrent=%d)",
            self.config.max_concurrent
        )
    
    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[ToolExecutionContext] = None,
    ) -> ToolResult:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            context: Execution context
            
        Returns:
            ToolResult with execution outcome
        """
        start_time = datetime.utcnow()
        start_ts = time.perf_counter()
        
        async with self._semaphore:
            try:
                # Get tool from registry
                tool = await self.registry.get(tool_name)
                if not tool:
                    return ToolResult(
                        output=None,
                        error=f"Tool not found: {tool_name}",
                        metadata={"tool_name": tool_name},
                    )
                
                # Check permissions
                if context and not self._check_permissions(tool, context):
                    return ToolResult(
                        output=None,
                        error="Permission denied",
                        metadata={"tool_name": tool_name},
                    )
                
                # Validate arguments
                validation = self._validate_arguments(tool, arguments)
                if not validation["valid"]:
                    return ToolResult(
                        output=None,
                        error=f"Invalid arguments: {validation['errors']}",
                        metadata={"tool_name": tool_name},
                    )
                
                # Prepare context
                exec_context = context or ToolExecutionContext(
                    user_id="system",
                    session_id="default",
                )
                
                # Execute with timeout
                timeout_ms = exec_context.timeout_ms or self.config.default_timeout_ms
                
                result = await self._execute_with_retry(
                    tool=tool,
                    arguments=arguments,
                    context=exec_context,
                    timeout_ms=timeout_ms,
                )
                
                # Record metrics
                end_ts = time.perf_counter()
                duration_ms = (end_ts - start_ts) * 1000
                
                if self.config.enable_metrics:
                    await self._record_metrics(ExecutionMetrics(
                        tool_name=tool_name,
                        start_time=start_time.isoformat(),
                        end_time=datetime.utcnow().isoformat(),
                        duration_ms=duration_ms,
                        success=result.success,
                        error=result.error,
                    ))
                
                # Record usage
                await self.registry.record_usage(tool_name)
                
                return result
                
            except Exception as e:
                logger.error("Execution error for %s: %s", tool_name, e)
                return ToolResult(
                    output=None,
                    error=str(e),
                    metadata={"tool_name": tool_name, "exception": type(e).__name__},
                )
    
    async def execute_parallel(
        self,
        executions: List[Dict[str, Any]],
        context: Optional[ToolExecutionContext] = None,
    ) -> List[ToolResult]:
        """
        Execute multiple tools in parallel.
        
        Args:
            executions: List of {"tool_name": str, "arguments": dict}
            context: Shared execution context
            
        Returns:
            List of ToolResults in same order as input
        """
        tasks = [
            self.execute(
                tool_name=exec_def["tool_name"],
                arguments=exec_def.get("arguments", {}),
                context=context,
            )
            for exec_def in executions
        ]
        
        return await asyncio.gather(*tasks)
    
    async def execute_sequential(
        self,
        executions: List[Dict[str, Any]],
        context: Optional[ToolExecutionContext] = None,
        stop_on_error: bool = True,
    ) -> List[ToolResult]:
        """
        Execute tools sequentially.
        
        Args:
            executions: List of tool execution definitions
            context: Shared execution context
            stop_on_error: Whether to stop on first error
            
        Returns:
            List of ToolResults
        """
        results = []
        
        for exec_def in executions:
            result = await self.execute(
                tool_name=exec_def["tool_name"],
                arguments=exec_def.get("arguments", {}),
                context=context,
            )
            results.append(result)
            
            if stop_on_error and not result.success:
                break
        
        return results
    
    async def _execute_with_retry(
        self,
        tool: Tool,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
        timeout_ms: int,
    ) -> ToolResult:
        """Execute with retry logic."""
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                result = await self.timeout_handler.execute_with_timeout(
                    coro=self._execute_tool(tool, arguments, context),
                    timeout_ms=timeout_ms,
                )
                
                if result.success:
                    return result
                
                last_error = result.error
                
                # Don't retry certain errors
                if self._is_permanent_error(result.error):
                    return result
                
            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout_ms}ms"
            except Exception as e:
                last_error = str(e)
            
            # Wait before retry
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_delay_ms / 1000)
        
        return ToolResult(
            output=None,
            error=f"Failed after {self.config.retry_attempts} attempts: {last_error}",
            metadata={"attempts": self.config.retry_attempts},
        )
    
    async def _execute_tool(
        self,
        tool: Tool,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        """Execute the tool handler."""
        if not tool.handler:
            return ToolResult(
                output=None,
                error="Tool has no handler",
                metadata={"tool_name": tool.name},
            )
        
        # Execute in sandbox if enabled
        if self.sandbox and not context.sandbox_disabled:
            return await self.sandbox.execute(
                handler=tool.handler,
                arguments=arguments,
                context=context,
            )
        
        # Direct execution
        if asyncio.iscoroutinefunction(tool.handler):
            output = await tool.handler(context, **arguments)
        else:
            output = tool.handler(context, **arguments)
        
        return self.result_handler.normalize(output, tool.name)
    
    def _check_permissions(
        self, tool: Tool, context: ToolExecutionContext
    ) -> bool:
        """Check if execution is permitted."""
        # Check required permissions
        for perm in tool.permissions:
            if perm not in context.permissions:
                return False
        return True
    
    def _validate_arguments(
        self, tool: Tool, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate tool arguments."""
        errors = []
        
        for param in tool.parameters:
            if param.required and param.name not in arguments:
                errors.append(f"Missing required parameter: {param.name}")
            
            if param.name in arguments:
                value = arguments[param.name]
                param_valid, param_errors = param.validate(value)
                if not param_valid:
                    errors.extend(param_errors)
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _is_permanent_error(self, error: Optional[str]) -> bool:
        """Check if error should not be retried."""
        if not error:
            return False
        permanent = ["permission denied", "not found", "invalid argument"]
        return any(p in error.lower() for p in permanent)
    
    async def _record_metrics(self, metrics: ExecutionMetrics) -> None:
        """Record execution metrics."""
        self._metrics.append(metrics)
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error("Callback error: %s", e)
        
        # Trim old metrics
        if len(self._metrics) > 10000:
            self._metrics = self._metrics[-5000:]
    
    def add_callback(self, callback: Callable) -> None:
        """Add execution callback."""
        self._callbacks.append(callback)
    
    def get_metrics(
        self,
        tool_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[ExecutionMetrics]:
        """Get execution metrics."""
        metrics = self._metrics
        if tool_name:
            metrics = [m for m in metrics if m.tool_name == tool_name]
        return metrics[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get executor statistics."""
        if not self._metrics:
            return {"total_executions": 0}
        
        total = len(self._metrics)
        successful = sum(1 for m in self._metrics if m.success)
        durations = [m.duration_ms for m in self._metrics]
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration_ms": sum(durations) / len(durations),
            "p50_duration_ms": sorted(durations)[len(durations) // 2],
            "p99_duration_ms": sorted(durations)[int(len(durations) * 0.99)],
        }
