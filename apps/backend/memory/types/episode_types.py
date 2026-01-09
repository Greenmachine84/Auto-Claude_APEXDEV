"""Episode type definitions for episodic memory.

Provides data models for storing and retrieving agent
execution episodes including task records, outcomes,
and metadata.

Part of Phase 2: Memory System Architecture
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EpisodeOutcome(Enum):
    """Outcome classification for episodes."""

    SUCCESS = "success"  # Task completed successfully
    PARTIAL_SUCCESS = "partial"  # Some objectives achieved
    FAILURE = "failure"  # Task failed
    ERROR = "error"  # Exception/error occurred
    CANCELLED = "cancelled"  # Task was cancelled
    TIMEOUT = "timeout"  # Task exceeded time limit

    @property
    def is_positive(self) -> bool:
        """Check if outcome is considered positive."""
        return self in (EpisodeOutcome.SUCCESS, EpisodeOutcome.PARTIAL_SUCCESS)


class EpisodeSeverity(Enum):
    """Severity level for episode categorization.

    Used for retention decisions and priority retrieval.
    """

    CRITICAL = 0  # Critical learnings, must retain
    HIGH = 1  # Important patterns
    MEDIUM = 2  # Standard episodes
    LOW = 3  # Routine, can be summarized
    DEBUG = 4  # Verbose, short retention


@dataclass
class ToolInvocation:
    """Record of a tool invocation within an episode."""

    tool_name: str
    tool_input: dict[str, Any]
    tool_output: Any
    duration_ms: int
    success: bool
    error_message: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolInvocation":
        """Create from dictionary."""
        return cls(
            tool_name=data["tool_name"],
            tool_input=data["tool_input"],
            tool_output=data["tool_output"],
            duration_ms=data["duration_ms"],
            success=data["success"],
            error_message=data.get("error_message"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class EpisodeMetadata:
    """Metadata associated with an episode."""

    # Context information
    project_path: str | None = None
    file_paths: list[str] = field(default_factory=list)
    git_branch: str | None = None
    git_commit: str | None = None

    # Agent context
    parent_task_id: str | None = None
    child_task_ids: list[str] = field(default_factory=list)

    # Quality metrics
    confidence_score: float | None = None
    quality_score: float | None = None
    user_feedback: str | None = None

    # LLM details
    llm_provider: str | None = None
    llm_model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    # Tags and labels
    tags: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "project_path": self.project_path,
            "file_paths": self.file_paths,
            "git_branch": self.git_branch,
            "git_commit": self.git_commit,
            "parent_task_id": self.parent_task_id,
            "child_task_ids": self.child_task_ids,
            "confidence_score": self.confidence_score,
            "quality_score": self.quality_score,
            "user_feedback": self.user_feedback,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "tags": self.tags,
            "labels": self.labels,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpisodeMetadata":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class EpisodeRecord:
    """Complete record of an agent execution episode.

    Episodes capture the full context of task execution
    for learning and retrieval. Core data structure for
    episodic memory.

    Attributes:
        id: Unique episode identifier
        agent_id: ID of the executing agent
        agent_type: Type of agent (coder, reviewer, etc.)
        task_id: Associated task identifier
        input_text: Input prompt/instruction
        output_text: Generated output/response
        outcome: Success/failure classification
        severity: Importance level
        tools_used: List of tools invoked
        tool_invocations: Detailed tool call records
        duration_ms: Total execution time
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        metadata: Additional context
    """

    # Identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    agent_type: str = ""
    task_id: str | None = None

    # Content
    input_text: str = ""
    output_text: str = ""
    reasoning: str | None = None  # Chain of thought

    # Classification
    outcome: EpisodeOutcome = EpisodeOutcome.SUCCESS
    severity: EpisodeSeverity = EpisodeSeverity.MEDIUM

    # Tool usage
    tools_used: list[str] = field(default_factory=list)
    tool_invocations: list[ToolInvocation] = field(default_factory=list)

    # Timing
    duration_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Extended metadata
    metadata: EpisodeMetadata = field(default_factory=EpisodeMetadata)

    # Embedding for semantic search
    embedding: list[float] | None = None

    @property
    def success(self) -> bool:
        """Check if episode was successful."""
        return self.outcome.is_positive

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        return self.metadata.input_tokens + self.metadata.output_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "task_id": self.task_id,
            "input_text": self.input_text,
            "output_text": self.output_text,
            "reasoning": self.reasoning,
            "outcome": self.outcome.value,
            "severity": self.severity.value,
            "tools_used": self.tools_used,
            "tool_invocations": [t.to_dict() for t in self.tool_invocations],
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata.to_dict(),
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpisodeRecord":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            agent_id=data["agent_id"],
            agent_type=data.get("agent_type", ""),
            task_id=data.get("task_id"),
            input_text=data["input_text"],
            output_text=data["output_text"],
            reasoning=data.get("reasoning"),
            outcome=EpisodeOutcome(data["outcome"]),
            severity=EpisodeSeverity(data.get("severity", 2)),
            tools_used=data.get("tools_used", []),
            tool_invocations=[
                ToolInvocation.from_dict(t) for t in data.get("tool_invocations", [])
            ],
            duration_ms=data.get("duration_ms", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(
                data.get("updated_at", data["created_at"])
            ),
            metadata=EpisodeMetadata.from_dict(data.get("metadata", {})),
            embedding=data.get("embedding"),
        )

    def get_searchable_text(self) -> str:
        """Get combined text for full-text search indexing."""
        parts = [
            self.input_text,
            self.output_text,
            self.reasoning or "",
            " ".join(self.tools_used),
            " ".join(self.metadata.tags),
        ]
        return " ".join(filter(None, parts))
