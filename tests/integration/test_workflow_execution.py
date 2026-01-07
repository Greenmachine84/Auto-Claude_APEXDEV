"""
Integration tests for Workflow Execution.

Tests the complete flow of workflow execution including step sequencing,
state management, conditional branching, and error handling.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from unittest.mock import AsyncMock, MagicMock


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Types of workflow steps."""
    ACTION = "action"
    DECISION = "decision"
    PARALLEL = "parallel"
    WAIT = "wait"
    SUBPROCESS = "subprocess"


class StepStatus(Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """Result of step execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """Definition of a workflow step."""
    id: str
    name: str
    step_type: StepType
    handler: Optional[Callable] = None
    condition: Optional[Callable[[dict], bool]] = None
    next_steps: list[str] = field(default_factory=list)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    timeout_seconds: float = 60.0
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowContext:
    """Context passed through workflow execution."""
    workflow_id: str
    variables: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    current_step: Optional[str] = None
    step_history: list[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def set_variable(self, key: str, value: Any) -> None:
        """Set a context variable."""
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self.variables.get(key, default)


@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow."""
    id: str
    name: str
    description: str
    steps: dict[str, WorkflowStep] = field(default_factory=dict)
    entry_step: Optional[str] = None
    version: str = "1.0.0"

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        self.steps[step.id] = step
        if self.entry_step is None:
            self.entry_step = step.id


class MockStepExecutor:
    """Executor for individual workflow steps."""

    def __init__(self):
        self.execution_count: dict[str, int] = {}
        self._step_results: dict[str, list[StepResult]] = {}
        self._delays: dict[str, float] = {}

    def set_result(self, step_id: str, results: list[StepResult]) -> None:
        """Set predefined results for a step."""
        self._step_results[step_id] = results.copy()

    def set_delay(self, step_id: str, delay_seconds: float) -> None:
        """Set execution delay for a step."""
        self._delays[step_id] = delay_seconds

    async def execute(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> StepResult:
        """Execute a workflow step."""
        self.execution_count[step.id] = self.execution_count.get(step.id, 0) + 1

        # Simulate delay
        if step.id in self._delays:
            import asyncio
            await asyncio.sleep(self._delays[step.id])

        # Check condition
        if step.condition and not step.condition(context.variables):
            return StepResult(
                success=True,
                output=None,
                metadata={"skipped": True}
            )

        # Return predefined result if available
        if step.id in self._step_results and self._step_results[step.id]:
            return self._step_results[step.id].pop(0)

        # Execute handler if available
        if step.handler:
            try:
                output = await step.handler(context) if asyncio.iscoroutinefunction(step.handler) else step.handler(context)
                return StepResult(success=True, output=output)
            except Exception as e:
                return StepResult(success=False, error=str(e))

        # Default success
        return StepResult(success=True, output=f"Executed {step.name}")


class MockWorkflowEngine:
    """Engine for executing workflows."""

    def __init__(self, step_executor: MockStepExecutor):
        self.step_executor = step_executor
        self.active_workflows: dict[str, WorkflowContext] = {}
        self._event_handlers: dict[str, list[Callable]] = {}
        self._pause_requested: set[str] = set()
        self._cancel_requested: set[str] = set()

    def on_event(self, event: str, handler: Callable) -> None:
        """Register event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def _emit(self, event: str, data: Any) -> None:
        """Emit an event."""
        for handler in self._event_handlers.get(event, []):
            handler(data)

    async def start(
        self,
        definition: WorkflowDefinition,
        initial_context: Optional[dict] = None
    ) -> WorkflowContext:
        """Start workflow execution."""
        context = WorkflowContext(
            workflow_id=definition.id,
            variables=initial_context or {},
            started_at=datetime.now()
        )
        self.active_workflows[definition.id] = context
        self._emit("workflow_started", {"workflow_id": definition.id})

        try:
            await self._execute_from(definition, definition.entry_step, context)
            context.completed_at = datetime.now()
            self._emit("workflow_completed", {"workflow_id": definition.id})
        except Exception as e:
            self._emit("workflow_failed", {"workflow_id": definition.id, "error": str(e)})
            raise

        return context

    async def _execute_from(
        self,
        definition: WorkflowDefinition,
        step_id: str,
        context: WorkflowContext
    ) -> None:
        """Execute workflow from a specific step."""
        import asyncio

        while step_id:
            # Check for pause/cancel
            if context.workflow_id in self._pause_requested:
                self._emit("workflow_paused", {"workflow_id": context.workflow_id})
                return

            if context.workflow_id in self._cancel_requested:
                self._emit("workflow_cancelled", {"workflow_id": context.workflow_id})
                raise RuntimeError("Workflow cancelled")

            step = definition.steps.get(step_id)
            if not step:
                break

            context.current_step = step_id
            context.step_history.append(step_id)
            self._emit("step_started", {"step_id": step_id})

            # Execute with retries
            result = None
            for attempt in range(step.max_retries + 1):
                result = await self.step_executor.execute(step, context)
                if result.success:
                    break
                step.retry_count = attempt + 1

            context.results[step_id] = result
            self._emit("step_completed", {"step_id": step_id, "result": result})

            # Determine next step
            if result.success:
                if result.metadata.get("skipped"):
                    step_id = step.next_steps[0] if step.next_steps else None
                elif step.step_type == StepType.DECISION:
                    # Decision step - output determines next step
                    step_id = result.output
                elif step.on_success:
                    step_id = step.on_success
                elif step.next_steps:
                    step_id = step.next_steps[0]
                else:
                    step_id = None
            else:
                if step.on_failure:
                    step_id = step.on_failure
                else:
                    raise RuntimeError(f"Step {step_id} failed: {result.error}")

    async def pause(self, workflow_id: str) -> bool:
        """Request workflow pause."""
        if workflow_id in self.active_workflows:
            self._pause_requested.add(workflow_id)
            return True
        return False

    async def resume(self, workflow_id: str, step_id: str) -> bool:
        """Resume paused workflow from step."""
        if workflow_id in self._pause_requested:
            self._pause_requested.discard(workflow_id)
            return True
        return False

    async def cancel(self, workflow_id: str) -> bool:
        """Request workflow cancellation."""
        if workflow_id in self.active_workflows:
            self._cancel_requested.add(workflow_id)
            return True
        return False


import asyncio


# ============================================================================
# Test Classes
# ============================================================================

class TestWorkflowExecution:
    """Tests for basic workflow execution."""

    @pytest.fixture
    def step_executor(self) -> MockStepExecutor:
        """Create step executor."""
        return MockStepExecutor()

    @pytest.fixture
    def engine(self, step_executor: MockStepExecutor) -> MockWorkflowEngine:
        """Create workflow engine."""
        return MockWorkflowEngine(step_executor)

    @pytest.fixture
    def simple_workflow(self) -> WorkflowDefinition:
        """Create simple sequential workflow."""
        workflow = WorkflowDefinition(
            id="simple-workflow",
            name="Simple Workflow",
            description="A simple test workflow"
        )
        workflow.add_step(WorkflowStep(
            id="step1",
            name="Step 1",
            step_type=StepType.ACTION,
            next_steps=["step2"]
        ))
        workflow.add_step(WorkflowStep(
            id="step2",
            name="Step 2",
            step_type=StepType.ACTION,
            next_steps=["step3"]
        ))
        workflow.add_step(WorkflowStep(
            id="step3",
            name="Step 3",
            step_type=StepType.ACTION
        ))
        return workflow

    @pytest.mark.asyncio
    async def test_sequential_execution(
        self,
        engine: MockWorkflowEngine,
        simple_workflow: WorkflowDefinition
    ):
        """Test sequential step execution."""
        context = await engine.start(simple_workflow)

        assert len(context.step_history) == 3
        assert context.step_history == ["step1", "step2", "step3"]
        assert all(r.success for r in context.results.values())

    @pytest.mark.asyncio
    async def test_context_variables(
        self,
        engine: MockWorkflowEngine,
        step_executor: MockStepExecutor
    ):
        """Test context variables passed through workflow."""
        workflow = WorkflowDefinition(
            id="var-workflow",
            name="Variable Workflow",
            description="Tests variables"
        )

        def set_var(ctx: WorkflowContext):
            ctx.set_variable("computed", ctx.get_variable("input", 0) * 2)
            return ctx.get_variable("computed")

        workflow.add_step(WorkflowStep(
            id="compute",
            name="Compute",
            step_type=StepType.ACTION,
            handler=set_var
        ))

        context = await engine.start(workflow, {"input": 21})

        assert context.get_variable("computed") == 42

    @pytest.mark.asyncio
    async def test_workflow_completion_time(
        self,
        engine: MockWorkflowEngine,
        simple_workflow: WorkflowDefinition
    ):
        """Test workflow timing is recorded."""
        context = await engine.start(simple_workflow)

        assert context.started_at is not None
        assert context.completed_at is not None
        assert context.completed_at >= context.started_at


class TestConditionalExecution:
    """Tests for conditional workflow execution."""

    @pytest.fixture
    def step_executor(self) -> MockStepExecutor:
        """Create step executor."""
        return MockStepExecutor()

    @pytest.fixture
    def engine(self, step_executor: MockStepExecutor) -> MockWorkflowEngine:
        """Create workflow engine."""
        return MockWorkflowEngine(step_executor)

    @pytest.mark.asyncio
    async def test_decision_step(self, engine: MockWorkflowEngine):
        """Test decision step routes based on output."""
        workflow = WorkflowDefinition(
            id="decision-workflow",
            name="Decision Workflow",
            description="Tests decision routing"
        )

        def decide(ctx: WorkflowContext) -> str:
            return "path_a" if ctx.get_variable("choose_a") else "path_b"

        workflow.add_step(WorkflowStep(
            id="decision",
            name="Decision",
            step_type=StepType.DECISION,
            handler=decide
        ))
        workflow.add_step(WorkflowStep(
            id="path_a",
            name="Path A",
            step_type=StepType.ACTION
        ))
        workflow.add_step(WorkflowStep(
            id="path_b",
            name="Path B",
            step_type=StepType.ACTION
        ))

        context = await engine.start(workflow, {"choose_a": True})

        assert "path_a" in context.step_history
        assert "path_b" not in context.step_history

    @pytest.mark.asyncio
    async def test_conditional_skip(
        self,
        engine: MockWorkflowEngine,
        step_executor: MockStepExecutor
    ):
        """Test conditional step skipping."""
        workflow = WorkflowDefinition(
            id="skip-workflow",
            name="Skip Workflow",
            description="Tests conditional skip"
        )
        workflow.add_step(WorkflowStep(
            id="always",
            name="Always Run",
            step_type=StepType.ACTION,
            next_steps=["conditional"]
        ))
        workflow.add_step(WorkflowStep(
            id="conditional",
            name="Conditional",
            step_type=StepType.ACTION,
            condition=lambda v: v.get("run_conditional", False),
            next_steps=["final"]
        ))
        workflow.add_step(WorkflowStep(
            id="final",
            name="Final",
            step_type=StepType.ACTION
        ))

        context = await engine.start(workflow, {"run_conditional": False})

        assert "conditional" in context.step_history
        assert context.results["conditional"].metadata.get("skipped") is True


class TestErrorHandling:
    """Tests for workflow error handling."""

    @pytest.fixture
    def step_executor(self) -> MockStepExecutor:
        """Create step executor."""
        return MockStepExecutor()

    @pytest.fixture
    def engine(self, step_executor: MockStepExecutor) -> MockWorkflowEngine:
        """Create workflow engine."""
        return MockWorkflowEngine(step_executor)

    @pytest.mark.asyncio
    async def test_step_failure_with_handler(
        self,
        engine: MockWorkflowEngine,
        step_executor: MockStepExecutor
    ):
        """Test step failure routes to failure handler."""
        workflow = WorkflowDefinition(
            id="failure-workflow",
            name="Failure Workflow",
            description="Tests failure handling"
        )
        workflow.add_step(WorkflowStep(
            id="risky",
            name="Risky Step",
            step_type=StepType.ACTION,
            on_failure="error_handler"
        ))
        workflow.add_step(WorkflowStep(
            id="error_handler",
            name="Error Handler",
            step_type=StepType.ACTION
        ))

        step_executor.set_result("risky", [
            StepResult(success=False, error="Simulated failure")
        ])

        context = await engine.start(workflow)

        assert "risky" in context.step_history
        assert "error_handler" in context.step_history

    @pytest.mark.asyncio
    async def test_step_failure_without_handler(
        self,
        engine: MockWorkflowEngine,
        step_executor: MockStepExecutor
    ):
        """Test step failure raises when no handler."""
        workflow = WorkflowDefinition(
            id="unhandled-workflow",
            name="Unhandled Failure",
            description="Tests unhandled failure"
        )
        workflow.add_step(WorkflowStep(
            id="failing",
            name="Failing Step",
            step_type=StepType.ACTION
        ))

        step_executor.set_result("failing", [
            StepResult(success=False, error="Unhandled failure")
        ])

        with pytest.raises(RuntimeError) as exc_info:
            await engine.start(workflow)

        assert "failing" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retry_on_failure(
        self,
        engine: MockWorkflowEngine,
        step_executor: MockStepExecutor
    ):
        """Test step retry on failure."""
        workflow = WorkflowDefinition(
            id="retry-workflow",
            name="Retry Workflow",
            description="Tests retry logic"
        )
        workflow.add_step(WorkflowStep(
            id="flaky",
            name="Flaky Step",
            step_type=StepType.ACTION,
            max_retries=3
        ))

        step_executor.set_result("flaky", [
            StepResult(success=False, error="Attempt 1"),
            StepResult(success=False, error="Attempt 2"),
            StepResult(success=True, output="Success on attempt 3")
        ])

        context = await engine.start(workflow)

        assert context.results["flaky"].success is True
        assert step_executor.execution_count["flaky"] == 3


class TestWorkflowEvents:
    """Tests for workflow event handling."""

    @pytest.fixture
    def step_executor(self) -> MockStepExecutor:
        """Create step executor."""
        return MockStepExecutor()

    @pytest.fixture
    def engine(self, step_executor: MockStepExecutor) -> MockWorkflowEngine:
        """Create workflow engine."""
        return MockWorkflowEngine(step_executor)

    @pytest.mark.asyncio
    async def test_events_emitted(self, engine: MockWorkflowEngine):
        """Test workflow events are emitted."""
        events = []

        engine.on_event("workflow_started", lambda d: events.append(("started", d)))
        engine.on_event("step_started", lambda d: events.append(("step", d)))
        engine.on_event("workflow_completed", lambda d: events.append(("completed", d)))

        workflow = WorkflowDefinition(
            id="event-workflow",
            name="Event Workflow",
            description="Tests events"
        )
        workflow.add_step(WorkflowStep(
            id="step1",
            name="Step 1",
            step_type=StepType.ACTION
        ))

        await engine.start(workflow)

        event_types = [e[0] for e in events]
        assert "started" in event_types
        assert "step" in event_types
        assert "completed" in event_types


class TestWorkflowControl:
    """Tests for workflow pause/resume/cancel."""

    @pytest.fixture
    def step_executor(self) -> MockStepExecutor:
        """Create step executor with delays."""
        executor = MockStepExecutor()
        executor.set_delay("slow_step", 0.1)
        return executor

    @pytest.fixture
    def engine(self, step_executor: MockStepExecutor) -> MockWorkflowEngine:
        """Create workflow engine."""
        return MockWorkflowEngine(step_executor)

    @pytest.mark.asyncio
    async def test_cancel_workflow(self, engine: MockWorkflowEngine):
        """Test workflow cancellation."""
        workflow = WorkflowDefinition(
            id="cancel-workflow",
            name="Cancel Workflow",
            description="Tests cancellation"
        )
        workflow.add_step(WorkflowStep(
            id="slow_step",
            name="Slow Step",
            step_type=StepType.ACTION,
            next_steps=["never_reached"]
        ))
        workflow.add_step(WorkflowStep(
            id="never_reached",
            name="Never Reached",
            step_type=StepType.ACTION
        ))

        # Request cancel before start
        await engine.cancel("cancel-workflow")
        engine.active_workflows["cancel-workflow"] = WorkflowContext(
            workflow_id="cancel-workflow"
        )

        with pytest.raises(RuntimeError) as exc_info:
            await engine.start(workflow)

        assert "cancelled" in str(exc_info.value).lower()


class TestComplexWorkflows:
    """Tests for complex workflow patterns."""

    @pytest.fixture
    def step_executor(self) -> MockStepExecutor:
        """Create step executor."""
        return MockStepExecutor()

    @pytest.fixture
    def engine(self, step_executor: MockStepExecutor) -> MockWorkflowEngine:
        """Create workflow engine."""
        return MockWorkflowEngine(step_executor)

    @pytest.mark.asyncio
    async def test_success_path_routing(
        self,
        engine: MockWorkflowEngine,
        step_executor: MockStepExecutor
    ):
        """Test on_success routing."""
        workflow = WorkflowDefinition(
            id="success-routing",
            name="Success Routing",
            description="Tests success routing"
        )
        workflow.add_step(WorkflowStep(
            id="start",
            name="Start",
            step_type=StepType.ACTION,
            on_success="success_handler",
            on_failure="failure_handler"
        ))
        workflow.add_step(WorkflowStep(
            id="success_handler",
            name="Success Handler",
            step_type=StepType.ACTION
        ))
        workflow.add_step(WorkflowStep(
            id="failure_handler",
            name="Failure Handler",
            step_type=StepType.ACTION
        ))

        context = await engine.start(workflow)

        assert "success_handler" in context.step_history
        assert "failure_handler" not in context.step_history

    @pytest.mark.asyncio
    async def test_workflow_with_computed_routing(
        self,
        engine: MockWorkflowEngine
    ):
        """Test workflow with computed routing decisions."""
        workflow = WorkflowDefinition(
            id="computed-routing",
            name="Computed Routing",
            description="Tests computed routing"
        )

        def router(ctx: WorkflowContext) -> str:
            score = ctx.get_variable("score", 0)
            if score >= 90:
                return "excellent"
            elif score >= 70:
                return "good"
            else:
                return "needs_improvement"

        workflow.add_step(WorkflowStep(
            id="evaluate",
            name="Evaluate",
            step_type=StepType.DECISION,
            handler=router
        ))
        workflow.add_step(WorkflowStep(
            id="excellent",
            name="Excellent",
            step_type=StepType.ACTION
        ))
        workflow.add_step(WorkflowStep(
            id="good",
            name="Good",
            step_type=StepType.ACTION
        ))
        workflow.add_step(WorkflowStep(
            id="needs_improvement",
            name="Needs Improvement",
            step_type=StepType.ACTION
        ))

        context = await engine.start(workflow, {"score": 85})

        assert "good" in context.step_history
        assert "excellent" not in context.step_history
        assert "needs_improvement" not in context.step_history
