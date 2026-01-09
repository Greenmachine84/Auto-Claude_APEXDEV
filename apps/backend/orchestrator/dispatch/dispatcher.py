"""Task dispatcher.

Dispatches tasks to agents.

Capabilities:
- Task routing
- Agent selection
- Load balancing
- Retry handling
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from orchestrator.pool.agent_pool import AgentInfo, AgentPool
    from orchestrator.queue.task_model import Task

from orchestrator.dispatch.load_balancer import LoadBalancer
from orchestrator.dispatch.priority_scheduler import PriorityScheduler
from orchestrator.dispatch.retry_handler import RetryHandler

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    """Result of task dispatch."""

    task_id: str
    agent_id: str
    success: bool
    result: Any = None
    error: str | None = None
    dispatched_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    @property
    def duration(self) -> float | None:
        """Get dispatch duration."""
        if self.completed_at:
            return (self.completed_at - self.dispatched_at).total_seconds()
        return None


class Dispatcher:
    """Dispatch tasks to agents.

    Coordinates task routing and execution.

    Example:
        dispatcher = Dispatcher(pool)
        result = await dispatcher.dispatch(task)
    """

    def __init__(
        self,
        pool: Optional["AgentPool"] = None,
        scheduler: PriorityScheduler | None = None,
        load_balancer: LoadBalancer | None = None,
        retry_handler: RetryHandler | None = None,
    ):
        """Initialize dispatcher."""
        self.pool = pool
        self.scheduler = scheduler or PriorityScheduler()
        self.load_balancer = load_balancer or LoadBalancer()
        self.retry_handler = retry_handler or RetryHandler()

        self._handlers: dict[str, Callable] = {}
        self._running = False
        self._dispatch_count = 0
        self._success_count = 0
        self._failure_count = 0

        logger.debug("Dispatcher initialized")

    def register_handler(
        self,
        task_type: str,
        handler: Callable,
    ) -> None:
        """Register task handler."""
        self._handlers[task_type] = handler
        logger.debug(f"Registered handler for task type: {task_type}")

    async def dispatch(
        self,
        task: "Task",
        agent: Optional["AgentInfo"] = None,
    ) -> DispatchResult:
        """Dispatch a task."""
        self._dispatch_count += 1

        # Get or select agent
        if not agent and self.pool:
            agent = await self.pool.acquire(
                capabilities=task.metadata.get("capabilities"),
            )

        if not agent:
            self._failure_count += 1
            return DispatchResult(
                task_id=task.id,
                agent_id="",
                success=False,
                error="No agent available",
            )

        result = DispatchResult(
            task_id=task.id,
            agent_id=agent.id,
            success=False,
        )

        try:
            # Get handler
            handler = self._handlers.get(task.type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.type}")

            # Execute with retry
            output = await self.retry_handler.execute(
                lambda: handler(task, agent),
                max_retries=task.max_retries,
            )

            result.success = True
            result.result = output
            self._success_count += 1

        except Exception as e:
            result.success = False
            result.error = str(e)
            self._failure_count += 1
            logger.error(f"Task {task.id} dispatch failed: {e}")
        finally:
            result.completed_at = datetime.now()

            # Release agent
            if self.pool:
                await self.pool.release(agent.id)

        return result

    async def dispatch_batch(
        self,
        tasks: list["Task"],
        parallel: bool = True,
    ) -> list[DispatchResult]:
        """Dispatch multiple tasks."""
        if parallel:
            # Sort by priority
            sorted_tasks = self.scheduler.schedule(tasks)

            # Dispatch in parallel
            results = await asyncio.gather(
                *[self.dispatch(task) for task in sorted_tasks],
                return_exceptions=True,
            )

            return [
                r
                if isinstance(r, DispatchResult)
                else DispatchResult(
                    task_id="unknown",
                    agent_id="",
                    success=False,
                    error=str(r),
                )
                for r in results
            ]
        else:
            results = []
            for task in tasks:
                result = await self.dispatch(task)
                results.append(result)
            return results

    def get_metrics(self) -> dict[str, Any]:
        """Get dispatcher metrics."""
        return {
            "dispatch_count": self._dispatch_count,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "success_rate": self._success_count / max(1, self._dispatch_count),
            "handlers": list(self._handlers.keys()),
        }
