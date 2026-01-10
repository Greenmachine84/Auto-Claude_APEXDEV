"""Memory type definitions for the memory subsystem.

Provides core enums and types for memory classification, tiering,
and operations across the H-MEM architecture.

Part of Phase 2: Memory System Architecture
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class MemoryType(Enum):
    """Classification of memory by content type.

    Memory types determine how content is stored, indexed,
    and retrieved across the memory subsystem.
    """

    EPISODIC = "episodic"  # Task execution records
    SEMANTIC = "semantic"  # Knowledge and concepts
    PROCEDURAL = "procedural"  # How-to knowledge, skills
    WORKING = "working"  # Temporary task context
    DECLARATIVE = "declarative"  # Facts and data

    def __str__(self) -> str:
        return self.value


class MemoryTier(Enum):
    """H-MEM memory tier classification.

    Implements tiered memory architecture:
    - L1: Hot cache (fastest, smallest)
    - L2: Session memory (medium speed/size)
    - L3: Persistent storage (slowest, largest)
    """

    L1_CACHE = "l1_cache"  # In-memory hot cache
    L2_SESSION = "l2_session"  # Session-scoped memory
    L3_PERSISTENT = "l3_persistent"  # Long-term storage

    @property
    def access_speed(self) -> str:
        """Get relative access speed description."""
        speeds = {
            MemoryTier.L1_CACHE: "sub-millisecond",
            MemoryTier.L2_SESSION: "milliseconds",
            MemoryTier.L3_PERSISTENT: "tens of milliseconds",
        }
        return speeds.get(self, "unknown")

    @property
    def capacity(self) -> str:
        """Get relative capacity description."""
        capacities = {
            MemoryTier.L1_CACHE: "limited (MB)",
            MemoryTier.L2_SESSION: "moderate (GB)",
            MemoryTier.L3_PERSISTENT: "unlimited",
        }
        return capacities.get(self, "unknown")

    def __lt__(self, other: "MemoryTier") -> bool:
        """Enable tier comparison (L1 < L2 < L3)."""
        order = [MemoryTier.L1_CACHE, MemoryTier.L2_SESSION, MemoryTier.L3_PERSISTENT]
        return order.index(self) < order.index(other)


class MemoryPriority(Enum):
    """Priority level for memory operations.

    Higher priority items are retained longer and
    retrieved preferentially during context building.
    """

    CRITICAL = 0  # Must retain (errors, critical learnings)
    HIGH = 1  # Important (successful patterns)
    MEDIUM = 2  # Standard (normal episodes)
    LOW = 3  # Background (verbose logs)
    EPHEMERAL = 4  # Temporary (can be discarded)

    def __lt__(self, other: "MemoryPriority") -> bool:
        return self.value < other.value

    @classmethod
    def from_importance_score(cls, score: float) -> "MemoryPriority":
        """Map importance score [0,1] to priority."""
        if score >= 0.9:
            return cls.CRITICAL
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.4:
            return cls.MEDIUM
        elif score >= 0.2:
            return cls.LOW
        return cls.EPHEMERAL


class MemoryStatus(Enum):
    """Status of a memory record."""

    ACTIVE = "active"  # Available for retrieval
    ARCHIVED = "archived"  # Compressed, slower access
    PENDING_DELETION = "pending_deletion"  # Marked for cleanup
    DELETED = "deleted"  # Soft-deleted
    CORRUPTED = "corrupted"  # Data integrity issue


class MemoryOperation(Enum):
    """Types of memory operations for audit logging."""

    STORE = auto()  # New memory stored
    RETRIEVE = auto()  # Memory accessed
    UPDATE = auto()  # Memory modified
    DELETE = auto()  # Memory removed
    PROMOTE = auto()  # Moved to higher tier
    DEMOTE = auto()  # Moved to lower tier
    ARCHIVE = auto()  # Compressed for storage
    RESTORE = auto()  # Restored from archive
    SEARCH = auto()  # Semantic search performed
    INDEX = auto()  # Added to search index


@dataclass
class MemoryStats:
    """Statistics for memory subsystem monitoring."""

    total_records: int = 0
    records_by_tier: dict[MemoryTier, int] = field(default_factory=dict)
    records_by_type: dict[MemoryType, int] = field(default_factory=dict)
    total_size_bytes: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    avg_retrieval_ms: float = 0.0
    last_compaction: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_records": self.total_records,
            "records_by_tier": {t.value: c for t, c in self.records_by_tier.items()},
            "records_by_type": {t.value: c for t, c in self.records_by_type.items()},
            "total_size_bytes": self.total_size_bytes,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "avg_retrieval_ms": self.avg_retrieval_ms,
            "last_compaction": self.last_compaction.isoformat()
            if self.last_compaction
            else None,
        }


@dataclass
class MemoryConfig:
    """Configuration for memory subsystem.

    Defines limits, policies, and behavior for
    the tiered memory architecture.
    """

    # L1 Cache settings
    l1_max_items: int = 1000
    l1_max_size_mb: int = 100
    l1_ttl_seconds: int = 3600  # 1 hour

    # L2 Session settings
    l2_max_items: int = 10000
    l2_max_size_mb: int = 1024
    l2_session_ttl_hours: int = 24

    # L3 Persistent settings
    l3_db_path: str = "memory.db"
    l3_enable_fts: bool = True  # Full-text search
    l3_vacuum_interval_hours: int = 24

    # Promotion/demotion
    promote_access_threshold: int = 5  # Promote after N accesses
    demote_idle_seconds: int = 1800  # Demote after 30min idle

    # Retention
    max_episodes_per_agent: int = 1000
    retention_days: int = 90

    # Embeddings
    embedding_dimension: int = 1536
    default_chunk_size: int = 512
    chunk_overlap: int = 50
