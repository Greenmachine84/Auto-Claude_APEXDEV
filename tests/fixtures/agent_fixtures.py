"""
Agent test fixtures.

Provides reusable fixtures for testing agents, including
pre-configured agents, factories, and test contexts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from unittest.mock import AsyncMock, MagicMock
import pytest


class AgentRole(Enum):
    """Agent roles for testing."""
    CODER = "coder"
    REVIEWER = "reviewer"
    PLANNER = "planner"
    TESTER = "tester"
    FIXER = "fixer"


class AgentStatus(Enum):
    """Agent status states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    description: str
    enabled: bool = True
    parameters: dict = field(default_factory=dict)


@dataclass
class AgentTestConfig:
    """Configuration for test agents."""
    agent_id: str
    name: str
    role: AgentRole = AgentRole.CODER
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    capabilities: list[AgentCapability] = field(default_factory=list)
    system_prompt: str = "You are a helpful assistant."
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentTestContext:
    """Test context for agent operations."""
    agent: Any
    config: AgentTestConfig
    messages: list[dict] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)
    errors: list[Exception] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to context."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def add_tool_call(self, tool_name: str, args: dict, result: Any) -> None:
        """Record a tool call."""
        self.tool_calls.append({
            "tool": tool_name,
            "args": args,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })


class MockAgentBase:
    """Base mock agent for testing."""

    def __init__(self, config: AgentTestConfig):
        self.config = config
        self.id = config.agent_id
        self.name = config.name
        self.role = config.role
        self.status = AgentStatus.IDLE
        self._responses: dict[str, str] = {}
        self._message_history: list[dict] = []

    def set_response(self, trigger: str, response: str) -> None:
        """Set a canned response for a trigger."""
        self._responses[trigger] = response

    async def handle_message(self, message: str) -> str:
        """Handle an incoming message."""
        self._message_history.append({
            "role": "user",
            "content": message
        })

        # Check for canned response
        for trigger, response in self._responses.items():
            if trigger.lower() in message.lower():
                self._message_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response

        default_response = f"Response from {self.name}"
        self._message_history.append({
            "role": "assistant",
            "content": default_response
        })
        return default_response

    async def execute_task(self, task: dict) -> dict:
        """Execute a task."""
        self.status = AgentStatus.RUNNING
        try:
            result = {
                "status": "success",
                "agent_id": self.id,
                "task_id": task.get("id", "unknown"),
                "output": f"Completed by {self.name}"
            }
            self.status = AgentStatus.COMPLETED
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {"status": "error", "error": str(e)}


class MockCoderAgent(MockAgentBase):
    """Mock coder agent for testing."""

    def __init__(self, config: AgentTestConfig):
        config.role = AgentRole.CODER
        super().__init__(config)
        self._code_templates: dict[str, str] = {}

    def add_code_template(self, name: str, code: str) -> None:
        """Add a code template."""
        self._code_templates[name] = code

    async def write_code(self, specification: str) -> str:
        """Generate code from specification."""
        # Check templates
        for name, code in self._code_templates.items():
            if name.lower() in specification.lower():
                return code
        return f"# Generated code for: {specification}\ndef generated(): pass"


class MockReviewerAgent(MockAgentBase):
    """Mock reviewer agent for testing."""

    def __init__(self, config: AgentTestConfig):
        config.role = AgentRole.REVIEWER
        super().__init__(config)
        self._review_rules: list[dict] = []

    def add_review_rule(self, pattern: str, comment: str, severity: str = "info") -> None:
        """Add a review rule."""
        self._review_rules.append({
            "pattern": pattern,
            "comment": comment,
            "severity": severity
        })

    async def review_code(self, code: str) -> dict:
        """Review code and return findings."""
        findings = []
        for rule in self._review_rules:
            if rule["pattern"].lower() in code.lower():
                findings.append({
                    "comment": rule["comment"],
                    "severity": rule["severity"]
                })
        return {
            "approved": len(findings) == 0,
            "findings": findings
        }


class AgentFactory:
    """Factory for creating test agents."""

    _default_config = AgentTestConfig(
        agent_id="default-agent",
        name="Default Agent"
    )

    @classmethod
    def create(
        cls,
        role: AgentRole = AgentRole.CODER,
        **overrides
    ) -> MockAgentBase:
        """Create an agent with the specified role."""
        config = AgentTestConfig(
            agent_id=overrides.get("agent_id", f"{role.value}-001"),
            name=overrides.get("name", f"Test {role.value.title()} Agent"),
            role=role,
            **{k: v for k, v in overrides.items() if k not in ["agent_id", "name"]}
        )

        if role == AgentRole.CODER:
            return MockCoderAgent(config)
        elif role == AgentRole.REVIEWER:
            return MockReviewerAgent(config)
        else:
            return MockAgentBase(config)

    @classmethod
    def create_coder(cls, **overrides) -> MockCoderAgent:
        """Create a coder agent."""
        return cls.create(AgentRole.CODER, **overrides)

    @classmethod
    def create_reviewer(cls, **overrides) -> MockReviewerAgent:
        """Create a reviewer agent."""
        return cls.create(AgentRole.REVIEWER, **overrides)


def create_test_agent(
    role: AgentRole = AgentRole.CODER,
    **config_overrides
) -> MockAgentBase:
    """Create a test agent with the specified configuration."""
    return AgentFactory.create(role, **config_overrides)


def create_agent_config(
    agent_id: str = "test-agent",
    name: str = "Test Agent",
    role: AgentRole = AgentRole.CODER,
    **kwargs
) -> AgentTestConfig:
    """Create an agent configuration."""
    return AgentTestConfig(
        agent_id=agent_id,
        name=name,
        role=role,
        **kwargs
    )


# ============================================================================
# Pytest Fixtures
# ============================================================================

@pytest.fixture
def coder_agent() -> MockCoderAgent:
    """Provide a coder agent fixture."""
    agent = AgentFactory.create_coder(
        agent_id="coder-test-001",
        name="Test Coder"
    )
    agent.add_code_template("hello", "def hello(): return 'Hello, World!'")
    return agent


@pytest.fixture
def reviewer_agent() -> MockReviewerAgent:
    """Provide a reviewer agent fixture."""
    agent = AgentFactory.create_reviewer(
        agent_id="reviewer-test-001",
        name="Test Reviewer"
    )
    agent.add_review_rule("pass", "Empty function body", "warning")
    return agent


@pytest.fixture
def agent_context(coder_agent: MockCoderAgent) -> AgentTestContext:
    """Provide an agent test context."""
    config = create_agent_config(
        agent_id=coder_agent.id,
        name=coder_agent.name
    )
    return AgentTestContext(agent=coder_agent, config=config)


@pytest.fixture
def multi_agent_setup() -> dict[str, MockAgentBase]:
    """Provide multiple agents for coordination testing."""
    return {
        "coder": AgentFactory.create_coder(),
        "reviewer": AgentFactory.create_reviewer(),
        "planner": AgentFactory.create(AgentRole.PLANNER),
        "tester": AgentFactory.create(AgentRole.TESTER),
    }
