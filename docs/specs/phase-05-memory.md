# Phase 5: Memory

> **Duration**: Week 9-10 | **Priority**: 🟡 MEDIUM
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| Episode storage | CRUD operations work | ✅ |
| Memory search | Semantic retrieval | <500ms |
| Cross-agent memory | Shared context access | ✅ |
| Provider abstraction | Multiple backends | 3+ |
| Memory persistence | Data survives restart | ✅ |

### Deliverables

1. `apps/backend/memory/store/episode_store.py`
2. `apps/backend/memory/store/working_memory.py`
3. `apps/backend/memory/store/long_term_memory.py`
4. `apps/backend/memory/search/semantic_search.py`
5. `apps/backend/memory/providers/base_memory.py`
6. `apps/backend/memory/providers/sqlite_memory.py`
7. `apps/backend/memory/providers/neo4j_memory.py`
8. `apps/backend/memory/providers/vector_memory.py`
9. Unit tests for all modules

---

## Section 1: Memory Architecture

### Task 1.1: Directory Structure

```
apps/backend/memory/
├── __init__.py
├── models.py
├── store/
│   ├── __init__.py
│   ├── episode_store.py
│   ├── working_memory.py
│   └── long_term_memory.py
├── search/
│   ├── __init__.py
│   ├── semantic_search.py
│   └── index_manager.py
└── providers/
    ├── __init__.py
    ├── base_memory.py
    ├── sqlite_memory.py
    ├── neo4j_memory.py
    └── vector_memory.py
```

---

### Task 1.2: Memory Models

**File**: `apps/backend/memory/models.py`

```python
"""Memory models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MemoryType(Enum):
    EPISODE = "episode"      # Task execution memory
    WORKING = "working"      # Short-term active memory
    LONG_TERM = "long_term"  # Persistent knowledge
    SEMANTIC = "semantic"    # Conceptual knowledge
    PROCEDURAL = "procedural"  # How-to knowledge

class MemoryScope(Enum):
    AGENT = "agent"          # Agent-specific
    SHARED = "shared"        # Cross-agent
    GLOBAL = "global"        # System-wide

@dataclass
class MemoryEntry:
    """Base memory entry."""
    id: str
    content: str
    memory_type: MemoryType
    scope: MemoryScope = MemoryScope.AGENT
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = ""
    updated_at: str = ""
    accessed_at: str = ""
    access_count: int = 0
    relevance_score: float = 0.0
    ttl_seconds: Optional[int] = None  # None = no expiry
    
    def __post_init__(self):
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if not self.accessed_at:
            self.accessed_at = now

@dataclass
class Episode:
    """Task execution episode."""
    id: str
    agent_id: str
    task_id: str
    action: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "started"
    started_at: str = ""
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    tokens_used: int = 0
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    parent_episode_id: Optional[str] = None
    child_episode_ids: List[str] = field(default_factory=list)

@dataclass
class MemoryQuery:
    """Query for memory search."""
    query: str
    memory_types: List[MemoryType] = field(default_factory=list)
    scope: Optional[MemoryScope] = None
    agent_id: Optional[str] = None
    limit: int = 10
    min_relevance: float = 0.0
    include_expired: bool = False

@dataclass
class SearchResult:
    """Memory search result."""
    entry: MemoryEntry
    score: float
    highlights: List[str] = field(default_factory=list)
```

---

## Section 2: Memory Providers

### Task 2.1: Base Memory Provider

**File**: `apps/backend/memory/providers/base_memory.py`

```python
"""Abstract base for memory providers."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..models import MemoryEntry, Episode, MemoryQuery, SearchResult

class BaseMemoryProvider(ABC):
    """Abstract memory storage backend."""
    
    def __init__(self, provider_id: str):
        self.provider_id = provider_id
        self._configured = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def supports_vector(self) -> bool:
        """Whether provider supports vector search."""
        pass
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure provider."""
        pass
    
    # CRUD operations
    @abstractmethod
    async def store(self, entry: MemoryEntry) -> str:
        """Store memory entry, return ID."""
        pass
    
    @abstractmethod
    async def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get entry by ID."""
        pass
    
    @abstractmethod
    async def update(self, entry: MemoryEntry) -> bool:
        """Update existing entry."""
        pass
    
    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """Delete entry."""
        pass
    
    # Search
    @abstractmethod
    async def search(self, query: MemoryQuery) -> List[SearchResult]:
        """Search memories."""
        pass
    
    # Episode-specific
    @abstractmethod
    async def store_episode(self, episode: Episode) -> str:
        """Store execution episode."""
        pass
    
    @abstractmethod
    async def get_episodes(
        self, 
        agent_id: str, 
        limit: int = 100
    ) -> List[Episode]:
        """Get agent's recent episodes."""
        pass
    
    # Maintenance
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired entries, return count."""
        pass
```

