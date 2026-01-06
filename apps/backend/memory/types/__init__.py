"""Memory types module - Foundation type definitions for memory system.

This module provides all type definitions for the memory subsystem including:
- MemoryType: Enum for memory classification
- Episode types: Data models for episodic memory
- Query types: Parameters for memory queries

Part of Phase 2: Memory System Architecture
See: docs/architecture/PHASE2_MEMORY_LLM_ARCHITECTURE.md
"""

from .memory_types import (
    MemoryType,
    MemoryTier,
    MemoryPriority,
    MemoryStatus,
    MemoryOperation,
)
from .episode_types import (
    EpisodeRecord,
    EpisodeOutcome,
    EpisodeSeverity,
    EpisodeMetadata,
    ToolInvocation,
)
from .query_types import (
    MemoryQuery,
    QueryFilter,
    QuerySort,
    SortOrder,
    QueryResult,
    PaginationParams,
)

__all__ = [
    # Memory types
    "MemoryType",
    "MemoryTier",
    "MemoryPriority",
    "MemoryStatus",
    "MemoryOperation",
    # Episode types
    "EpisodeRecord",
    "EpisodeOutcome",
    "EpisodeSeverity",
    "EpisodeMetadata",
    "ToolInvocation",
    # Query types
    "MemoryQuery",
    "QueryFilter",
    "QuerySort",
    "SortOrder",
    "QueryResult",
    "PaginationParams",
]
