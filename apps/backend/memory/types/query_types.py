"""Query type definitions for memory operations.

Provides query builders, filters, and result types
for searching and retrieving memories.

Part of Phase 2: Memory System Architecture
"""

from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from dataclasses import dataclass, field
from datetime import datetime

from .memory_types import MemoryType, MemoryTier, MemoryPriority
from .episode_types import EpisodeOutcome, EpisodeSeverity


T = TypeVar("T")


class SortOrder(Enum):
    """Sort order for query results."""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(Enum):
    """Operators for query filters."""
    EQ = "eq"           # Equal
    NE = "ne"           # Not equal
    GT = "gt"           # Greater than
    GTE = "gte"         # Greater than or equal
    LT = "lt"           # Less than
    LTE = "lte"         # Less than or equal
    IN = "in"           # In list
    NOT_IN = "not_in"   # Not in list
    CONTAINS = "contains"  # Contains substring
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"     # Regular expression match
    EXISTS = "exists"   # Field exists
    IS_NULL = "is_null" # Field is null


@dataclass
class QueryFilter:
    """Single filter condition for queries.
    
    Attributes:
        field: Field name to filter on
        operator: Comparison operator
        value: Value to compare against
    """
    field: str
    operator: FilterOperator
    value: Any
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value,
        }
    
    @classmethod
    def eq(cls, field: str, value: Any) -> "QueryFilter":
        """Create equality filter."""
        return cls(field=field, operator=FilterOperator.EQ, value=value)
    
    @classmethod
    def contains(cls, field: str, value: str) -> "QueryFilter":
        """Create contains filter."""
        return cls(field=field, operator=FilterOperator.CONTAINS, value=value)
    
    @classmethod
    def in_list(cls, field: str, values: List[Any]) -> "QueryFilter":
        """Create in-list filter."""
        return cls(field=field, operator=FilterOperator.IN, value=values)
    
    @classmethod
    def between(cls, field: str, min_val: Any, max_val: Any) -> List["QueryFilter"]:
        """Create range filter (returns two filters)."""
        return [
            cls(field=field, operator=FilterOperator.GTE, value=min_val),
            cls(field=field, operator=FilterOperator.LTE, value=max_val),
        ]


@dataclass
class QuerySort:
    """Sort specification for query results."""
    field: str
    order: SortOrder = SortOrder.DESC
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "field": self.field,
            "order": self.order.value,
        }


