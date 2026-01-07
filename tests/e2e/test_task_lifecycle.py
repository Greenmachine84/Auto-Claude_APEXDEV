"""
End-to-end tests for task lifecycle.

Tests complete task lifecycle from creation through completion,
including state management, persistence, and event handling.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import asyncio


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskState(Enum):
    """Task lifecycle states."""
    DRAFT = "draft"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TaskEvent(Enum):
    """Task lifecycle events."""
    CREATED = "created"
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    STARTED = "started"
    PAUSED = "paused"
    RESUMED = "resumed"
    BLOCKED = "blocked"
    UNBLOCKED = "unblocked"
    SUBMITTED_FOR_REVIEW = "submitted_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class TaskDefinition:
    """Task definition with metadata."""
    id: str
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class TaskInstance:
    """Runtime task instance with state."""
    definition: TaskDefinition
    state: TaskState = TaskState.DRAFT
    assignee: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    blocked_by: Optional[str] = None
    output: Any = None
    error: Optional[str] = None
    event_log: list[dict] = field(default_factory=list)

    def log_event(self, event: TaskEvent, details: str = "") -> None:
        """Log a task event."""
        self.event_log.append({
            "event": event.value,
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
            "details": details
        })


# Valid state transitions
VALID_TRANSITIONS: dict[TaskState, list[TaskState]] = {
    TaskState.DRAFT: [TaskState.QUEUED, TaskState.CANCELLED],
    TaskState.QUEUED: [TaskState.ASSIGNED, TaskState.CANCELLED],
    TaskState.ASSIGNED: [TaskState.RUNNING, TaskState.CANCELLED],
    TaskState.RUNNING: [TaskState.PAUSED, TaskState.BLOCKED, TaskState.REVIEW,
                        TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED],
    TaskState.PAUSED: [TaskState.RUNNING, TaskState.CANCELLED],
    TaskState.BLOCKED: [TaskState.RUNNING, TaskState.CANCELLED],
    TaskState.REVIEW: [TaskState.RUNNING, TaskState.COMPLETED, TaskState.CANCELLED],
    TaskState.COMPLETED: [],
    TaskState.CANCELLED: [],
    TaskState.FAILED: [TaskState.QUEUED],  # Can retry
}


class MockTaskQueue:
    """Mock task queue for scheduling."""

    def __init__(self):
        self.tasks: dict[str, TaskInstance] = {}
        self.queue: list[str] = []
        self._priority_queues: dict[TaskPriority, list[str]] = {
            p: [] for p in TaskPriority
        }

    def submit(self, task: TaskInstance) -> None:
        """Submit task to queue."""
        if task.state != TaskState.DRAFT:
            raise ValueError("Can only submit draft tasks")

        task.state = TaskState.QUEUED
        task.log_event(TaskEvent.SUBMITTED)
        self.tasks[task.definition.id] = task
        self._priority_queues[task.definition.priority].append(task.definition.id)

    def get_next(self) -> Optional[TaskInstance]:
        """Get next task by priority."""
        for priority in reversed(TaskPriority):
            queue = self._priority_queues[priority]
            while queue:
                task_id = queue.pop(0)
                task = self.tasks.get(task_id)
                if task and task.state == TaskState.QUEUED:
                    return task
        return None


class MockTaskExecutor:
    """Mock task executor."""

    def __init__(self):
        self.active_tasks: dict[str, TaskInstance] = {}
        self.completed_tasks: list[str] = []
        self._results: dict[str, Any] = {}

    def set_result(self, task_id: str, result: Any) -> None:
        """Set expected result for task."""
        self._results[task_id] = result

    def assign(self, task: TaskInstance, assignee: str) -> None:
        """Assign task to executor."""
        if task.state != TaskState.QUEUED:
            raise ValueError("Can only assign queued tasks")

        task.state = TaskState.ASSIGNED
        task.assignee = assignee
        task.log_event(TaskEvent.ASSIGNED, f"Assigned to {assignee}")
        self.active_tasks[task.definition.id] = task

    async def start(self, task: TaskInstance) -> None:
        """Start task execution."""
        if task.state != TaskState.ASSIGNED:
            raise ValueError("Can only start assigned tasks")

        task.state = TaskState.RUNNING
        task.started_at = datetime.now()
        task.log_event(TaskEvent.STARTED)

    async def execute(self, task: TaskInstance) -> Any:
        """Execute task to completion."""
        if task.state != TaskState.RUNNING:
            raise ValueError("Task must be running")

        result = self._results.get(task.definition.id, "default_result")

        if isinstance(result, Exception):
            task.state = TaskState.FAILED
            task.error = str(result)
            task.log_event(TaskEvent.FAILED, str(result))
            raise result

        task.output = result
        return result

    def pause(self, task: TaskInstance, reason: str = "") -> None:
        """Pause task execution."""
        if task.state != TaskState.RUNNING:
            raise ValueError("Can only pause running tasks")

        task.state = TaskState.PAUSED
        task.log_event(TaskEvent.PAUSED, reason)

    def resume(self, task: TaskInstance) -> None:
        """Resume paused task."""
        if task.state != TaskState.PAUSED:
            raise ValueError("Can only resume paused tasks")

        task.state = TaskState.RUNNING
        task.log_event(TaskEvent.RESUMED)

    def block(self, task: TaskInstance, blocker: str) -> None:
        """Block task on dependency."""
        if task.state != TaskState.RUNNING:
            raise ValueError("Can only block running tasks")

        task.state = TaskState.BLOCKED
        task.blocked_by = blocker
        task.log_event(TaskEvent.BLOCKED, f"Blocked by {blocker}")

    def unblock(self, task: TaskInstance) -> None:
        """Unblock task."""
        if task.state != TaskState.BLOCKED:
            raise ValueError("Can only unblock blocked tasks")

        task.state = TaskState.RUNNING
        task.blocked_by = None
        task.log_event(TaskEvent.UNBLOCKED)


class MockTaskManager:
    """Complete task lifecycle manager."""

    def __init__(self):
        self.queue = MockTaskQueue()
        self.executor = MockTaskExecutor()
        self.reviewers: dict[str, Callable] = {}
        self._event_handlers: dict[TaskEvent, list[Callable]] = {}

    def on_event(self, event: TaskEvent, handler: Callable) -> None:
        """Register event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def register_reviewer(self, name: str, reviewer: Callable) -> None:
        """Register a task reviewer."""
        self.reviewers[name] = reviewer

    def create_task(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> TaskInstance:
        """Create a new task."""
        definition = TaskDefinition(
            id=task_id,
            title=title,
            description=description,
            priority=priority
        )
        task = TaskInstance(definition=definition)
        task.log_event(TaskEvent.CREATED)
        return task

    async def run_full_lifecycle(
        self,
        task: TaskInstance,
        assignee: str = "default"
    ) -> TaskInstance:
        """Run task through complete lifecycle."""
        # Submit to queue
        self.queue.submit(task)

        # Assign
        self.executor.assign(task, assignee)

        # Start
        await self.executor.start(task)

        # Execute
        try:
            await self.executor.execute(task)

            # Review
            task.state = TaskState.REVIEW
            task.log_event(TaskEvent.SUBMITTED_FOR_REVIEW)

            # Auto-approve for testing
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.now()
            task.log_event(TaskEvent.COMPLETED)

        except Exception:
            pass  # Error already logged

        return task


# ============================================================================
# Test Classes
# ============================================================================

class TestTaskCreation:
    """Tests for task creation."""

    def test_create_task(self):
        """Test basic task creation."""
        manager = MockTaskManager()
        task = manager.create_task("t1", "Test Task", "Description")

        assert task.definition.id == "t1"
        assert task.state == TaskState.DRAFT
        assert len(task.event_log) == 1
        assert task.event_log[0]["event"] == TaskEvent.CREATED.value

    def test_create_task_with_priority(self):
        """Test task creation with priority."""
        manager = MockTaskManager()
        task = manager.create_task(
            "t2", "High Priority", "Urgent",
            priority=TaskPriority.CRITICAL
        )

        assert task.definition.priority == TaskPriority.CRITICAL


class TestTaskQueue:
    """Tests for task queuing."""

    @pytest.fixture
    def queue(self) -> MockTaskQueue:
        """Create test queue."""
        return MockTaskQueue()

    def test_submit_task(self, queue: MockTaskQueue):
        """Test submitting task to queue."""
        definition = TaskDefinition(id="q1", title="Q1", description="Queued")
        task = TaskInstance(definition=definition)

        queue.submit(task)

        assert task.state == TaskState.QUEUED
        assert "q1" in queue.tasks

    def test_priority_ordering(self, queue: MockTaskQueue):
        """Test tasks returned by priority."""
        low = TaskInstance(
            definition=TaskDefinition(id="low", title="Low", description="",
                                      priority=TaskPriority.LOW)
        )
        high = TaskInstance(
            definition=TaskDefinition(id="high", title="High", description="",
                                      priority=TaskPriority.HIGH)
        )

        queue.submit(low)
        queue.submit(high)

        next_task = queue.get_next()
        assert next_task.definition.id == "high"


class TestTaskExecution:
    """Tests for task execution."""

    @pytest.fixture
    def executor(self) -> MockTaskExecutor:
        """Create test executor."""
        return MockTaskExecutor()

    @pytest.fixture
    def running_task(self, executor: MockTaskExecutor) -> TaskInstance:
        """Create running task."""
        task = TaskInstance(
            definition=TaskDefinition(id="run1", title="Running", description="")
        )
        task.state = TaskState.QUEUED
        executor.assign(task, "agent1")
        return task

    @pytest.mark.asyncio
    async def test_start_task(self, executor: MockTaskExecutor, running_task: TaskInstance):
        """Test starting a task."""
        await executor.start(running_task)

        assert running_task.state == TaskState.RUNNING
        assert running_task.started_at is not None

    @pytest.mark.asyncio
    async def test_execute_task(self, executor: MockTaskExecutor, running_task: TaskInstance):
        """Test executing a task."""
        executor.set_result("run1", {"success": True})
        await executor.start(running_task)

        result = await executor.execute(running_task)

        assert result == {"success": True}
        assert running_task.output == {"success": True}


class TestTaskPauseResume:
    """Tests for pause/resume functionality."""

    @pytest.fixture
    async def running_task(self) -> TaskInstance:
        """Create running task."""
        task = TaskInstance(
            definition=TaskDefinition(id="pr1", title="Pause Test", description="")
        )
        task.state = TaskState.RUNNING
        return task

    @pytest.mark.asyncio
    async def test_pause_task(self, running_task: TaskInstance):
        """Test pausing a task."""
        executor = MockTaskExecutor()
        executor.pause(running_task, "User requested pause")

        assert running_task.state == TaskState.PAUSED

    @pytest.mark.asyncio
    async def test_resume_task(self, running_task: TaskInstance):
        """Test resuming a paused task."""
        executor = MockTaskExecutor()
        executor.pause(running_task)
        executor.resume(running_task)

        assert running_task.state == TaskState.RUNNING


class TestTaskBlocking:
    """Tests for task blocking/unblocking."""

    @pytest.fixture
    def executor(self) -> MockTaskExecutor:
        """Create test executor."""
        return MockTaskExecutor()

    def test_block_task(self, executor: MockTaskExecutor):
        """Test blocking a task."""
        task = TaskInstance(
            definition=TaskDefinition(id="b1", title="Block Test", description="")
        )
        task.state = TaskState.RUNNING

        executor.block(task, "dependency-123")

        assert task.state == TaskState.BLOCKED
        assert task.blocked_by == "dependency-123"

    def test_unblock_task(self, executor: MockTaskExecutor):
        """Test unblocking a task."""
        task = TaskInstance(
            definition=TaskDefinition(id="b2", title="Unblock Test", description="")
        )
        task.state = TaskState.RUNNING
        executor.block(task, "blocker")
        executor.unblock(task)

        assert task.state == TaskState.RUNNING
        assert task.blocked_by is None


class TestFullLifecycle:
    """Tests for complete task lifecycle."""

    @pytest.fixture
    def manager(self) -> MockTaskManager:
        """Create task manager."""
        return MockTaskManager()

    @pytest.mark.asyncio
    async def test_complete_lifecycle(self, manager: MockTaskManager):
        """Test complete task lifecycle."""
        task = manager.create_task("lc1", "Lifecycle Test", "Full lifecycle")
        manager.executor.set_result("lc1", "completed")

        result = await manager.run_full_lifecycle(task)

        assert result.state == TaskState.COMPLETED
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_lifecycle_events_logged(self, manager: MockTaskManager):
        """Test all lifecycle events are logged."""
        task = manager.create_task("lc2", "Event Test", "Event logging")
        manager.executor.set_result("lc2", "done")

        await manager.run_full_lifecycle(task)

        events = [e["event"] for e in task.event_log]
        assert TaskEvent.CREATED.value in events
        assert TaskEvent.SUBMITTED.value in events


class TestStateTransitions:
    """Tests for state transition validation."""

    def test_valid_transitions(self):
        """Test valid state transitions are defined."""
        # Draft can only go to queued or cancelled
        assert TaskState.QUEUED in VALID_TRANSITIONS[TaskState.DRAFT]
        assert TaskState.CANCELLED in VALID_TRANSITIONS[TaskState.DRAFT]

        # Completed has no valid transitions
        assert len(VALID_TRANSITIONS[TaskState.COMPLETED]) == 0

    def test_failed_can_retry(self):
        """Test failed tasks can be requeued."""
        assert TaskState.QUEUED in VALID_TRANSITIONS[TaskState.FAILED]


class TestErrorHandling:
    """Tests for error handling in lifecycle."""

    @pytest.fixture
    def manager(self) -> MockTaskManager:
        """Create task manager."""
        return MockTaskManager()

    @pytest.mark.asyncio
    async def test_task_failure(self, manager: MockTaskManager):
        """Test task failure is handled."""
        task = manager.create_task("err1", "Error Test", "Will fail")
        manager.executor.set_result("err1", ValueError("Execution failed"))

        result = await manager.run_full_lifecycle(task)

        assert result.state == TaskState.FAILED
        assert "Execution failed" in result.error
