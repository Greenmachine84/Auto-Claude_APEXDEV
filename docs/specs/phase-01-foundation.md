# Phase 1: Foundation

> **Duration**: Week 1-2 | **Priority**: HIGH
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| BaseEnterpriseAgent class created | Unit tests pass | 100% |
| AgentRegistry functional | Can register/discover agents | ✅ |
| EpisodeStore operational | CRUD operations work | ✅ |
| Existing agents unaffected | Regression tests pass | 100% |
| Documentation complete | All classes documented | ✅ |

### Deliverables

1. `apps/backend/agents/enterprise/base_enterprise.py`
2. `apps/backend/agents/enterprise/__init__.py`
3. `apps/backend/agents/registry.py`
4. `apps/backend/memory/episodes/store.py`
5. `apps/backend/memory/episodes/__init__.py`
6. Unit tests for all new modules
7. Updated `__init__.py` files for imports

---

## Section 1: BaseEnterpriseAgent Class

### Task 1.1: Create Enterprise Directory Structure

**Objective**: Establish directory for enterprise agents

**Steps**:
1. Create `apps/backend/agents/enterprise/` directory
2. Create `__init__.py` with module exports
3. Verify existing `agents/` structure unchanged

**Validation**:
```bash
# Directory exists
test -d apps/backend/agents/enterprise && echo "PASS"

# Init file exists
test -f apps/backend/agents/enterprise/__init__.py && echo "PASS"
```

---

### Task 1.2: Implement BaseEnterpriseAgent

**Objective**: Create LLM-agnostic base class for all enterprise agents

**File**: `apps/backend/agents/enterprise/base_enterprise.py`