---

### Task 2.2: SQLite Memory Provider

**File**: `apps/backend/memory/providers/sqlite_memory.py`

```python
"""SQLite-based memory storage."""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from .base_memory import BaseMemoryProvider
from ..models import MemoryEntry, Episode, MemoryQuery, SearchResult, MemoryType, MemoryScope

class SQLiteMemoryProvider(BaseMemoryProvider):
    """SQLite implementation (default provider)."""
    
    def __init__(self):
        super().__init__("sqlite")
        self.db_path: Optional[Path] = None
    
    @property
    def name(self) -> str:
        return "SQLite Memory"
    
    @property
    def supports_vector(self) -> bool:
        return False  # Use vector_memory for semantic search
    
    async def configure(self, config: Dict[str, Any]) -> bool:
        self.db_path = Path(config.get("db_path", "memory.db"))
        self._init_db()
        self._configured = True
        return True
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    agent_id TEXT,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    accessed_at TEXT,
                    access_count INTEGER DEFAULT 0,
                    ttl_seconds INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    status TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    duration_ms INTEGER,
                    tokens_used INTEGER,
                    llm_provider TEXT,
                    llm_model TEXT,
                    parent_episode_id TEXT
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ep_agent ON episodes(agent_id)")
    
    async def store(self, entry: MemoryEntry) -> str:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories 
                (id, content, memory_type, scope, agent_id, metadata, 
                 created_at, updated_at, accessed_at, access_count, ttl_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                entry.content,
                entry.memory_type.value,
                entry.scope.value,
                entry.agent_id,
                json.dumps(entry.metadata),
                entry.created_at,
                entry.updated_at,
                entry.accessed_at,
                entry.access_count,
                entry.ttl_seconds,
            ))
        return entry.id
    
    async def get(self, entry_id: str) -> Optional[MemoryEntry]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?", (entry_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Update access stats
            conn.execute("""
                UPDATE memories 
                SET accessed_at = ?, access_count = access_count + 1
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), entry_id))
            
            return self._row_to_entry(row)
    
    def _row_to_entry(self, row) -> MemoryEntry:
        return MemoryEntry(
            id=row["id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            scope=MemoryScope(row["scope"]),
            agent_id=row["agent_id"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            accessed_at=row["accessed_at"],
            access_count=row["access_count"],
            ttl_seconds=row["ttl_seconds"],
        )
    
    async def update(self, entry: MemoryEntry) -> bool:
        entry.updated_at = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories SET
                content = ?, metadata = ?, updated_at = ?
                WHERE id = ?
            """, (
                entry.content,
                json.dumps(entry.metadata),
                entry.updated_at,
                entry.id,
            ))
        return True
    
    async def delete(self, entry_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (entry_id,))
        return True
    
    async def search(self, query: MemoryQuery) -> List[SearchResult]:
        # Basic text search (for vector search, use vector_memory)
        conditions = ["1=1"]
        params = []
        
        if query.memory_types:
            placeholders = ",".join("?" * len(query.memory_types))
            conditions.append(f"memory_type IN ({placeholders})")
            params.extend(t.value for t in query.memory_types)
        
        if query.scope:
            conditions.append("scope = ?")
            params.append(query.scope.value)
        
        if query.agent_id:
            conditions.append("(agent_id = ? OR scope = 'shared' OR scope = 'global')")
            params.append(query.agent_id)
        
        conditions.append("content LIKE ?")
        params.append(f"%{query.query}%")
        params.append(query.limit)
        
        sql = f"""
            SELECT * FROM memories
            WHERE {' AND '.join(conditions)}
            ORDER BY accessed_at DESC
            LIMIT ?
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            return [
                SearchResult(
                    entry=self._row_to_entry(row),
                    score=1.0,  # Basic search has no relevance score
                )
                for row in cursor.fetchall()
            ]
    
    async def store_episode(self, episode: Episode) -> str:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO episodes
                (id, agent_id, task_id, action, input_data, output_data,
                 status, started_at, completed_at, duration_ms, tokens_used,
                 llm_provider, llm_model, parent_episode_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                episode.id,
                episode.agent_id,
                episode.task_id,
                episode.action,
                json.dumps(episode.input_data),
                json.dumps(episode.output_data) if episode.output_data else None,
                episode.status,
                episode.started_at,
                episode.completed_at,
                episode.duration_ms,
                episode.tokens_used,
                episode.llm_provider,
                episode.llm_model,
                episode.parent_episode_id,
            ))
        return episode.id
    
    async def get_episodes(self, agent_id: str, limit: int = 100) -> List[Episode]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM episodes
                WHERE agent_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (agent_id, limit))
            
            return [self._row_to_episode(row) for row in cursor.fetchall()]
    
    def _row_to_episode(self, row) -> Episode:
        return Episode(
            id=row["id"],
            agent_id=row["agent_id"],
            task_id=row["task_id"],
            action=row["action"],
            input_data=json.loads(row["input_data"] or "{}"),
            output_data=json.loads(row["output_data"]) if row["output_data"] else None,
            status=row["status"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            duration_ms=row["duration_ms"],
            tokens_used=row["tokens_used"],
            llm_provider=row["llm_provider"],
            llm_model=row["llm_model"],
            parent_episode_id=row["parent_episode_id"],
        )
    
    async def cleanup_expired(self) -> int:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM memories
                WHERE ttl_seconds IS NOT NULL
                AND datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime(?)
            """, (now,))
            return cursor.rowcount
```

