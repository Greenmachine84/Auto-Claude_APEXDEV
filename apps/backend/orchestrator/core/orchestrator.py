"""Main orchestrator implementation.

Coordinates task execution across agents.

Responsibilities:
- Task scheduling
- Agent coordination
- Workflow execution
- Resource management
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from orchestrator.core.config import OrchestratorConfig
from orchestrator.core.execution_context import ExecutionContext

logger = logging.getLogger(__name__)


@dataclass
class TaskState:
    """Track state of a task."""

    task_id: str
    status: str = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None


class Orchestrator:
    """Main orchestrator for task coordination.

    Manages the lifecycle of tasks from submission to completion.
    Coordinates between task queues, agent pools, and workflows.

    Example:
        config = OrchestratorConfig()
        orchestrator = Orchestrator(config)
        await orchestrator.start()

        task_id = await orchestrator.submit_task(task)
        result = await orchestrator.wait_for_result(task_id)
    """

    def __init__(self, config: OrchestratorConfig | None = None):
        """Initialize orchestrator."""
        self.config = config or OrchestratorConfig()
        self._running = False
        self._tasks: dict[str, TaskState] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._workers: list[asyncio.Task] = []
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()

        logger.info(f"Orchestrator initialized with config: {self.config}")

    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running

    @property
    def pending_count(self) -> int:
        """Get count of pending tasks."""
        return sum(1 for t in self._tasks.values() if t.status == "pending")

    @property
    def running_count(self) -> int:
        """Get count of running tasks."""
        return sum(1 for t in self._tasks.values() if t.status == "running")

    async def start(self) -> None:
        """Start the orchestrator."""
        if self._running:
            logger.warning("Orchestrator already running")
            return

        self._running = True
        self._shutdown_event.clear()

        # Start worker tasks
        for i in range(self.config.worker_count):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)

        logger.info(f"Orchestrator started with {self.config.worker_count} workers")

    async def stop(self, timeout: float = 30.0) -> None:
        """Stop the orchestrator gracefully."""
        if not self._running:
            return

        logger.info("Stopping orchestrator...")
        self._running = False
        self._shutdown_event.set()

        # Wait for workers to finish
        if self._workers:
            done, pending = await asyncio.wait(
                self._workers,
                timeout=timeout,
            )

            # Cancel remaining
            for task in pending:
                task.cancel()

            self._workers.clear()

        logger.info("Orchestrator stopped")

    async def submit_task(
        self,
        task: dict[str, Any],
        priority: int = 0,
    ) -> str:
        """Submit a task for execution."""
        task_id = task.get("id") or self._generate_task_id()

        async with self._lock:
            state = TaskState(task_id=task_id)
            self._tasks[task_id] = state

        await self._task_queue.put((priority, task_id, task))

        logger.debug(f"Task {task_id} submitted with priority {priority}")
        return task_id

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get status of a task."""
        state = self._tasks.get(task_id)
        if not state:
            return None

        return {
            "task_id": state.task_id,
            "status": state.status,
            "started_at": state.started_at.isoformat() if state.started_at else None,
            "completed_at": state.completed_at.isoformat()
            if state.completed_at
            else None,
            "error": state.error,
        }

    async def wait_for_result(
        self,
        task_id: str,
        timeout: float | None = None,
    ) -> Any:
        """Wait for task completion and return result."""
        timeout = timeout or self.config.default_timeout
        deadline = asyncio.get_event_loop().time() + timeout

        while asyncio.get_event_loop().time() < deadline:
            state = self._tasks.get(task_id)
            if not state:
                raise ValueError(f"Unknown task: {task_id}")

            if state.status == "completed":
                return state.result
            elif state.status == "failed":
                raise RuntimeError(state.error)

            await asyncio.sleep(0.1)

        raise asyncio.TimeoutError(f"Task {task_id} timed out")

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        state = self._tasks.get(task_id)
        if not state:
            return False

        if state.status == "pending":
            async with self._lock:
                state.status = "cancelled"
                state.completed_at = datetime.now()
            return True

        return False

    async def _worker_loop(self, worker_id: int) -> None:
        """Worker loop for processing tasks."""
        logger.debug(f"Worker {worker_id} started")

        while self._running:
            try:
                # Get task with timeout
                try:
                    priority, task_id, task = await asyncio.wait_for(
                        self._task_queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue

                # Process task
                state = self._tasks.get(task_id)
                if not state or state.status == "cancelled":
                    continue

                state.status = "running"
                state.started_at = datetime.now()

                try:
                    result = await self._execute_task(task)
                    state.result = result
                    state.status = "completed"
                except Exception as e:
                    state.error = str(e)
                    state.status = "failed"
                    logger.error(f"Task {task_id} failed: {e}")
                finally:
                    state.completed_at = datetime.now()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")

        logger.debug(f"Worker {worker_id} stopped")

    async def _execute_task(self, task: dict[str, Any]) -> Any:
        """Execute a single task."""
        # Create execution context
        context = ExecutionContext(
            task_id=task.get("id", ""),
            config=self.config,
        )

        # Get task type and dispatch
        task_type = task.get("type")
        handler = task.get("handler")

        if handler and callable(handler):
            return await handler(task, context)

        # Default: return task data
        return task.get("data")

    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        import uuid

        return f"task_{uuid.uuid4().hex[:12]}"

    def get_metrics(self) -> dict[str, Any]:
        """Get orchestrator metrics."""
        return {
            "running": self._running,
            "worker_count": len(self._workers),
            "total_tasks": len(self._tasks),
            "pending_tasks": self.pending_count,
            "running_tasks": self.running_count,
            "queue_size": self._task_queue.qsize(),
        }
