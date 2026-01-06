"""Priority Type Definitions.

Defines task priority levels for agent operations.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.

Priority levels control:
- Task queue ordering
- Resource allocation
- Execution scheduling
"""

from enum import IntEnum
from typing import Final


class Priority(IntEnum):
    """Task priority levels for agent operations.

    Priority is implemented as IntEnum for natural ordering.
    Lower numeric value = higher priority.

    Usage:
        >>> task_priority = Priority.HIGH
        >>> task_priority < Priority.LOW  # True - HIGH comes before LOW
        True
        >>> sorted([Priority.LOW, Priority.CRITICAL, Priority.MEDIUM])
        [<Priority.CRITICAL: 0>, <Priority.MEDIUM: 2>, <Priority.LOW: 3>]
    """

    CRITICAL = 0  # Immediate execution - security issues, critical bugs
    HIGH = 1  # Next in queue - blocking issues, urgent features
    MEDIUM = 2  # Standard priority - normal development tasks
    LOW = 3  # Background tasks - refactoring, optimization

    @property
    def display_name(self) -> str:
        """Human-readable priority name."""
        return self.name.capitalize()

    @property
    def emoji(self) -> str:
        """Emoji representation for UI display."""
        return PRIORITY_EMOJI_MAP[self]

    def is_urgent(self) -> bool:
        """Check if this is an urgent priority (CRITICAL or HIGH)."""
        return self <= Priority.HIGH

    def is_background(self) -> bool:
        """Check if this is a background priority (LOW)."""
        return self == Priority.LOW

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Parse priority from string value.

        Args:
            value: Priority name (case-insensitive)

        Returns:
            Priority enum value

        Raises:
            ValueError: If value is not a valid priority name
        """
        try:
            return cls[value.upper()]
        except KeyError:
            valid = ", ".join(p.name for p in cls)
            raise ValueError(
                f"Invalid priority '{value}'. Valid values: {valid}"
            ) from None

    @classmethod
    def default(cls) -> "Priority":
        """Get the default priority for new tasks."""
        return cls.MEDIUM


# ═══════════════════════════════════════════════════════════════════════════
# PRIORITY METADATA
# ═══════════════════════════════════════════════════════════════════════════

PRIORITY_EMOJI_MAP: Final[dict[Priority, str]] = {
    Priority.CRITICAL: "🔴",
    Priority.HIGH: "🟠",
    Priority.MEDIUM: "🟡",
    Priority.LOW: "🟢",
}

PRIORITY_DESCRIPTIONS: Final[dict[Priority, str]] = {
    Priority.CRITICAL: "Immediate execution required. Security issues, critical bugs.",
    Priority.HIGH: "Next in queue. Blocking issues, urgent features.",
    Priority.MEDIUM: "Standard priority. Normal development tasks.",
    Priority.LOW: "Background tasks. Refactoring, optimization, tech debt.",
}


def get_priority_description(priority: Priority) -> str:
    """Get the description for a priority level."""
    return PRIORITY_DESCRIPTIONS[priority]