---

### Task 2.3: Vector Memory Provider

**File**: `apps/backend/memory/providers/vector_memory.py`

**Features**:
- Embedding generation (uses LLM Router from Phase 2)
- Cosine similarity search
- Integration with existing embedding providers (OpenAI, Voyage, etc.)

---

### Task 2.4: Neo4j Memory Provider (Optional)

**File**: `apps/backend/memory/providers/neo4j_memory.py`

**Features**:
- Graph-based memory storage
- Relationship modeling between memories
- Graphiti integration hook

---

## Section 3: Memory Manager

### Task 3.1: Unified Memory Manager

**File**: `apps/backend/memory/memory_manager.py`

```python
"""Unified memory management."""
from typing import Dict, Optional, List
from .models import MemoryEntry, Episode, MemoryQuery, SearchResult, MemoryScope
from .providers.base_memory import BaseMemoryProvider
from .providers.sqlite_memory import SQLiteMemoryProvider

class MemoryManager:
    """Unified interface for all memory operations."""
    
    def __init__(self):
        self._providers: Dict[str, BaseMemoryProvider] = {}
        self._default_provider: Optional[str] = None
    
    async def register_provider(
        self, 
        provider: BaseMemoryProvider,
        is_default: bool = False
    ) -> None:
        """Register memory provider."""
        self._providers[provider.provider_id] = provider
        if is_default or not self._default_provider:
            self._default_provider = provider.provider_id
    
    async def initialize_default(self) -> None:
        """Initialize with SQLite as default."""
        sqlite = SQLiteMemoryProvider()
        await sqlite.configure({"db_path": "memory.db"})
        await self.register_provider(sqlite, is_default=True)
    
    def get_provider(
        self, 
        provider_id: Optional[str] = None
    ) -> BaseMemoryProvider:
        """Get provider by ID or default."""
        pid = provider_id or self._default_provider
        if pid not in self._providers:
            raise ValueError(f"Provider {pid} not registered")
        return self._providers[pid]
    
    # Convenience methods delegating to default provider
    async def store(self, entry: MemoryEntry) -> str:
        return await self.get_provider().store(entry)
    
    async def get(self, entry_id: str) -> Optional[MemoryEntry]:
        return await self.get_provider().get(entry_id)
    
    async def search(self, query: MemoryQuery) -> List[SearchResult]:
        provider = self.get_provider()
        
        # If query needs vector search but provider doesn't support it
        if not provider.supports_vector:
            # Fall back to text search
            pass
        
        return await provider.search(query)
    
    async def store_episode(self, episode: Episode) -> str:
        return await self.get_provider().store_episode(episode)
    
    async def get_agent_context(
        self, 
        agent_id: str,
        query: str,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Get relevant context for agent."""
        mq = MemoryQuery(
            query=query,
            agent_id=agent_id,
            limit=limit,
        )
        results = await self.search(mq)
        return [r.entry for r in results]
```

---

## Validation Checklist

- [ ] Memory CRUD operations work
- [ ] Episode storage and retrieval works
- [ ] Text search finds relevant entries
- [ ] SQLite provider fully functional
- [ ] Memory scopes enforced
- [ ] TTL expiration works
- [ ] Access tracking works
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 1 (Foundation), Phase 2 (LLM for embeddings)

**Enables**: Phase 7 (Enterprise Agents)

---

## ADR References

- ADR-009: Memory Architecture Alignment

---

*Phase 5 Specification v1.0.0*
