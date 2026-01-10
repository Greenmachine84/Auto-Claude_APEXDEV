"""Agent Execution Context.

Defines the execution context passed to agent operations.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Context provides access to:
- Task information
- Memory system
- Tool permissions
- Parent agent (for MDA)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..types import AgentType, Priority

if TYPE_CHECKING:
    from .base_agent import BaseAgent


@dataclass
class TaskReference:
    """Reference to the current task being executed."""

    task_id: str
    subtask_id: str | None = None
    description: str = ""
    priority: Priority = Priority.MEDIUM
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, description: str, **kwargs: Any) -> "TaskReference":
        """Create a new task reference with generated ID."""
        return cls(
            task_id=str(uuid.uuid4()),
            description=description,
            **kwargs,
        )


@dataclass
class MemoryAccess:
    """Memory system access configuration."""

    enabled: bool = True
    read_allowed: bool = True
    write_allowed: bool = True
    graphiti_enabled: bool = False
    namespace: str = "default"


@dataclass
class ToolPermissions:
    """Tool access permissions for the context."""

    allowed_tools: set[str] = field(default_factory=set)
    denied_tools: set[str] = field(default_factory=set)
    sandboxed: bool = True

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed in this context."""
        if tool_name in self.denied_tools:
            return False
        if self.allowed_tools:
            return tool_name in self.allowed_tools
        return True


