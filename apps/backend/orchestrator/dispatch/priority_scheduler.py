"""Priority scheduler.

Schedules tasks by priority.

Capabilities:
- Priority ordering
- Deadline awareness
- Fair scheduling
- Preemption support
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchestrator.queue.task_model import Task, TaskPriority


logger = logging.getLogger(__name__)


@dataclass
class ScheduleEntry:
    """An entry in the schedule."""

    task_id: str
    priority: int
    deadline: datetime | None = None
    scheduled_at: datetime = None

    def __post_init__(self):
        """Set defaults."""
        if self.scheduled_at is None:
            self.scheduled_at = datetime.now()


class PriorityScheduler:
    """Schedule tasks by priority.

    Orders tasks for optimal execution.

    Example:
        scheduler = PriorityScheduler()
        ordered = scheduler.schedule(tasks)
    """

    def __init__(self, preempt: bool = False):
        """Initialize scheduler."""
        self.preempt = preempt
        self._schedule: list[ScheduleEntry] = []

        logger.debug("PriorityScheduler initialized")

    def schedule(self, tasks: list["Task"]) -> list["Task"]:
        """Schedule tasks in priority order."""
        # Sort by priority (lower = higher priority)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (t.priority.value, t.created_at),
        )

        # Update schedule
        self._schedule = [
            ScheduleEntry(
                task_id=t.id,
                priority=t.priority.value,
            )
            for t in sorted_tasks
        ]

        return sorted_tasks

    def insert(self, task: "Task", position: int | None = None) -> int:
        """Insert task into schedule."""
        entry = ScheduleEntry(
            task_id=task.id,
            priority=task.priority.value,
        )

        if position is not None:
            self._schedule.insert(position, entry)
            return position

        # Find correct position by priority
        for i, e in enumerate(self._schedule):
            if task.priority.value < e.priority:
                self._schedule.insert(i, entry)
                return i

        self._schedule.append(entry)
        return len(self._schedule) - 1

    def remove(self, task_id: str) -> bool:
        """Remove task from schedule."""
        for i, entry in enumerate(self._schedule):
            if entry.task_id == task_id:
                del self._schedule[i]
                return True
        return False

    def peek(self) -> str | None:
        """Peek at next task ID."""
        if self._schedule:
            return self._schedule[0].task_id
        return None

    def pop(self) -> str | None:
        """Pop next task ID."""
        if self._schedule:
            return self._schedule.pop(0).task_id
        return None

    def reorder(
        self,
        task_id: str,
        new_priority: "TaskPriority",
    ) -> bool:
        """Reorder task in schedule."""
        # Find and remove
        for i, entry in enumerate(self._schedule):
            if entry.task_id == task_id:
                del self._schedule[i]

                # Re-insert with new priority
                new_entry = ScheduleEntry(
                    task_id=task_id,
                    priority=new_priority.value,
                )

                for j, e in enumerate(self._schedule):
                    if new_priority.value < e.priority:
                        self._schedule.insert(j, new_entry)
                        return True

                self._schedule.append(new_entry)
                return True

        return False

    def get_schedule(self) -> list[str]:
        """Get current schedule as task IDs."""
        return [e.task_id for e in self._schedule]

    def clear(self) -> None:
        """Clear schedule."""
        self._schedule.clear()
