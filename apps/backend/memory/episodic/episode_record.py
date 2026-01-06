"""Episode data model for episodic memory.

Part of Phase 2: Memory System Architecture
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


@dataclass
class EpisodeRecord:
    """A single episode representing an agent interaction.
    
    Episodes capture the complete context of an agent action including
    input, output, success status, tools used, and timing information.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    task_id: Optional[str] = None
    input_text: str = ""
    output_text: str = ""
    success: bool = True
    tools_used: List[str] = field(default_factory=list)
    duration_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "input_text": self.input_text,
            "output_text": self.output_text,
            "success": self.success,
            "tools_used": json.dumps(self.tools_used),
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat(),
            "metadata": json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EpisodeRecord":
        """Create from dictionary."""
        tools = data.get("tools_used", "[]")
        if isinstance(tools, str):
            tools = json.loads(tools)
        
        metadata = data.get("metadata", "{}")
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        created = data.get("created_at")
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        elif created is None:
            created = datetime.utcnow()
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            agent_id=data.get("agent_id", ""),
            task_id=data.get("task_id"),
            input_text=data.get("input_text", ""),
            output_text=data.get("output_text", ""),
            success=data.get("success", True),
            tools_used=tools,
            duration_ms=data.get("duration_ms", 0),
            created_at=created,
            metadata=metadata
        )
    
    @property
    def summary(self) -> str:
        """Get a short summary of the episode."""
        status = "✓" if self.success else "✗"
        tools = f" [{', '.join(self.tools_used)}]" if self.tools_used else ""
        return f"[{status}] {self.agent_id}: {self.input_text[:50]}...{tools}"
    
    def with_metadata(self, key: str, value: Any) -> "EpisodeRecord":
        """Return a copy with additional metadata."""
        new_metadata = self.metadata.copy()
        new_metadata[key] = value
        return EpisodeRecord(
            id=self.id,
            agent_id=self.agent_id,
            task_id=self.task_id,
            input_text=self.input_text,
            output_text=self.output_text,
            success=self.success,
            tools_used=self.tools_used.copy(),
            duration_ms=self.duration_ms,
            created_at=self.created_at,
            metadata=new_metadata
        )


@dataclass
class EpisodeSummary:
    """Lightweight summary of an episode for listing."""
    id: str
    agent_id: str
    success: bool
    created_at: datetime
    duration_ms: int
    
    @classmethod
    def from_record(cls, record: EpisodeRecord) -> "EpisodeSummary":
        return cls(
            id=record.id,
            agent_id=record.agent_id,
            success=record.success,
            created_at=record.created_at,
            duration_ms=record.duration_ms
        )