@dataclass
class ExecutionContext:
    """Execution context for agent operations.

    Provides all necessary context for an agent to execute a task.
    Immutable after creation to ensure consistent execution.

    Attributes:
        context_id: Unique context identifier
        session_id: Session this context belongs to
        agent_type: Type of agent this context is for
        task: Current task reference
        project_dir: Project root directory
        spec_dir: Specification directory
        memory: Memory access configuration
        tools: Tool permissions
        parent_agent: Parent agent for MDA scenarios
        created_at: Context creation timestamp
        metadata: Additional context data
    """

    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType = AgentType.CODER
    task: TaskReference | None = None
    project_dir: Path | None = None
    spec_dir: Path | None = None
    memory: MemoryAccess = field(default_factory=MemoryAccess)
    tools: ToolPermissions = field(default_factory=ToolPermissions)
    parent_agent: "BaseAgent | None" = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: int = 3600
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate context after initialization."""
        if self.project_dir and not isinstance(self.project_dir, Path):
            object.__setattr__(self, "project_dir", Path(self.project_dir))
        if self.spec_dir and not isinstance(self.spec_dir, Path):
            object.__setattr__(self, "spec_dir", Path(self.spec_dir))

    @property
    def has_parent(self) -> bool:
        """Check if this context has a parent agent (MDA scenario)."""
        return self.parent_agent is not None

    @property
    def is_root_context(self) -> bool:
        """Check if this is a root context (no parent)."""
        return not self.has_parent

    def with_task(self, task: TaskReference) -> "ExecutionContext":
        """Create a new context with a different task."""
        return ExecutionContext(
            context_id=str(uuid.uuid4()),
            session_id=self.session_id,
            agent_type=self.agent_type,
            task=task,
            project_dir=self.project_dir,
            spec_dir=self.spec_dir,
            memory=self.memory,
            tools=self.tools,
            parent_agent=self.parent_agent,
            timeout_seconds=self.timeout_seconds,
            metadata=dict(self.metadata),
        )

    def with_parent(self, parent: "BaseAgent") -> "ExecutionContext":
        """Create a child context with parent agent."""
        return ExecutionContext(
            context_id=str(uuid.uuid4()),
            session_id=self.session_id,
            agent_type=self.agent_type,
            task=self.task,
            project_dir=self.project_dir,
            spec_dir=self.spec_dir,
            memory=self.memory,
            tools=self.tools,
            parent_agent=parent,
            timeout_seconds=self.timeout_seconds,
            metadata={**self.metadata, "parent_context_id": self.context_id},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "context_id": self.context_id,
            "session_id": self.session_id,
            "agent_type": self.agent_type.value,
            "task": {
                "task_id": self.task.task_id,
                "subtask_id": self.task.subtask_id,
                "description": self.task.description,
            }
            if self.task
            else None,
            "project_dir": str(self.project_dir) if self.project_dir else None,
            "spec_dir": str(self.spec_dir) if self.spec_dir else None,
            "has_parent": self.has_parent,
            "created_at": self.created_at.isoformat(),
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
        }


class ContextBuilder:
    """Builder pattern for creating execution contexts.

    Usage:
        >>> context = (
        ...     ContextBuilder()
        ...     .with_agent_type(AgentType.CODER)
        ...     .with_project_dir(Path("/project"))
        ...     .with_task(TaskReference.create("Implement feature"))
        ...     .with_memory(enabled=True, graphiti_enabled=True)
        ...     .build()
        ... )
    """

    def __init__(self) -> None:
        self._context_id = str(uuid.uuid4())
        self._session_id = str(uuid.uuid4())
        self._agent_type = AgentType.CODER
        self._task: TaskReference | None = None
        self._project_dir: Path | None = None
        self._spec_dir: Path | None = None
        self._memory = MemoryAccess()
        self._tools = ToolPermissions()
        self._parent_agent: BaseAgent | None = None
        self._timeout_seconds = 3600
        self._metadata: dict[str, Any] = {}

    def with_session_id(self, session_id: str) -> "ContextBuilder":
        """Set session ID."""
        self._session_id = session_id
        return self

    def with_agent_type(self, agent_type: AgentType) -> "ContextBuilder":
        """Set agent type."""
        self._agent_type = agent_type
        return self

    def with_task(self, task: TaskReference) -> "ContextBuilder":
        """Set task reference."""
        self._task = task
        return self

    def with_project_dir(self, path: Path | str) -> "ContextBuilder":
        """Set project directory."""
        self._project_dir = Path(path) if isinstance(path, str) else path
        return self

    def with_spec_dir(self, path: Path | str) -> "ContextBuilder":
        """Set specification directory."""
        self._spec_dir = Path(path) if isinstance(path, str) else path
        return self

    def with_memory(
        self,
        enabled: bool = True,
        read_allowed: bool = True,
        write_allowed: bool = True,
        graphiti_enabled: bool = False,
        namespace: str = "default",
    ) -> "ContextBuilder":
        """Configure memory access."""
        self._memory = MemoryAccess(
            enabled=enabled,
            read_allowed=read_allowed,
            write_allowed=write_allowed,
            graphiti_enabled=graphiti_enabled,
            namespace=namespace,
        )
        return self

    def with_tools(
        self,
        allowed: set[str] | None = None,
        denied: set[str] | None = None,
        sandboxed: bool = True,
    ) -> "ContextBuilder":
        """Configure tool permissions."""
        self._tools = ToolPermissions(
            allowed_tools=allowed or set(),
            denied_tools=denied or set(),
            sandboxed=sandboxed,
        )
        return self

    def with_parent(self, parent: "BaseAgent") -> "ContextBuilder":
        """Set parent agent."""
        self._parent_agent = parent
        return self

    def with_timeout(self, seconds: int) -> "ContextBuilder":
        """Set timeout."""
        self._timeout_seconds = seconds
        return self

    def with_metadata(self, **kwargs: Any) -> "ContextBuilder":
        """Add metadata."""
        self._metadata.update(kwargs)
        return self

    def build(self) -> ExecutionContext:
        """Build the execution context."""
        return ExecutionContext(
            context_id=self._context_id,
            session_id=self._session_id,
            agent_type=self._agent_type,
            task=self._task,
            project_dir=self._project_dir,
            spec_dir=self._spec_dir,
            memory=self._memory,
            tools=self._tools,
            parent_agent=self._parent_agent,
            timeout_seconds=self._timeout_seconds,
            metadata=self._metadata,
        )
