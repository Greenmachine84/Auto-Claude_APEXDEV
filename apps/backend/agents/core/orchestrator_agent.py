"""Orchestrator Agent.

Multi-agent coordination agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Responsibilities:
- Coordinate multiple agents
- Manage task distribution
- Handle agent communication
- Monitor execution progress
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar

from ..base import (
    AgentConfig,
    BaseAgent,
    ExecutionContext,
)
from ..base.agent_hooks import HookType
from ..registry import AgentFactory
from ..types import (
    AgentResult,
    AgentType,
    ErrorCode,
    ErrorResult,
    PartialResult,
    SuccessResult,
)

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of an orchestrated task."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class OrchestrationTask:
    """A task in the orchestration plan."""

    task_id: str
    agent_type: AgentType
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    result: AgentResult | None = None
    assigned_agent_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type.value,
            "description": self.description,
            "status": self.status.name,
            "dependencies": self.dependencies,
            "assigned_agent_id": self.assigned_agent_id,
        }


@dataclass
class OrchestrationPlan:
    """Plan for multi-agent orchestration."""

    plan_id: str
    tasks: list[OrchestrationTask] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_task(
        self,
        task_id: str,
        agent_type: AgentType,
        description: str,
        dependencies: list[str] | None = None,
    ) -> OrchestrationTask:
        """Add a task to the plan."""
        task = OrchestrationTask(
            task_id=task_id,
            agent_type=agent_type,
            description=description,
            dependencies=dependencies or [],
        )
        self.tasks.append(task)
        return task

    def get_ready_tasks(self) -> list[OrchestrationTask]:
        """Get tasks that are ready to execute."""
        completed_ids = {
            t.task_id for t in self.tasks if t.status == TaskStatus.COMPLETED
        }
        return [
            t
            for t in self.tasks
            if t.status == TaskStatus.PENDING
            and all(d in completed_ids for d in t.dependencies)
        ]

    def is_complete(self) -> bool:
        """Check if all tasks are complete."""
        return all(
            t.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.FAILED)
            for t in self.tasks
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "tasks": [t.to_dict() for t in self.tasks],
            "metadata": self.metadata,
            "is_complete": self.is_complete(),
        }


class OrchestratorAgent(BaseAgent):
    """Multi-agent coordination agent.

    The Orchestrator manages the execution of multiple agents to
    accomplish complex tasks. Implements MDA (Multi-Directed Agent)
    patterns from APEX Constitution.

    Capabilities:
    - Spawn and manage other agents
    - Distribute and coordinate tasks
    - Monitor execution progress
    - Handle failures and retries

    Usage:
        >>> orchestrator = OrchestratorAgent()
        >>> orchestrator.initialize()
        >>> result = orchestrator.run(context)
    """

    AGENT_TYPE: ClassVar[AgentType] = AgentType.ORCHESTRATOR

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent_id: str | None = None,
    ):
        """Initialize orchestrator agent.

        Args:
            config: Agent configuration
            agent_id: Optional agent identifier
        """
        if config is None:
            config = AgentConfig.for_orchestrator()
        super().__init__(config=config, agent_id=agent_id)

        self._factory = AgentFactory()
        self._active_agents: dict[str, BaseAgent] = {}
        self._plans: dict[str, OrchestrationPlan] = {}

    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Multi-agent coordination agent that manages the execution of "
            "multiple agents to accomplish complex tasks. Implements MDA "
            "patterns for distributed agent coordination."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        """Execute orchestration task.

        Args:
            context: Execution context with task details

        Returns:
            AgentResult with orchestration results
        """
        self._logger.info(f"Orchestrator executing task: {context.task}")

        try:
            self._hooks.execute(
                HookType.ON_TASK_START,
                metadata={"task_id": context.task.task_id if context.task else None},
            )

            # Create and execute plan
            plan = self._create_plan(context)
            results = self._execute_plan(plan, context)

            self._hooks.execute(
                HookType.ON_TASK_COMPLETE,
                result=results,
            )

            completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)

            if plan.is_complete() and all(
                t.status == TaskStatus.COMPLETED for t in plan.tasks
            ):
                return SuccessResult(
                    data={"plan": plan.to_dict(), "results": results},
                    message=f"Orchestration completed: {completed}/{len(plan.tasks)} tasks",
                )
            else:
                return PartialResult(
                    data={"plan": plan.to_dict(), "results": results},
                    message=f"Orchestration partially completed: {completed}/{len(plan.tasks)} tasks",
                    completed_percentage=completed / len(plan.tasks) * 100
                    if plan.tasks
                    else 0,
                )

        except Exception as e:
            self._logger.error(f"Orchestrator execution failed: {e}")
            return ErrorResult(
                message=str(e),
                code=ErrorCode.EXECUTION_ERROR,
                recoverable=True,
            )
        finally:
            self._cleanup_agents()

    def _create_plan(self, context: ExecutionContext) -> OrchestrationPlan:
        """Create orchestration plan.

        Args:
            context: Execution context

        Returns:
            OrchestrationPlan
        """
        # Placeholder - in production this uses LLM to create plan
        import uuid

        plan = OrchestrationPlan(plan_id=str(uuid.uuid4()))
        self._plans[plan.plan_id] = plan
        return plan

    def _execute_plan(
        self,
        plan: OrchestrationPlan,
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        """Execute an orchestration plan.

        Args:
            plan: Plan to execute
            context: Execution context

        Returns:
            List of task results
        """
        results = []

        while not plan.is_complete():
            ready_tasks = plan.get_ready_tasks()
            if not ready_tasks:
                break

            for task in ready_tasks:
                result = self._execute_task(task, context)
                results.append(
                    {
                        "task_id": task.task_id,
                        "status": task.status.name,
                    }
                )

        return results

    def _execute_task(
        self,
        task: OrchestrationTask,
        parent_context: ExecutionContext,
    ) -> AgentResult:
        """Execute a single orchestration task.

        Args:
            task: Task to execute
            parent_context: Parent execution context

        Returns:
            AgentResult from task execution
        """
        task.status = TaskStatus.RUNNING

        try:
            # Create agent for task
            agent = self._factory.create(task.agent_type)
            agent.initialize()
            self._active_agents[agent.id] = agent
            task.assigned_agent_id = agent.id

            # Create child context
            from ..base.agent_context import TaskReference

            child_context = parent_context.with_task(
                TaskReference.create(task.description)
            ).with_parent(self)

            # Execute
            self._hooks.execute(
                HookType.ON_SPAWN_AGENT,
                metadata={"spawned_agent_id": agent.id, "task_id": task.task_id},
            )

            result = agent.run(child_context)
            task.result = result
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED

            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            return ErrorResult(
                message=str(e),
                code=ErrorCode.EXECUTION_ERROR,
                recoverable=True,
            )

    def _cleanup_agents(self) -> None:
        """Cleanup spawned agents."""
        for agent in self._active_agents.values():
            try:
                agent.cleanup()
            except Exception as e:
                self._logger.warning(f"Failed to cleanup agent {agent.id}: {e}")
        self._active_agents.clear()

    def spawn_agent(
        self,
        agent_type: AgentType,
        context: ExecutionContext,
    ) -> BaseAgent:
        """Spawn a child agent.

        Args:
            agent_type: Type of agent to spawn
            context: Execution context

        Returns:
            Spawned agent
        """
        agent = self._factory.create(agent_type)
        agent.initialize()
        self._active_agents[agent.id] = agent

        self._hooks.execute(
            HookType.ON_SPAWN_AGENT,
            metadata={"spawned_agent_id": agent.id},
        )

        return agent

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self.to_dict(),
            "active_agents": len(self._active_agents),
            "plans_count": len(self._plans),
        }