**Class Specification**:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class AgentLLMConfig:
    """Per-agent LLM configuration - LLM AGNOSTIC."""
    provider: str           # User-chosen provider
    model: str              # User-chosen model
    fallback_providers: List[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    
class BaseEnterpriseAgent(ABC):
    """Abstract base for all enterprise agents.
    
    CRITICAL: This class is LLM-AGNOSTIC.
    No assumptions about which provider will be used.
    """
    
    def __init__(self, agent_id: str, llm_config: AgentLLMConfig):
        self.agent_id = agent_id
        self.llm_config = llm_config
        self.status = AgentStatus.IDLE
        self.metadata: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type identifier."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        pass
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task - implementation uses configured LLM."""
        pass
    
    async def health_check(self) -> bool:
        """Verify agent is operational."""
        return self.status != AgentStatus.ERROR
```

**Validation**:
- [ ] Class can be imported without errors
- [ ] Cannot instantiate directly (abstract)
- [ ] Subclass can be created and instantiated
- [ ] LLM config is properly stored

---

### Task 1.3: Create Agent Init Module

**File**: `apps/backend/agents/enterprise/__init__.py`

**Content**:
```python
"""Enterprise Agents Module.

Provides LLM-agnostic base classes and utilities
for enterprise agent implementations.
"""

from .base_enterprise import (
    BaseEnterpriseAgent,
    AgentLLMConfig,
    AgentStatus,
)

__all__ = [
    "BaseEnterpriseAgent",
    "AgentLLMConfig", 
    "AgentStatus",
]
```

---

## Section 2: Agent Registry

### Task 2.1: Create AgentRegistry Class

**Objective**: Central registry for agent discovery and management

**File**: `apps/backend/agents/registry.py`

**Class Specification**:

```python
from typing import Dict, List, Optional, Type
from .enterprise.base_enterprise import BaseEnterpriseAgent, AgentLLMConfig

class AgentRegistry:
    """Central registry for all agents.
    
    Supports dynamic registration and discovery.
    """
    
    _instance = None
    _agents: Dict[str, Type[BaseEnterpriseAgent]] = {}
    _instances: Dict[str, BaseEnterpriseAgent] = {}
    
    @classmethod
    def register(cls, agent_class: Type[BaseEnterpriseAgent]) -> None:
        """Register an agent class."""
        agent_type = agent_class.__name__
        cls._agents[agent_type] = agent_class
    
    @classmethod
    def get_agent_class(cls, agent_type: str) -> Optional[Type[BaseEnterpriseAgent]]:
        """Get registered agent class by type."""
        return cls._agents.get(agent_type)
    
    @classmethod
    def create_instance(
        cls, 
        agent_type: str, 
        agent_id: str,
        llm_config: AgentLLMConfig
    ) -> BaseEnterpriseAgent:
        """Create agent instance with LLM config."""
        agent_class = cls.get_agent_class(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        instance = agent_class(agent_id, llm_config)
        cls._instances[agent_id] = instance
        return instance
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent types."""
        return list(cls._agents.keys())
    
    @classmethod
    def get_instance(cls, agent_id: str) -> Optional[BaseEnterpriseAgent]:
        """Get running agent instance."""
        return cls._instances.get(agent_id)
```

**Validation**:
- [ ] Can register agent class
- [ ] Can retrieve registered class
- [ ] Can create instance with LLM config
- [ ] Can list all registered agents

---

## Section 3: Episode Store

### Task 3.1: Create Episodes Directory

**Steps**:
1. Create `apps/backend/memory/episodes/` directory
2. Create `__init__.py`

---

### Task 3.2: Implement EpisodeStore

**Objective**: SQLite-based storage for agent episodes

**File**: `apps/backend/memory/episodes/store.py`

**Class Specification**:

```python
import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

@dataclass
class Episode:
    """Record of an agent interaction."""
    id: Optional[int] = None
    agent_id: str = ""
    task_id: str = ""
    input_text: str = ""
    output_text: str = ""
    tools_used: List[str] = None
    llm_provider: str = ""      # Track which provider was used
    llm_model: str = ""         # Track which model was used
    tokens_used: int = 0
    duration_ms: int = 0
    success: bool = True
    error_message: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class EpisodeStore:
    """SQLite-based episode storage."""
    
    def __init__(self, db_path: str = "episodes.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    input_text TEXT,
                    output_text TEXT,
                    tools_used TEXT,
                    llm_provider TEXT,
                    llm_model TEXT,
                    tokens_used INTEGER,
                    duration_ms INTEGER,
                    success INTEGER,
                    error_message TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_id 
                ON episodes(agent_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_id 
                ON episodes(task_id)
            """)
    
    async def store(self, episode: Episode) -> int:
        """Store episode, return ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO episodes 
                (agent_id, task_id, input_text, output_text, tools_used,
                 llm_provider, llm_model, tokens_used, duration_ms,
                 success, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                episode.agent_id,
                episode.task_id,
                episode.input_text,
                episode.output_text,
                json.dumps(episode.tools_used),
                episode.llm_provider,
                episode.llm_model,
                episode.tokens_used,
                episode.duration_ms,
                1 if episode.success else 0,
                episode.error_message,
                episode.created_at,
            ))
            return cursor.lastrowid
    
    async def get_by_agent(self, agent_id: str, limit: int = 50) -> List[Episode]:
        """Get episodes for an agent."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM episodes 
                WHERE agent_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (agent_id, limit))
            return [self._row_to_episode(row) for row in cursor.fetchall()]
    
    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        """Convert database row to Episode."""
        return Episode(
            id=row["id"],
            agent_id=row["agent_id"],
            task_id=row["task_id"],
            input_text=row["input_text"],
            output_text=row["output_text"],
            tools_used=json.loads(row["tools_used"] or "[]"),
            llm_provider=row["llm_provider"],
            llm_model=row["llm_model"],
            tokens_used=row["tokens_used"],
            duration_ms=row["duration_ms"],
            success=bool(row["success"]),
            error_message=row["error_message"],
            created_at=row["created_at"],
        )
```

**Validation**:
- [ ] Database created on init
- [ ] Can store episode
- [ ] Can retrieve by agent_id
- [ ] Indexes created for performance

---

### Task 3.3: Create Episodes Init Module

**File**: `apps/backend/memory/episodes/__init__.py`

```python
"""Episodes Module - Agent interaction storage."""

from .store import Episode, EpisodeStore

__all__ = ["Episode", "EpisodeStore"]
```

---

## Section 4: Unit Tests

### Task 4.1: Test BaseEnterpriseAgent

**File**: `tests/unit/test_base_enterprise_agent.py`

### Task 4.2: Test AgentRegistry  

**File**: `tests/unit/test_agent_registry.py`

### Task 4.3: Test EpisodeStore

**File**: `tests/unit/test_episode_store.py`

---

## Validation Checklist

- [ ] All files created in correct locations
- [ ] All imports work without errors
- [ ] Unit tests pass (100%)
- [ ] No changes to existing agent files
- [ ] Documentation complete
- [ ] Code follows project style

---

## Dependencies

**Requires**: None (first phase)

**Enables**: Phase 2 (LLM Agnostic Layer)

---

## ADR References

- ADR-001: Core Repository Selection
- ADR-003: Memory System Architecture
- ADR-013: Per-Agent LLM Configuration

---

*Phase 1 Specification v1.0.0*
