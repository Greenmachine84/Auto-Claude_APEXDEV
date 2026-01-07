"""
Timeout Handler - Phase 8 Implementation.

Robust timeout management for tool execution.

World-Class Standards:
- Configurable timeouts
- Graceful cancellation
- Timeout chains
- Deadline propagation
"""

from typing import TypeVar, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class TimeoutStats:
    """Timeout statistics."""
    total_executions: int = 0
    timeout_count: int = 0
    cancelled_count: int = 0
    avg_execution_ms: float = 0.0


class TimeoutHandler:
    """
    Robust timeout management.
    
    Features:
    - Async timeout handling
    - Graceful cancellation
    - Deadline chains
    - Statistics tracking
    """
    
    def __init__(
        self,
        default_timeout_ms: int = 30000,
        grace_period_ms: int = 1000,
    ) -> None:
        """Initialize handler."""
        self.default_timeout_ms = default_timeout_ms
        self.grace_period_ms = grace_period_ms
        
        self._stats = TimeoutStats()
        self._active_tasks: dict = {}
        
        logger.info(
            "TimeoutHandler initialized (default=%dms, grace=%dms)",
            default_timeout_ms,
            grace_period_ms
        )
    
    async def execute_with_timeout(
        self,
        coro,
        timeout_ms: Optional[int] = None,
        on_timeout: Optional[Callable] = None,
    ) -> Any:
        """
        Execute coroutine with timeout.
        
        Args:
            coro: Coroutine to execute
            timeout_ms: Timeout in milliseconds
            on_timeout: Optional callback on timeout
            
        Returns:
            Coroutine result
            
        Raises:
            asyncio.TimeoutError: If execution times out
        """
        timeout = (timeout_ms or self.default_timeout_ms) / 1000.0
        task_id = id(coro)
        
        self._stats.total_executions += 1
        start_time = datetime.utcnow()
        
        try:
            task = asyncio.ensure_future(coro)
            self._active_tasks[task_id] = {
                "task": task,
                "start_time": start_time,
                "timeout_ms": timeout_ms,
            }
            
            result = await asyncio.wait_for(task, timeout=timeout)
            
            # Update stats
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_avg_duration(duration_ms)
            
            return result
            
        except asyncio.TimeoutError:
            self._stats.timeout_count += 1
            logger.warning("Execution timed out after %dms", timeout_ms)
            
            if on_timeout:
                try:
                    on_timeout()
                except Exception as e:
                    logger.error("Timeout callback error: %s", e)
            
            raise
            
        except asyncio.CancelledError:
            self._stats.cancelled_count += 1
            logger.info("Execution was cancelled")
            raise
            
        finally:
            self._active_tasks.pop(task_id, None)
    
    async def execute_with_deadline(
        self,
        coro,
        deadline: datetime,
        on_timeout: Optional[Callable] = None,
    ) -> Any:
        """
        Execute coroutine with absolute deadline.
        
        Args:
            coro: Coroutine to execute
            deadline: Absolute deadline
            on_timeout: Optional callback on timeout
            
        Returns:
            Coroutine result
        """
        now = datetime.utcnow()
        remaining = deadline - now
        
        if remaining.total_seconds() <= 0:
            raise asyncio.TimeoutError("Deadline already passed")
        
        timeout_ms = int(remaining.total_seconds() * 1000)
        return await self.execute_with_timeout(coro, timeout_ms, on_timeout)
    
    async def execute_with_chain(
        self,
        coros: list,
        total_timeout_ms: int,
        allocation: Optional[list] = None,
    ) -> list:
        """
        Execute chain of coroutines with total timeout.
        
        Args:
            coros: List of coroutines
            total_timeout_ms: Total timeout for all
            allocation: Optional per-coro allocation (percentages)
            
        Returns:
            List of results
        """
        if not coros:
            return []
        
        # Calculate per-coroutine timeouts
        if allocation:
            if len(allocation) != len(coros):
                raise ValueError("Allocation must match coroutine count")
            timeouts = [int(total_timeout_ms * a) for a in allocation]
        else:
            per_coro = total_timeout_ms // len(coros)
            timeouts = [per_coro] * len(coros)
        
        deadline = datetime.utcnow() + timedelta(milliseconds=total_timeout_ms)
        results = []
        
        for i, coro in enumerate(coros):
            # Check deadline
            remaining = (deadline - datetime.utcnow()).total_seconds() * 1000
            if remaining <= 0:
                raise asyncio.TimeoutError("Chain deadline exceeded")
            
            # Use minimum of allocated and remaining
            timeout = min(timeouts[i], int(remaining))
            
            result = await self.execute_with_timeout(coro, timeout)
            results.append(result)
        
        return results
    
    async def cancel_all(self) -> int:
        """Cancel all active tasks."""
        cancelled = 0
        
        for task_id, task_info in list(self._active_tasks.items()):
            task = task_info["task"]
            if not task.done():
                task.cancel()
                cancelled += 1
        
        logger.info("Cancelled %d active tasks", cancelled)
        return cancelled
    
    async def graceful_cancel(
        self,
        task_id: int,
        grace_ms: Optional[int] = None,
    ) -> bool:
        """
        Gracefully cancel a task.
        
        Args:
            task_id: Task ID to cancel
            grace_ms: Grace period before force cancel
            
        Returns:
            True if cancelled successfully
        """
        if task_id not in self._active_tasks:
            return False
        
        grace = (grace_ms or self.grace_period_ms) / 1000.0
        task_info = self._active_tasks[task_id]
        task = task_info["task"]
        
        # Request cancellation
        task.cancel()
        
        try:
            # Wait for graceful completion
            await asyncio.wait_for(
                asyncio.shield(task),
                timeout=grace
            )
        except (asyncio.TimeoutError, asyncio.CancelledError):
            # Force cancel
            pass
        
        return True
    
    def _update_avg_duration(self, duration_ms: float) -> None:
        """Update average duration statistic."""
        n = self._stats.total_executions - self._stats.timeout_count
        if n <= 0:
            return
        
        # Running average
        current_avg = self._stats.avg_execution_ms
        self._stats.avg_execution_ms = (
            (current_avg * (n - 1) + duration_ms) / n
        )
    
    def get_stats(self) -> TimeoutStats:
        """Get timeout statistics."""
        return self._stats
    
    def get_active_count(self) -> int:
        """Get count of active executions."""
        return len(self._active_tasks)
    
    def get_active_tasks(self) -> list:
        """Get info about active tasks."""
        return [
            {
                "id": task_id,
                "start_time": info["start_time"].isoformat(),
                "timeout_ms": info["timeout_ms"],
                "elapsed_ms": (
                    datetime.utcnow() - info["start_time"]
                ).total_seconds() * 1000,
            }
            for task_id, info in self._active_tasks.items()
        ]
