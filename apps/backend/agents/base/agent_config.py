"""Agent Configuration Dataclasses.

Defines configuration structures for agent initialization.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Configurations are immutable after creation for APEX compliance.
"""

from dataclasses import dataclass, field
from typing import Any, Final
from enum import Flag, auto

from ..types import AgentType, Priority


class Capability(Flag):
    """Agent capability flags.

    Capabilities define what operations an agent is permitted to perform.
    Follows principle of least privilege - agents only get required capabilities.
    """

    NONE = 0

    # File Operations
    CAN_READ_FILES = auto()
    CAN_WRITE_FILES = auto()
    CAN_DELETE_FILES = auto()

    # Code Operations
    CAN_ANALYZE_CODE = auto()
    CAN_GENERATE_CODE = auto()
    CAN_REFACTOR_CODE = auto()

    # Execution
    CAN_EXECUTE_COMMANDS = auto()
    CAN_EXECUTE_TESTS = auto()

    # Git Operations
    CAN_USE_GIT = auto()
    CAN_CREATE_BRANCHES = auto()
    CAN_COMMIT = auto()
    CAN_PUSH = auto()

    # LLM Operations
    CAN_CALL_LLM = auto()
    CAN_USE_TOOLS = auto()

    # Agent Operations
    CAN_SPAWN_AGENTS = auto()
    CAN_MANAGE_TASKS = auto()
    CAN_COORDINATE_AGENTS = auto()

    # Memory Operations
    CAN_READ_MEMORY = auto()
    CAN_WRITE_MEMORY = auto()

    # Network Operations
    CAN_FETCH_WEB = auto()
    CAN_CALL_APIS = auto()


# Predefined capability sets for common agent roles
READ_ONLY_CAPABILITIES: Final[Capability] = (
    Capability.CAN_READ_FILES
    | Capability.CAN_ANALYZE_CODE
    | Capability.CAN_READ_MEMORY
)

CODER_CAPABILITIES: Final[Capability] = (
    Capability.CAN_READ_FILES
    | Capability.CAN_WRITE_FILES
    | Capability.CAN_ANALYZE_CODE
    | Capability.CAN_GENERATE_CODE
    | Capability.CAN_EXECUTE_COMMANDS
    | Capability.CAN_USE_GIT
    | Capability.CAN_COMMIT
    | Capability.CAN_CALL_LLM
    | Capability.CAN_USE_TOOLS
    | Capability.CAN_READ_MEMORY
    | Capability.CAN_WRITE_MEMORY
    | Capability.CAN_FETCH_WEB
)

REVIEWER_CAPABILITIES: Final[Capability] = (
    Capability.CAN_READ_FILES
    | Capability.CAN_ANALYZE_CODE
    | Capability.CAN_CALL_LLM
    | Capability.CAN_READ_MEMORY
)

ORCHESTRATOR_CAPABILITIES: Final[Capability] = (
    Capability.CAN_SPAWN_AGENTS
    | Capability.CAN_MANAGE_TASKS
    | Capability.CAN_COORDINATE_AGENTS
    | Capability.CAN_READ_MEMORY
    | Capability.CAN_WRITE_MEMORY
)


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    """Resource limits for agent execution.

    Defines constraints on agent resource usage for cost control
    and system stability.
    """

    max_tokens_per_request: int = 100_000
    max_tokens_per_session: int = 1_000_000
    max_execution_time_seconds: int = 3600  # 1 hour
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    max_files_per_operation: int = 100
    max_concurrent_tools: int = 5
    max_memory_mb: int = 512
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Validate resource limits."""
        if self.max_tokens_per_request <= 0:
            raise ValueError("max_tokens_per_request must be positive")
        if self.max_execution_time_seconds <= 0:
            raise ValueError("max_execution_time_seconds must be positive")


@dataclass(frozen=True, slots=True)
class AgentCapabilities:
    """Capability declaration for an agent.

    Declares what capabilities an agent requires and optionally requests.
    Required capabilities must be granted; optional capabilities are nice-to-have.
    """

    required: Capability = Capability.NONE
    optional: Capability = Capability.NONE

    def has_capability(self, capability: Capability) -> bool:
        """Check if this agent has a specific capability."""
        return bool(self.required & capability) or bool(self.optional & capability)

    def get_all_capabilities(self) -> Capability:
        """Get all capabilities (required + optional)."""
        return self.required | self.optional

    def validate_required(self, granted: Capability) -> bool:
        """Check if all required capabilities are granted."""
        return (self.required & granted) == self.required


@dataclass(frozen=True, slots=True)
class AgentConfig:
    """Configuration for agent initialization.

    Immutable configuration that defines agent behavior and constraints.
    Validated at creation time to ensure APEX compliance.

    Attributes:
        agent_type: The type of agent
        name: Human-readable agent name
        capabilities: Capability declarations
        resource_limits: Resource constraints
        priority: Default task priority
        model: LLM model to use (optional, uses system default)
        thinking_budget: Extended thinking token budget
        metadata: Additional agent-specific configuration
    """

    agent_type: AgentType
    name: str = ""
    description: str = ""
    capabilities: AgentCapabilities = field(default_factory=AgentCapabilities)
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    priority: Priority = Priority.MEDIUM
    model: str | None = None
    thinking_budget: int | None = None
    enable_memory: bool = True
    enable_tools: bool = True
    enable_hooks: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Set default name from agent type if not provided
        if not self.name:
            object.__setattr__(self, "name", self.agent_type.value.replace("_", " ").title())

    @classmethod
    def for_coder(cls, **kwargs: Any) -> "AgentConfig":
        """Create configuration for a coder agent."""
        return cls(
            agent_type=AgentType.CODER,
            capabilities=AgentCapabilities(required=CODER_CAPABILITIES),
            **kwargs,
        )

    @classmethod
    def for_reviewer(cls, **kwargs: Any) -> "AgentConfig":
        """Create configuration for a reviewer agent."""
        return cls(
            agent_type=AgentType.REVIEWER,
            capabilities=AgentCapabilities(required=REVIEWER_CAPABILITIES),
            **kwargs,
        )

    @classmethod
    def for_orchestrator(cls, **kwargs: Any) -> "AgentConfig":
        """Create configuration for an orchestrator agent."""
        return cls(
            agent_type=AgentType.ORCHESTRATOR,
            capabilities=AgentCapabilities(required=ORCHESTRATOR_CAPABILITIES),
            **kwargs,
        )