@dataclass
class PaginationParams:
    """Pagination parameters for queries."""
    offset: int = 0
    limit: int = 50
    
    @property
    def page_number(self) -> int:
        """Calculate current page number (1-based)."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1
    
    def next_page(self) -> "PaginationParams":
        """Get params for next page."""
        return PaginationParams(offset=self.offset + self.limit, limit=self.limit)
    
    def prev_page(self) -> "PaginationParams":
        """Get params for previous page."""
        return PaginationParams(
            offset=max(0, self.offset - self.limit), 
            limit=self.limit
        )


@dataclass
class MemoryQuery:
    """Query specification for memory retrieval.
    
    Fluent builder pattern for constructing complex queries
    against the memory subsystem.
    """
    # Target specification
    memory_type: Optional[MemoryType] = None
    memory_tier: Optional[MemoryTier] = None
    
    # Episode-specific filters
    agent_id: Optional[str] = None
    agent_type: Optional[str] = None
    task_id: Optional[str] = None
    outcome: Optional[EpisodeOutcome] = None
    severity: Optional[EpisodeSeverity] = None
    priority: Optional[MemoryPriority] = None
    
    # Time filters
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    
    # Text search
    text_query: Optional[str] = None
    semantic_query: Optional[str] = None
    similarity_threshold: float = 0.7
    
    # Generic filters
    filters: List[QueryFilter] = field(default_factory=list)
    
    # Sorting
    sort_by: List[QuerySort] = field(default_factory=list)
    
    # Pagination
    pagination: PaginationParams = field(default_factory=PaginationParams)
    
    # Options
    include_embedding: bool = False
    include_metadata: bool = True
    
    def by_agent(self, agent_id: str) -> "MemoryQuery":
        """Filter by agent ID."""
        self.agent_id = agent_id
        return self
    
    def by_type(self, agent_type: str) -> "MemoryQuery":
        """Filter by agent type."""
        self.agent_type = agent_type
        return self
    
    def by_task(self, task_id: str) -> "MemoryQuery":
        """Filter by task ID."""
        self.task_id = task_id
        return self
    
    def successful_only(self) -> "MemoryQuery":
        """Filter to successful episodes only."""
        self.outcome = EpisodeOutcome.SUCCESS
        return self
    
    def failed_only(self) -> "MemoryQuery":
        """Filter to failed episodes only."""
        self.outcome = EpisodeOutcome.FAILURE
        return self
    
    def with_severity(self, severity: EpisodeSeverity) -> "MemoryQuery":
        """Filter by severity level."""
        self.severity = severity
        return self
    
    def since_time(self, timestamp: datetime) -> "MemoryQuery":
        """Filter to episodes after timestamp."""
        self.since = timestamp
        return self
    
    def until_time(self, timestamp: datetime) -> "MemoryQuery":
        """Filter to episodes before timestamp."""
        self.until = timestamp
        return self
    
    def search_text(self, query: str) -> "MemoryQuery":
        """Add full-text search query."""
        self.text_query = query
        return self
    
    def search_semantic(self, query: str, threshold: float = 0.7) -> "MemoryQuery":
        """Add semantic similarity search."""
        self.semantic_query = query
        self.similarity_threshold = threshold
        return self
    
    def add_filter(self, filter_: QueryFilter) -> "MemoryQuery":
        """Add custom filter."""
        self.filters.append(filter_)
        return self
    
    def order_by(self, field: str, order: SortOrder = SortOrder.DESC) -> "MemoryQuery":
        """Add sort specification."""
        self.sort_by.append(QuerySort(field=field, order=order))
        return self
    
    def limit(self, n: int) -> "MemoryQuery":
        """Set result limit."""
        self.pagination.limit = n
        return self
    
    def offset(self, n: int) -> "MemoryQuery":
        """Set result offset."""
        self.pagination.offset = n
        return self
    
    def with_embeddings(self) -> "MemoryQuery":
        """Include embeddings in results."""
        self.include_embedding = True
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary representation."""
        return {
            "memory_type": self.memory_type.value if self.memory_type else None,
            "memory_tier": self.memory_tier.value if self.memory_tier else None,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "task_id": self.task_id,
            "outcome": self.outcome.value if self.outcome else None,
            "severity": self.severity.value if self.severity else None,
            "since": self.since.isoformat() if self.since else None,
            "until": self.until.isoformat() if self.until else None,
            "text_query": self.text_query,
            "semantic_query": self.semantic_query,
            "similarity_threshold": self.similarity_threshold,
            "filters": [f.to_dict() for f in self.filters],
            "sort_by": [s.to_dict() for s in self.sort_by],
            "pagination": {
                "offset": self.pagination.offset,
                "limit": self.pagination.limit,
            },
            "include_embedding": self.include_embedding,
            "include_metadata": self.include_metadata,
        }


@dataclass
class QueryResult(Generic[T]):
    """Result container for memory queries.
    
    Generic type T represents the item type (e.g., EpisodeRecord).
    """
    items: List[T]
    total_count: int
    query_time_ms: float
    pagination: PaginationParams
    
    # Optional semantic search metadata
    relevance_scores: Optional[List[float]] = None
    
    @property
    def has_more(self) -> bool:
        """Check if more results are available."""
        return self.pagination.offset + len(self.items) < self.total_count
    
    @property
    def is_empty(self) -> bool:
        """Check if result set is empty."""
        return len(self.items) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "items": [item.to_dict() if hasattr(item, "to_dict") else item for item in self.items],
            "total_count": self.total_count,
            "query_time_ms": self.query_time_ms,
            "pagination": {
                "offset": self.pagination.offset,
                "limit": self.pagination.limit,
            },
            "has_more": self.has_more,
            "relevance_scores": self.relevance_scores,
        }
