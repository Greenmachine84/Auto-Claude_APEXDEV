"""Task model.

Defines task data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, Enum
from typing import Any, Dict, List, Optional
import uuid


class TaskPriority(IntEnum):
    """Task priority levels."""
    
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(str, Enum):
    """Task status values."""
    
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


@dataclass
class Task:
    """Task model.
    
    Represents a unit of work to be executed.
    
    Attributes:
        id: Unique task identifier
        type: Task type for routing
        data: Task payload
        priority: Execution priority
        status: Current status
    """
    
    type: str
    data: Dict[str, Any]
    
    # Identification
    id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    name: Optional[str] = None
    
    # Priority and status
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution
    result: Any = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    
    # Relationships
    parent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __lt__(self, other: "Task") -> bool:
        """Compare tasks by priority."""
        return self.priority < other.priority
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
    
    @property
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retries < self.max_retries
    
    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def mark_started(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Any = None) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def mark_retry(self) -> None:
        """Mark task for retry."""
        self.status = TaskStatus.RETRYING
        self.retries += 1
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "data": self.data,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "retries": self.retries,
            "parent_id": self.parent_id,
            "workflow_id": self.workflow_id,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data.get("id", f"task_{uuid.uuid4().hex[:12]}"),
            type=data["type"],
            name=data.get("name"),
            data=data.get("data", {}),
            priority=TaskPriority(data.get("priority", TaskPriority.NORMAL)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING)),
            parent_id=data.get("parent_id"),
            workflow_id=data.get("workflow_id"),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
        )
