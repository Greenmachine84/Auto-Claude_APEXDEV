"""
End-to-end tests for full agent workflow.

Tests complete agent workflows from task assignment to completion,
including multi-agent coordination and tool usage.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock
import asyncio


class AgentType(Enum):
    """Agent types in the system."""
    CODER = "coder"
    REVIEWER = "reviewer"
    FIXER = "fixer"
    PLANNER = "planner"
    TESTER = "tester"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    FIXING = "fixing"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowPhase(Enum):
    """Phases in the agent workflow."""
    PLANNING = "planning"
    CODING = "coding"
    REVIEW = "review"
    FIXING = "fixing"
    TESTING = "testing"
    COMPLETION = "completion"


@dataclass
class Task:
    """Task representation for workflow."""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[AgentType] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    history: list[dict] = field(default_factory=list)

    def transition(self, new_status: TaskStatus, details: str = "") -> None:
        """Transition task to new status."""
        self.history.append({
            "from": self.status.value,
            "to": new_status.value,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        self.status = new_status


@dataclass
class AgentAction:
    """An action taken by an agent."""
    agent_type: AgentType
    action: str
    input_data: Any
    output_data: Any
    duration_ms: float = 0.0
    success: bool = True


@dataclass
class WorkflowExecution:
    """Execution record for a workflow."""
    workflow_id: str
    task: Task
    current_phase: WorkflowPhase
    actions: list[AgentAction] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    artifacts: dict = field(default_factory=dict)


class MockAgent:
    """Mock agent for E2E testing."""

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.actions_taken: list[AgentAction] = []
        self._responses: dict[str, Any] = {}

    def set_response(self, action: str, response: Any) -> None:
        """Set predefined response for an action."""
        self._responses[action] = response

    async def execute(self, action: str, input_data: Any) -> Any:
        """Execute an action."""
        import time
        start = time.time()

        response = self._responses.get(action, f"Default response for {action}")

        action_record = AgentAction(
            agent_type=self.agent_type,
            action=action,
            input_data=input_data,
            output_data=response,
            duration_ms=(time.time() - start) * 1000
        )
        self.actions_taken.append(action_record)

        return response


class MockAgentOrchestrator:
    """Orchestrator for multi-agent workflows."""

    def __init__(self):
        self.agents: dict[AgentType, MockAgent] = {}
        self.executions: list[WorkflowExecution] = []
        self._workflow_hooks: dict[str, list] = {}

    def register_agent(self, agent: MockAgent) -> None:
        """Register an agent."""
        self.agents[agent.agent_type] = agent

    def on_phase(self, phase: WorkflowPhase, handler) -> None:
        """Register phase handler."""
        key = phase.value
        if key not in self._workflow_hooks:
            self._workflow_hooks[key] = []
        self._workflow_hooks[key].append(handler)

    async def execute_workflow(self, task: Task) -> WorkflowExecution:
        """Execute complete workflow for a task."""
        execution = WorkflowExecution(
            workflow_id=f"wf-{task.id}",
            task=task,
            current_phase=WorkflowPhase.PLANNING
        )
        self.executions.append(execution)

        try:
            # Phase 1: Planning
            await self._execute_phase(execution, WorkflowPhase.PLANNING)

            # Phase 2: Coding
            await self._execute_phase(execution, WorkflowPhase.CODING)

            # Phase 3: Review
            await self._execute_phase(execution, WorkflowPhase.REVIEW)

            # Phase 4: Fixing (if needed)
            if execution.artifacts.get("needs_fixes"):
                await self._execute_phase(execution, WorkflowPhase.FIXING)

            # Phase 5: Testing
            await self._execute_phase(execution, WorkflowPhase.TESTING)

            # Phase 6: Completion
            await self._execute_phase(execution, WorkflowPhase.COMPLETION)

            task.transition(TaskStatus.COMPLETED, "Workflow completed successfully")
            task.completed_at = datetime.now()
            execution.completed_at = datetime.now()

        except Exception as e:
            task.transition(TaskStatus.FAILED, str(e))
            raise

        return execution

    async def _execute_phase(
        self,
        execution: WorkflowExecution,
        phase: WorkflowPhase
    ) -> None:
        """Execute a workflow phase."""
        import asyncio as aio
        import inspect

        execution.current_phase = phase

        # Call phase hooks (may be sync or async)
        for handler in self._workflow_hooks.get(phase.value, []):
            result = handler(execution)
            if inspect.iscoroutine(result):
                await result

        # Execute phase-specific logic
        if phase == WorkflowPhase.PLANNING:
            planner = self.agents.get(AgentType.PLANNER)
            if planner:
                plan = await planner.execute("create_plan", execution.task.description)
                execution.artifacts["plan"] = plan
                execution.actions.append(planner.actions_taken[-1])

        elif phase == WorkflowPhase.CODING:
            coder = self.agents.get(AgentType.CODER)
            if coder:
                plan = execution.artifacts.get("plan", "No plan")
                code = await coder.execute("write_code", plan)
                execution.artifacts["code"] = code
                execution.actions.append(coder.actions_taken[-1])

        elif phase == WorkflowPhase.REVIEW:
            reviewer = self.agents.get(AgentType.REVIEWER)
            if reviewer:
                code = execution.artifacts.get("code", "")
                review = await reviewer.execute("review_code", code)
                execution.artifacts["review"] = review
                execution.artifacts["needs_fixes"] = "issues" in str(review).lower()
                execution.actions.append(reviewer.actions_taken[-1])

        elif phase == WorkflowPhase.FIXING:
            fixer = self.agents.get(AgentType.FIXER)
            if fixer:
                review = execution.artifacts.get("review", "")
                fixes = await fixer.execute("apply_fixes", review)
                execution.artifacts["fixes"] = fixes
                execution.actions.append(fixer.actions_taken[-1])

        elif phase == WorkflowPhase.TESTING:
            tester = self.agents.get(AgentType.TESTER)
            if tester:
                code = execution.artifacts.get("code", "")
                tests = await tester.execute("run_tests", code)
                execution.artifacts["test_results"] = tests
                execution.actions.append(tester.actions_taken[-1])

        elif phase == WorkflowPhase.COMPLETION:
            execution.artifacts["final_status"] = "completed"


# ============================================================================
# Test Classes
# ============================================================================

class TestFullWorkflowExecution:
    """Tests for complete workflow execution."""

    @pytest.fixture
    def orchestrator(self) -> MockAgentOrchestrator:
        """Create orchestrator with all agents."""
        orch = MockAgentOrchestrator()

        planner = MockAgent(AgentType.PLANNER)
        planner.set_response("create_plan", {"steps": ["step1", "step2"]})
        orch.register_agent(planner)

        coder = MockAgent(AgentType.CODER)
        coder.set_response("write_code", "def hello(): pass")
        orch.register_agent(coder)

        reviewer = MockAgent(AgentType.REVIEWER)
        reviewer.set_response("review_code", {"approved": True})
        orch.register_agent(reviewer)

        tester = MockAgent(AgentType.TESTER)
        tester.set_response("run_tests", {"passed": 5, "failed": 0})
        orch.register_agent(tester)

        return orch

    @pytest.mark.asyncio
    async def test_complete_workflow(self, orchestrator: MockAgentOrchestrator):
        """Test complete workflow executes all phases."""
        task = Task(id="task-1", title="Write Hello", description="Write hello function")

        execution = await orchestrator.execute_workflow(task)

        assert execution.completed_at is not None
        assert task.status == TaskStatus.COMPLETED
        assert "plan" in execution.artifacts
        assert "code" in execution.artifacts
        assert "review" in execution.artifacts
        assert "test_results" in execution.artifacts

    @pytest.mark.asyncio
    async def test_workflow_phases_in_order(self, orchestrator: MockAgentOrchestrator):
        """Test workflow phases execute in correct order."""
        phases_executed = []

        for phase in WorkflowPhase:
            orchestrator.on_phase(phase, lambda e, p=phase: phases_executed.append(p))

        task = Task(id="task-2", title="Test", description="Test task")
        await orchestrator.execute_workflow(task)

        # Should have planning, coding, review, testing, completion (no fixing)
        assert WorkflowPhase.PLANNING in phases_executed
        assert WorkflowPhase.CODING in phases_executed
        assert phases_executed.index(WorkflowPhase.CODING) > phases_executed.index(WorkflowPhase.PLANNING)


class TestWorkflowWithFixes:
    """Tests for workflow requiring fixes."""

    @pytest.fixture
    def orchestrator_with_issues(self) -> MockAgentOrchestrator:
        """Create orchestrator where review finds issues."""
        orch = MockAgentOrchestrator()

        planner = MockAgent(AgentType.PLANNER)
        planner.set_response("create_plan", {"steps": ["step1"]})
        orch.register_agent(planner)

        coder = MockAgent(AgentType.CODER)
        coder.set_response("write_code", "def buggy(): pass")
        orch.register_agent(coder)

        reviewer = MockAgent(AgentType.REVIEWER)
        reviewer.set_response("review_code", {"issues": ["Missing docstring"]})
        orch.register_agent(reviewer)

        fixer = MockAgent(AgentType.FIXER)
        fixer.set_response("apply_fixes", "def fixed(): '''Doc''' pass")
        orch.register_agent(fixer)

        tester = MockAgent(AgentType.TESTER)
        tester.set_response("run_tests", {"passed": 3, "failed": 0})
        orch.register_agent(tester)

        return orch

    @pytest.mark.asyncio
    async def test_fixing_phase_triggered(self, orchestrator_with_issues: MockAgentOrchestrator):
        """Test fixing phase is triggered when review has issues."""
        task = Task(id="task-fix", title="Fix Test", description="Test with fixes")

        execution = await orchestrator_with_issues.execute_workflow(task)

        assert "fixes" in execution.artifacts
        assert execution.artifacts.get("needs_fixes") is True


class TestTaskTransitions:
    """Tests for task status transitions."""

    @pytest.fixture
    def task(self) -> Task:
        """Create test task."""
        return Task(id="trans-1", title="Transition Test", description="Test transitions")

    def test_transition_records_history(self, task: Task):
        """Test transitions are recorded in history."""
        task.transition(TaskStatus.ASSIGNED, "Assigned to coder")
        task.transition(TaskStatus.IN_PROGRESS, "Started work")

        assert len(task.history) == 2
        assert task.history[0]["to"] == TaskStatus.ASSIGNED.value
        assert task.history[1]["to"] == TaskStatus.IN_PROGRESS.value

    def test_transition_preserves_details(self, task: Task):
        """Test transition details are preserved."""
        task.transition(TaskStatus.FAILED, "Error in execution")

        assert task.history[0]["details"] == "Error in execution"


class TestAgentActions:
    """Tests for agent action tracking."""

    @pytest.fixture
    def coder(self) -> MockAgent:
        """Create coder agent."""
        agent = MockAgent(AgentType.CODER)
        agent.set_response("write_code", "def example(): pass")
        return agent

    @pytest.mark.asyncio
    async def test_action_recorded(self, coder: MockAgent):
        """Test action is recorded after execution."""
        await coder.execute("write_code", "Write example function")

        assert len(coder.actions_taken) == 1
        action = coder.actions_taken[0]
        assert action.agent_type == AgentType.CODER
        assert action.action == "write_code"

    @pytest.mark.asyncio
    async def test_multiple_actions_recorded(self, coder: MockAgent):
        """Test multiple actions are recorded."""
        await coder.execute("write_code", "First task")
        await coder.execute("write_code", "Second task")

        assert len(coder.actions_taken) == 2


class TestWorkflowArtifacts:
    """Tests for workflow artifact handling."""

    @pytest.fixture
    def orchestrator(self) -> MockAgentOrchestrator:
        """Create orchestrator with agents."""
        orch = MockAgentOrchestrator()

        for agent_type in AgentType:
            agent = MockAgent(agent_type)
            agent.set_response("create_plan", {"steps": ["s1"]})
            agent.set_response("write_code", "code")
            agent.set_response("review_code", {"ok": True})
            agent.set_response("apply_fixes", "fixed")
            agent.set_response("run_tests", {"passed": 1})
            orch.register_agent(agent)

        return orch

    @pytest.mark.asyncio
    async def test_artifacts_accumulate(self, orchestrator: MockAgentOrchestrator):
        """Test artifacts accumulate through phases."""
        task = Task(id="art-1", title="Artifact Test", description="Test artifacts")

        execution = await orchestrator.execute_workflow(task)

        assert len(execution.artifacts) > 0
        assert "final_status" in execution.artifacts


class TestWorkflowErrorHandling:
    """Tests for workflow error handling."""

    @pytest.fixture
    def failing_orchestrator(self) -> MockAgentOrchestrator:
        """Create orchestrator with failing agent."""
        orch = MockAgentOrchestrator()

        planner = MockAgent(AgentType.PLANNER)
        orch.register_agent(planner)

        # No coder registered - will cause issues

        return orch

    @pytest.mark.asyncio
    async def test_workflow_handles_missing_agent(
        self,
        failing_orchestrator: MockAgentOrchestrator
    ):
        """Test workflow handles missing agent gracefully."""
        task = Task(id="err-1", title="Error Test", description="Test error handling")

        # Should complete even without all agents
        execution = await failing_orchestrator.execute_workflow(task)
        assert execution is not None


class TestPhaseHooks:
    """Tests for workflow phase hooks."""

    @pytest.fixture
    def orchestrator(self) -> MockAgentOrchestrator:
        """Create orchestrator."""
        orch = MockAgentOrchestrator()
        for agent_type in AgentType:
            orch.register_agent(MockAgent(agent_type))
        return orch

    @pytest.mark.asyncio
    async def test_hooks_called(self, orchestrator: MockAgentOrchestrator):
        """Test phase hooks are called."""
        hook_calls = []

        async def planning_hook(execution):
            hook_calls.append("planning")

        orchestrator.on_phase(WorkflowPhase.PLANNING, planning_hook)

        task = Task(id="hook-1", title="Hook Test", description="Test hooks")
        await orchestrator.execute_workflow(task)

        assert "planning" in hook_calls
