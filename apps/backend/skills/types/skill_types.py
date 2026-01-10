"""Skill type enumerations and definitions.

Defines:
- SkillCategory: Categories of skills
- SkillStatus: Execution status states
- SkillPriority: Execution priority levels
- SkillCapability: Capability flags
"""

from enum import Enum, Flag, auto


class SkillCategory(Enum):
    """Categories of skills.

    Skills are organized into categories based on their primary function.
    """

    CODING = "coding"
    TESTING = "testing"
    REVIEW = "review"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"

    @classmethod
    def list_all(cls) -> list[str]:
        """List all category values."""
        return [c.value for c in cls]

    @classmethod
    def from_string(cls, value: str) -> "SkillCategory":
        """Create from string value."""
        for cat in cls:
            if cat.value == value.lower():
                return cat
        return cls.CUSTOM


class SkillStatus(Enum):
    """Skill execution status.

    Represents the current state of a skill execution.
    """

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

    @property
    def is_terminal(self) -> bool:
        """Check if status is terminal (no further transitions)."""
        return self in (
            SkillStatus.COMPLETED,
            SkillStatus.FAILED,
            SkillStatus.CANCELLED,
            SkillStatus.TIMEOUT,
        )

    @property
    def is_active(self) -> bool:
        """Check if status represents active execution."""
        return self in (SkillStatus.RUNNING, SkillStatus.PAUSED)

    @property
    def is_success(self) -> bool:
        """Check if status represents successful completion."""
        return self == SkillStatus.COMPLETED


class SkillPriority(Enum):
    """Skill execution priority.

    Lower values = higher priority.
    """

    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4

    @classmethod
    def from_int(cls, value: int) -> "SkillPriority":
        """Create from integer value."""
        for priority in cls:
            if priority.value == value:
                return priority
        return cls.MEDIUM

    def __lt__(self, other: "SkillPriority") -> bool:
        return self.value < other.value

    def __le__(self, other: "SkillPriority") -> bool:
        return self.value <= other.value


class SkillCapability(Flag):
    """Capability flags for skills.

    Flags indicating what capabilities a skill has.
    """

    NONE = 0
    READ_FILES = auto()
    WRITE_FILES = auto()
    EXECUTE_CODE = auto()
    NETWORK_ACCESS = auto()
    GIT_OPERATIONS = auto()
    LLM_INFERENCE = auto()
    MEMORY_ACCESS = auto()
    TOOL_EXECUTION = auto()
    PARALLEL_EXECUTION = auto()
    STREAMING = auto()

    # Common combinations
    READ_ONLY = READ_FILES
    READ_WRITE = READ_FILES | WRITE_FILES
    FULL_ACCESS = READ_FILES | WRITE_FILES | EXECUTE_CODE | GIT_OPERATIONS

    @classmethod
    def from_list(cls, capabilities: list[str]) -> "SkillCapability":
        """Create from list of capability names."""
        result = cls.NONE
        for cap_name in capabilities:
            cap_name = cap_name.upper()
            if hasattr(cls, cap_name):
                result |= getattr(cls, cap_name)
        return result

    def to_list(self) -> list[str]:
        """Convert to list of capability names."""
        caps = []
        for cap in SkillCapability:
            if cap != SkillCapability.NONE and cap in self:
                caps.append(cap.name.lower())
        return caps


# Valid status transitions
VALID_TRANSITIONS: dict[SkillStatus, set[SkillStatus]] = {
    SkillStatus.PENDING: {
        SkillStatus.QUEUED,
        SkillStatus.RUNNING,
        SkillStatus.CANCELLED,
    },
    SkillStatus.QUEUED: {SkillStatus.RUNNING, SkillStatus.CANCELLED},
    SkillStatus.RUNNING: {
        SkillStatus.PAUSED,
        SkillStatus.COMPLETED,
        SkillStatus.FAILED,
        SkillStatus.CANCELLED,
        SkillStatus.TIMEOUT,
    },
    SkillStatus.PAUSED: {SkillStatus.RUNNING, SkillStatus.CANCELLED},
    SkillStatus.COMPLETED: set(),  # Terminal
    SkillStatus.FAILED: set(),  # Terminal
    SkillStatus.CANCELLED: set(),  # Terminal
    SkillStatus.TIMEOUT: set(),  # Terminal
}


def can_transition(from_status: SkillStatus, to_status: SkillStatus) -> bool:
    """Check if status transition is valid.

    Args:
        from_status: Current status
        to_status: Target status

    Returns:
        True if transition is valid
    """
    return to_status in VALID_TRANSITIONS.get(from_status, set())
