"""Agent Status Type Definitions.

Defines lifecycle states for agents in the system.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Status lifecycle:
    IDLE -> INITIALIZING -> RUNNING -> (PAUSED) -> TERMINATED
                              |                       ^
                              v                       |
                            ERROR ------------------->
"""

from enum import Enum
from typing import Final


class AgentStatus(Enum):
    """Agent lifecycle status enumeration.

    Defines the possible states an agent can be in during its lifecycle.
    State transitions are validated to prevent invalid state changes.

    Usage:
        >>> status = AgentStatus.IDLE
        >>> status.is_active()
        False
        >>> AgentStatus.RUNNING.can_transition_to(AgentStatus.PAUSED)
        True
    """

    IDLE = "idle"  # Agent created but not started
    INITIALIZING = "initializing"  # Agent is starting up
    RUNNING = "running"  # Agent is actively processing
    PAUSED = "paused"  # Agent temporarily suspended
    WAITING = "waiting"  # Agent waiting for external input/resource
    ERROR = "error"  # Agent encountered an error
    TERMINATED = "terminated"  # Agent has been stopped

    def is_active(self) -> bool:
        """Check if the agent is in an active state (can process tasks)."""
        return self in (AgentStatus.RUNNING, AgentStatus.WAITING)

    def is_final(self) -> bool:
        """Check if this is a terminal state."""
        return self in (AgentStatus.TERMINATED, AgentStatus.ERROR)

    def is_healthy(self) -> bool:
        """Check if the agent is in a healthy state."""
        return self not in (AgentStatus.ERROR, AgentStatus.TERMINATED)

    def can_transition_to(self, target: "AgentStatus") -> bool:
        """Check if transition to target status is valid.

        Args:
            target: The target status to transition to

        Returns:
            True if the transition is valid
        """
        return target in VALID_TRANSITIONS.get(self, set())

    @property
    def display_name(self) -> str:
        """Human-readable status name."""
        return self.value.replace("_", " ").title()

    @property
    def emoji(self) -> str:
        """Emoji representation for UI display."""
        return STATUS_EMOJI_MAP[self]

    @classmethod
    def from_string(cls, value: str) -> "AgentStatus":
        """Parse status from string value.

        Args:
            value: Status name (case-insensitive) or value

        Returns:
            AgentStatus enum value

        Raises:
            ValueError: If value is not a valid status
        """
        # Try by name first
        try:
            return cls[value.upper()]
        except KeyError:
            pass

        # Try by value
        value_lower = value.lower()
        for status in cls:
            if status.value == value_lower:
                return status

        valid = ", ".join(s.name for s in cls)
        raise ValueError(f"Invalid status '{value}'. Valid values: {valid}") from None


# ═══════════════════════════════════════════════════════════════════════════
# STATE TRANSITION RULES
# Defines valid state transitions per APEX governance
# ═══════════════════════════════════════════════════════════════════════════

VALID_TRANSITIONS: Final[dict[AgentStatus, set[AgentStatus]]] = {
    AgentStatus.IDLE: {
        AgentStatus.INITIALIZING,
        AgentStatus.TERMINATED,
    },
    AgentStatus.INITIALIZING: {
        AgentStatus.RUNNING,
        AgentStatus.ERROR,
        AgentStatus.TERMINATED,
    },
    AgentStatus.RUNNING: {
        AgentStatus.PAUSED,
        AgentStatus.WAITING,
        AgentStatus.ERROR,
        AgentStatus.TERMINATED,
    },
    AgentStatus.PAUSED: {
        AgentStatus.RUNNING,
        AgentStatus.ERROR,
        AgentStatus.TERMINATED,
    },
    AgentStatus.WAITING: {
        AgentStatus.RUNNING,
        AgentStatus.PAUSED,
        AgentStatus.ERROR,
        AgentStatus.TERMINATED,
    },
    AgentStatus.ERROR: {
        AgentStatus.INITIALIZING,  # Retry
        AgentStatus.TERMINATED,
    },
    AgentStatus.TERMINATED: set(),  # Terminal state - no transitions allowed
}


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, current: AgentStatus, target: AgentStatus):
        self.current = current
        self.target = target
        valid = VALID_TRANSITIONS.get(current, set())
        valid_str = ", ".join(s.name for s in valid) if valid else "none"
        super().__init__(
            f"Cannot transition from {current.name} to {target.name}. "
            f"Valid transitions: {valid_str}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# STATUS METADATA
# ═══════════════════════════════════════════════════════════════════════════

STATUS_EMOJI_MAP: Final[dict[AgentStatus, str]] = {
    AgentStatus.IDLE: "⚪",
    AgentStatus.INITIALIZING: "🔄",
    AgentStatus.RUNNING: "🟢",
    AgentStatus.PAUSED: "⏸️",
    AgentStatus.WAITING: "⏳",
    AgentStatus.ERROR: "🔴",
    AgentStatus.TERMINATED: "⏹️",
}

STATUS_DESCRIPTIONS: Final[dict[AgentStatus, str]] = {
    AgentStatus.IDLE: "Agent created but not yet started",
    AgentStatus.INITIALIZING: "Agent is starting up and loading resources",
    AgentStatus.RUNNING: "Agent is actively processing tasks",
    AgentStatus.PAUSED: "Agent is temporarily suspended",
    AgentStatus.WAITING: "Agent is waiting for external input or resources",
    AgentStatus.ERROR: "Agent encountered an error and stopped",
    AgentStatus.TERMINATED: "Agent has been stopped and cleaned up",
}


def get_status_description(status: AgentStatus) -> str:
    """Get the description for an agent status."""
    return STATUS_DESCRIPTIONS[status]
