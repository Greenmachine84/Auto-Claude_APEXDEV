"""
Mock agents for testing.

Provides mock implementations of various agent types with
configurable behavior for testing agent workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import asyncio


class AgentRole(Enum):
    """Agent roles."""
    CODER = "coder"
    REVIEWER = "reviewer"
    PLANNER = "planner"
    TESTER = "tester"
    FIXER = "fixer"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(Enum):
    """Agent status states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Agent configuration."""
    agent_id: str
    name: str
    role: AgentRole
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)


@dataclass
class AgentMessage:
    """Message for agent communication."""
    sender: str
    recipient: str
    content: Any
    message_type: str = "text"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentAction:
    """An action taken by an agent."""
    action_type: str
    input_data: Any
    output_data: Any = None
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class MockAgent:
    """Base mock agent implementation."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = config.agent_id
        self.name = config.name
        self.role = config.role
        self.status = AgentStatus.IDLE
        self._responses: dict[str, Any] = {}
        self._actions: list[AgentAction] = []
        self._messages: list[AgentMessage] = []
        self._error_mode = False
        self._error: Optional[Exception] = None

    def set_response(self, trigger: str, response: Any) -> None:
        """Set canned response for trigger."""
        self._responses[trigger] = response

    def set_error(self, error: Exception) -> None:
        """Set error mode."""
        self._error_mode = True
        self._error = error

    def clear_error(self) -> None:
        """Clear error mode."""
        self._error_mode = False
        self._error = None

    async def handle_message(self, message: str) -> str:
        """Handle an incoming message."""
        self._messages.append(AgentMessage(
            sender="user",
            recipient=self.id,
            content=message
        ))

        if self._error_mode and self._error:
            raise self._error

        # Check for canned response
        for trigger, response in self._responses.items():
            if trigger.lower() in message.lower():
                return str(response)

        return f"Response from {self.name}: Acknowledged"

    async def execute_task(self, task: dict) -> dict:
        """Execute a task."""
        import time
        start = time.time()
        self.status = AgentStatus.RUNNING

        try:
            if self._error_mode and self._error:
                raise self._error

            result = await self._process_task(task)
            action = AgentAction(
                action_type="execute_task",
                input_data=task,
                output_data=result,
                duration_ms=(time.time() - start) * 1000
            )
            self._actions.append(action)
            self.status = AgentStatus.COMPLETED
            return result

        except Exception as e:
            self.status = AgentStatus.ERROR
            action = AgentAction(
                action_type="execute_task",
                input_data=task,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
            self._actions.append(action)
            raise

    async def _process_task(self, task: dict) -> dict:
        """Process task - override in subclasses."""
        return {
            "status": "success",
            "agent_id": self.id,
            "task_id": task.get("id", "unknown")
        }

    def get_action_history(self) -> list[AgentAction]:
        """Get action history."""
        return self._actions.copy()


class MockCoderAgent(MockAgent):
    """Mock coder agent."""

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.CODER
        super().__init__(config)
        self._code_templates: dict[str, str] = {}

    def add_code_template(self, name: str, code: str) -> None:
        """Add a code template."""
        self._code_templates[name] = code

    async def write_code(self, specification: str) -> str:
        """Generate code from specification."""
        if self._error_mode and self._error:
            raise self._error

        for name, code in self._code_templates.items():
            if name.lower() in specification.lower():
                return code

        return f"# Generated for: {specification}\ndef generated(): pass"

    async def _process_task(self, task: dict) -> dict:
        """Process coding task."""
        spec = task.get("specification", task.get("description", ""))
        code = await self.write_code(spec)
        return {
            "status": "success",
            "agent_id": self.id,
            "task_id": task.get("id"),
            "code": code
        }


class MockReviewerAgent(MockAgent):
    """Mock reviewer agent."""

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.REVIEWER
        super().__init__(config)
        self._review_rules: list[dict] = []

    def add_review_rule(
        self,
        pattern: str,
        comment: str,
        severity: str = "info"
    ) -> None:
        """Add a review rule."""
        self._review_rules.append({
            "pattern": pattern,
            "comment": comment,
            "severity": severity
        })

    async def review_code(self, code: str) -> dict:
        """Review code."""
        if self._error_mode and self._error:
            raise self._error

        findings = []
        for rule in self._review_rules:
            if rule["pattern"].lower() in code.lower():
                findings.append({
                    "comment": rule["comment"],
                    "severity": rule["severity"]
                })

        return {
            "approved": len(findings) == 0,
            "findings": findings,
            "reviewer": self.id
        }

    async def _process_task(self, task: dict) -> dict:
        """Process review task."""
        code = task.get("code", "")
        review = await self.review_code(code)
        return {
            "status": "success",
            "agent_id": self.id,
            "task_id": task.get("id"),
            "review": review
        }


class MockAgentFactory:
    """Factory for creating mock agents."""

    @classmethod
    def create(
        cls,
        role: AgentRole,
        agent_id: str = None,
        name: str = None,
        **config_kwargs
    ) -> MockAgent:
        """Create a mock agent."""
        if agent_id is None:
            agent_id = f"{role.value}-{id(cls) % 1000}"
        if name is None:
            name = f"Mock {role.value.title()} Agent"

        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            role=role,
            **config_kwargs
        )

        if role == AgentRole.CODER:
            return MockCoderAgent(config)
        elif role == AgentRole.REVIEWER:
            return MockReviewerAgent(config)
        else:
            return MockAgent(config)

    @classmethod
    def create_team(cls) -> dict[AgentRole, MockAgent]:
        """Create a full agent team."""
        return {role: cls.create(role) for role in AgentRole}


class MockAgentOrchestrator:
    """Orchestrator for coordinating multiple agents."""

    def __init__(self):
        self.agents: dict[str, MockAgent] = {}
        self._workflows: dict[str, list[tuple[str, str]]] = {}
        self._execution_log: list[dict] = []

    def register_agent(self, agent: MockAgent) -> None:
        """Register an agent."""
        self.agents[agent.id] = agent

    def define_workflow(
        self,
        workflow_id: str,
        steps: list[tuple[str, str]]
    ) -> None:
        """Define a workflow as sequence of (agent_id, action)."""
        self._workflows[workflow_id] = steps

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_input: dict
    ) -> dict:
        """Execute a workflow."""
        steps = self._workflows.get(workflow_id, [])
        if not steps:
            return {"status": "error", "error": "Workflow not found"}

        context = dict(initial_input)
        results = []

        for agent_id, action in steps:
            agent = self.agents.get(agent_id)
            if not agent:
                continue

            try:
                task = {"action": action, **context}
                result = await agent.execute_task(task)
                results.append(result)
                context.update(result)

                self._execution_log.append({
                    "workflow_id": workflow_id,
                    "agent_id": agent_id,
                    "action": action,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                self._execution_log.append({
                    "workflow_id": workflow_id,
                    "agent_id": agent_id,
                    "action": action,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                return {"status": "error", "error": str(e), "results": results}

        return {"status": "success", "results": results}

    def get_execution_log(self) -> list[dict]:
        """Get execution log."""
        return self._execution_log.copy()
