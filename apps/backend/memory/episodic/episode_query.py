"""Fluent query builder for episode retrieval.

Part of Phase 2: Memory System Architecture
"""

from typing import Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

from ..types.episode_types import EpisodeRecord, EpisodeOutcome, EpisodeSeverity
from ..types.query_types import SortOrder

if TYPE_CHECKING:
    from .episode_store import EpisodeStore


@dataclass
class EpisodeQueryBuilder:
    """Fluent query builder for episodes."""
    
    _store: Optional["EpisodeStore"] = None
    _agent_id: Optional[str] = None
    _agent_type: Optional[str] = None
    _task_id: Optional[str] = None
    _outcome: Optional[EpisodeOutcome] = None
    _severity: Optional[EpisodeSeverity] = None
    _since: Optional[datetime] = None
    _until: Optional[datetime] = None
    _text_query: Optional[str] = None
    _tools: List[str] = field(default_factory=list)
    _sort_field: str = "created_at"
    _sort_order: SortOrder = SortOrder.DESC
    _limit: int = 50
    _offset: int = 0
    
    def with_store(self, store: "EpisodeStore") -> "EpisodeQueryBuilder":
        self._store = store
        return self
    
    def by_agent(self, agent_id: str) -> "EpisodeQueryBuilder":
        self._agent_id = agent_id
        return self
    
    def by_type(self, agent_type: str) -> "EpisodeQueryBuilder":
        self._agent_type = agent_type
        return self
    
    def by_task(self, task_id: str) -> "EpisodeQueryBuilder":
        self._task_id = task_id
        return self
    
    def successful(self) -> "EpisodeQueryBuilder":
        self._outcome = EpisodeOutcome.SUCCESS
        return self
    
    def failed(self) -> "EpisodeQueryBuilder":
        self._outcome = EpisodeOutcome.FAILURE
        return self
    
    def with_outcome(self, outcome: EpisodeOutcome) -> "EpisodeQueryBuilder":
        self._outcome = outcome
        return self
    
    def with_severity(self, severity: EpisodeSeverity) -> "EpisodeQueryBuilder":
        self._severity = severity
        return self
    
    def since(self, timestamp: datetime) -> "EpisodeQueryBuilder":
        self._since = timestamp
        return self
    
    def until(self, timestamp: datetime) -> "EpisodeQueryBuilder":
        self._until = timestamp
        return self
    
    def search(self, text: str) -> "EpisodeQueryBuilder":
        self._text_query = text
        return self
    
    def using_tools(self, *tools: str) -> "EpisodeQueryBuilder":
        self._tools = list(tools)
        return self
    
    def order_by(self, field: str, order: SortOrder = SortOrder.DESC) -> "EpisodeQueryBuilder":
        self._sort_field = field
        self._sort_order = order
        return self
    
    def limit(self, n: int) -> "EpisodeQueryBuilder":
        self._limit = n
        return self
    
    def offset(self, n: int) -> "EpisodeQueryBuilder":
        self._offset = n
        return self
    
    def build_sql(self) -> tuple[str, list]:
        conditions = []
        params: List[Any] = []
        
        if self._agent_id:
            conditions.append("agent_id = ?")
            params.append(self._agent_id)
        if self._agent_type:
            conditions.append("agent_type = ?")
            params.append(self._agent_type)
        if self._task_id:
            conditions.append("task_id = ?")
            params.append(self._task_id)
        if self._outcome:
            conditions.append("outcome = ?")
            params.append(self._outcome.value)
        if self._severity:
            conditions.append("severity = ?")
            params.append(self._severity.value)
        if self._since:
            conditions.append("created_at >= ?")
            params.append(self._since)
        if self._until:
            conditions.append("created_at <= ?")
            params.append(self._until)
        
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order = f"ORDER BY {self._sort_field} {self._sort_order.value.upper()}"
        limit = f"LIMIT {self._limit} OFFSET {self._offset}"
        
        sql = f"SELECT * FROM episodes {where} {order} {limit}"
        return sql, params
    
    def execute(self) -> List[EpisodeRecord]:
        if not self._store:
            raise ValueError("No store configured")
        
        if self._text_query:
            return self._store.search_text(self._text_query, self._limit)
        
        sql, params = self.build_sql()
        conn = self._store._get_conn()
        rows = conn.execute(sql, params).fetchall()
        return [self._store._row_to_episode(r) for r in rows]
