"""Task queue implementation.

Priority-based task queue with persistence.

Capabilities:
- Priority ordering
- FIFO within priority
- Persistence support
- Metrics tracking
"""

import asyncio
import heapq
import logging
from datetime import datetime
from typing import Any

from orchestrator.queue.metrics import QueueMetrics
from orchestrator.queue.persistence import QueuePersistence
from orchestrator.queue.task_model import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueue:
    """Priority-based task queue.

    Manages task scheduling with priority ordering.

    Example:
        queue = TaskQueue()
        await queue.put(task, priority=TaskPriority.HIGH)
        task = await queue.get()
    """

    def __init__(
        self,
        max_size: int = 1000,
        persistence: QueuePersistence | None = None,
    ):
        """Initialize queue."""
        self.max_size = max_size
        self.persistence = persistence
        self._heap: list[tuple[int, int, Task]] = []
        self._counter = 0
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)
        self._not_full = asyncio.Condition(self._lock)
        self._metrics = QueueMetrics()

        logger.debug(f"TaskQueue initialized with max_size={max_size}")

    @property
    def size(self) -> int:
        """Get current queue size."""
        return len(self._heap)

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self.size == 0

    @property
    def is_full(self) -> bool:
        """Check if queue is full."""
        return self.size >= self.max_size

    async def put(
        self,
        task: Task,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float | None = None,
    ) -> bool:
        """Add task to queue."""
        async with self._not_full:
            # Wait if full
            if timeout:
                await asyncio.wait_for(
                    self._wait_not_full(),
                    timeout=timeout,
                )
            else:
                while self.is_full:
                    await self._not_full.wait()

            # Add to heap
            self._counter += 1
            entry = (priority.value, self._counter, task)
            heapq.heappush(self._heap, entry)

            # Persist if enabled
            if self.persistence:
                await self.persistence.save_task(task)

            # Update metrics
            self._metrics.tasks_enqueued += 1
            self._metrics.current_size = self.size

            self._not_empty.notify()

            logger.debug(f"Task {task.id} added with priority {priority}")
            return True

    async def get(self, timeout: float | None = None) -> Task | None:
        """Get next task from queue."""
        async with self._not_empty:
            # Wait if empty
            if timeout:
                await asyncio.wait_for(
                    self._wait_not_empty(),
                    timeout=timeout,
                )
            else:
                while self.is_empty:
                    await self._not_empty.wait()

            # Get from heap
            if self._heap:
                _, _, task = heapq.heappop(self._heap)
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()

                # Update metrics
                self._metrics.tasks_dequeued += 1
                self._metrics.current_size = self.size

                self._not_full.notify()

                logger.debug(f"Task {task.id} dequeued")
                return task

            return None

    async def peek(self) -> Task | None:
        """Peek at next task without removing."""
        async with self._lock:
            if self._heap:
                _, _, task = self._heap[0]
                return task
            return None

    async def remove(self, task_id: str) -> bool:
        """Remove task by ID."""
        async with self._lock:
            for i, (_, _, task) in enumerate(self._heap):
                if task.id == task_id:
                    del self._heap[i]
                    heapq.heapify(self._heap)

                    self._metrics.tasks_cancelled += 1
                    self._metrics.current_size = self.size

                    logger.debug(f"Task {task_id} removed")
                    return True
            return False

    async def clear(self) -> int:
        """Clear all tasks from queue."""
        async with self._lock:
            count = len(self._heap)
            self._heap.clear()
            self._metrics.current_size = 0
            return count

    async def _wait_not_full(self) -> None:
        """Wait until not full."""
        while self.is_full:
            await self._not_full.wait()

    async def _wait_not_empty(self) -> None:
        """Wait until not empty."""
        while self.is_empty:
            await self._not_empty.wait()

    def get_metrics(self) -> dict[str, Any]:
        """Get queue metrics."""
        return self._metrics.to_dict()
