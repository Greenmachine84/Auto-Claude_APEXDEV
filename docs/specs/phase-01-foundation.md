# Phase 1: Foundation

> **Duration**: Week 1-2 | **Priority**: HIGH
>
> **Status**: 📋 Specification Ready

---

## ⚠️ QUALITY STANDARDS

> **ALL implementations in this phase MUST meet these mandatory standards:**

| Standard | Requirement | Verification |
|----------|-------------|--------------|
| **World-Class** | Best-in-industry patterns and practices | Code review |
| **Enterprise-Grade** | Production-ready from day one | Load testing |
| **Fully Production Ready** | Zero technical debt, complete error handling | Audit |
| **Clean & Concise Code** | Self-documenting, minimal complexity | Linting + Review |
| **Beyond PhD Level** | Cutting-edge CS principles applied | Architecture review |

---

## Outcome Expectations

### Business Objective

| Objective | Description | Impact |
|-----------|-------------|--------|
| **Platform Foundation** | Establish rock-solid base for enterprise agents | Enables all future phases |
| **LLM Independence** | Create abstraction layer for LLM-agnostic design | Provider flexibility |
| **Learning System** | Enable agents to learn from experience | Continuous improvement |

### Technical Outcome

| Outcome | Description | Measurement |
|---------|-------------|-------------|
| **BaseEnterpriseAgent** | Abstract base class for all enterprise agents with LLM-agnostic design | Instantiable, tested |
| **AgentRegistry** | Central discovery mechanism for dynamic agent registration | Can register/discover |
| **EpisodeStore** | Persistent storage for agent interactions and learning | CRUD functional |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| BaseEnterpriseAgent class created | Unit tests pass | 100% | Clean abstractions, SOLID principles |
| AgentRegistry functional | Can register/discover agents | ✅ | O(1) lookup, thread-safe |
| EpisodeStore operational | CRUD operations work | ✅ | <10ms latency, ACID compliant |
| Existing agents unaffected | Regression tests pass | 100% | Zero breaking changes |
| Documentation complete | All classes documented | ✅ | Docstrings, examples, diagrams |
| Code coverage | Test coverage measured | >95% | Industry-leading coverage |
| Type safety | Static type checking | 100% | Full mypy compliance |

### Acceptance Tests

| Test | Input | Expected Output | Passing Criteria |
|------|-------|-----------------|------------------|
| AT-1.1 | Import BaseEnterpriseAgent | No errors | Import succeeds in <100ms |
| AT-1.2 | Direct instantiation attempt | TypeError | Abstract class enforced |
| AT-1.3 | Subclass instantiation | Instance created | All properties accessible |
| AT-1.4 | Register agent to registry | Success confirmation | Agent discoverable |
| AT-1.5 | Create agent from registry | Instance with LLM config | Correct provider assigned |
| AT-1.6 | Store episode | Episode ID returned | ID > 0, data persisted |
| AT-1.7 | Retrieve episodes by agent | List of episodes | Ordered by created_at DESC |
| AT-1.8 | Concurrent episode writes | All succeed | No race conditions |

### Performance Metrics

| Metric | Target | World-Class Standard |
|--------|--------|----------------------|
| Agent instantiation | <10ms | Sub-millisecond preferred |
| Registry lookup | <1ms | O(1) constant time |
| Episode store write | <20ms | Optimized batch writes available |
| Episode query (50 records) | <50ms | Indexed queries |
| Memory footprint per agent | <5MB | Efficient object lifecycle |
| Concurrent agent limit | 100+ | Scalable architecture |

### Risk Mitigations

| Risk | Mitigation | Verification |
|------|------------|--------------|
| Registry concurrency issues | Thread-safe singleton pattern | Stress test with 1000 concurrent registrations |
| SQLite locking | WAL mode + connection pooling | Concurrent write tests |
| Memory leaks in agents | Weak references for instances | Long-running memory profile |
| Import cycles | Lazy imports, clean dependency graph | Import order tests |

### Integration Points

| Phase | Component | Integration |
|-------|-----------|-------------|
| Phase 2 | LLM Abstraction | BaseEnterpriseAgent uses AgentLLMConfig |
| Phase 4 | Orchestration | AgentRegistry provides agent discovery |
| Phase 5 | Memory | EpisodeStore integrates with H-MEM |
| Phase 7 | Enterprise Agents | All agents extend BaseEnterpriseAgent |

### User-Visible Impact

| Impact | Description |
|--------|-------------|
| **Foundation for Agents** | Users will be able to use enterprise agents (Phase 7) |
| **LLM Flexibility** | Per-agent LLM config structure established |
| **Learning Capability** | Agents can learn from past interactions |

### Deliverables

| # | Deliverable | Purpose | LOC Estimate |
|---|-------------|---------|--------------|
| 1 | `apps/backend/agents/enterprise/base_enterprise.py` | Abstract base class | 150-200 |
| 2 | `apps/backend/agents/enterprise/__init__.py` | Module exports | 20-30 |
| 3 | `apps/backend/agents/registry.py` | Agent discovery | 100-150 |
| 4 | `apps/backend/memory/episodes/store.py` | Episode persistence | 200-250 |
| 5 | `apps/backend/memory/episodes/__init__.py` | Module exports | 10-15 |
| 6 | `tests/unit/test_base_enterprise_agent.py` | Unit tests | 150-200 |
| 7 | `tests/unit/test_agent_registry.py` | Unit tests | 100-150 |
| 8 | `tests/unit/test_episode_store.py` | Unit tests | 150-200 |

---

## Section 1: BaseEnterpriseAgent Class

### Task 1.1: Create Enterprise Directory Structure

**Objective**: Establish directory for enterprise agents

**Quality Gate**: Directory structure follows Python package best practices

**Steps**:

| Step | Action | Verification |
|------|--------|--------------|
| 1.1.1 | Create `apps/backend/agents/enterprise/` directory | `test -d` passes |
| 1.1.2 | Create `__init__.py` with module docstring | File exists, PEP 257 compliant |
| 1.1.3 | Verify existing `agents/` structure unchanged | Diff shows no changes |

**Validation**:
```bash
# Directory exists
test -d apps/backend/agents/enterprise && echo "PASS"

# Init file exists
test -f apps/backend/agents/enterprise/__init__.py && echo "PASS"

# No changes to existing files
git diff --quiet apps/backend/agents/core && echo "PASS: No changes to core"
```

**Expected Outcome**: Clean directory structure ready for enterprise agent implementation

---

### Task 1.2: Implement BaseEnterpriseAgent

**Objective**: Create LLM-agnostic base class for all enterprise agents

**Quality Gate**: SOLID principles, 100% type coverage, comprehensive docstrings

**File**: `apps/backend/agents/enterprise/base_enterprise.py`

**Class Specification**:

```python
"""BaseEnterpriseAgent - World-Class Enterprise Agent Foundation.

This module provides the abstract base class for all enterprise agents.
Designed to be LLM-agnostic, production-ready, and extensible.

Design Patterns:
    - Template Method Pattern for execute lifecycle
    - Strategy Pattern for LLM provider selection
    - Observer Pattern for status changes

Quality Standards:
    - 100% type annotated
    - Full PEP 257 docstrings
    - Thread-safe state management
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TypeVar, Generic
from enum import Enum
from datetime import datetime
import threading
import uuid

class AgentStatus(Enum):
    """Agent operational status.
    
    States follow a finite state machine pattern with valid transitions.
    """
    IDLE = "idle"           # Ready to accept tasks
    ACTIVE = "active"       # Currently processing
    PAUSED = "paused"       # Temporarily suspended
    ERROR = "error"         # Encountered error, needs attention
    TERMINATED = "terminated"  # Permanently stopped

@dataclass
class AgentLLMConfig:
    """Per-agent LLM configuration - FULLY LLM AGNOSTIC.
    
    This configuration allows each agent to use ANY provider.
    No defaults - user must explicitly configure.
    
    Attributes:
        provider: User-chosen provider (e.g., "openrouter", "ollama")
        model: User-chosen model (e.g., "gpt-4", "llama-3")
        fallback_providers: Ordered list of backup providers
        max_tokens: Maximum tokens for responses
        temperature: Creativity setting (0.0-1.0)
        
    Example:
        >>> config = AgentLLMConfig(
        ...     provider="openrouter",
        ...     model="anthropic/claude-3-opus",
        ...     fallback_providers=["ollama", "openai"]
        ... )
    """
    provider: str           # User-chosen provider
    model: str              # User-chosen model
    fallback_providers: List[str] = field(default_factory=list)
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 120
    retry_attempts: int = 3
    cost_limit_per_task: Optional[float] = None

@dataclass
class TaskResult:
    """Result of agent task execution.
    
    Provides comprehensive information about task completion.
    """
    success: bool
    output: Any
    error: Optional[str] = None
    duration_ms: int = 0
    tokens_used: int = 0
    llm_provider_used: str = ""
    llm_model_used: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseEnterpriseAgent(ABC):
    """Abstract base for all enterprise agents.
    
    CRITICAL DESIGN PRINCIPLES:
    1. LLM-AGNOSTIC: No assumptions about which provider will be used
    2. THREAD-SAFE: All state changes are protected
    3. OBSERVABLE: Status changes can be monitored
    4. EXTENSIBLE: Easy to subclass and customize
    
    World-Class Implementation Features:
    - Lifecycle hooks (pre/post execute)
    - Automatic retry with exponential backoff
    - Comprehensive error handling
    - Performance metrics collection
    - Resource cleanup guarantees
    
    Example:
        >>> class MyAgent(BaseEnterpriseAgent):
        ...     @property
        ...     def agent_type(self) -> str:
        ...         return "MyAgent"
        ...     
        ...     @property
        ...     def capabilities(self) -> List[str]:
        ...         return ["analysis", "generation"]
        ...     
        ...     async def execute(self, task: Dict[str, Any]) -> TaskResult:
        ...         # Implementation here
        ...         pass
    """
    
    _status_lock: threading.Lock
    
    def __init__(self, agent_id: str, llm_config: AgentLLMConfig):
        """Initialize enterprise agent.
        
        Args:
            agent_id: Unique identifier for this agent instance
            llm_config: LLM provider configuration (user-defined)
            
        Raises:
            ValueError: If agent_id is empty or llm_config is invalid
        """
        if not agent_id:
            raise ValueError("agent_id cannot be empty")
        if not llm_config.provider or not llm_config.model:
            raise ValueError("llm_config must have provider and model set")
            
        self.agent_id = agent_id
        self.llm_config = llm_config
        self._status = AgentStatus.IDLE
        self._status_lock = threading.Lock()
        self.metadata: Dict[str, Any] = {}
        self._created_at = datetime.utcnow()
        self._last_activity = self._created_at
        self._task_count = 0
        self._error_count = 0
    
    @property
    def status(self) -> AgentStatus:
        """Thread-safe status access."""
        with self._status_lock:
            return self._status
    
    @status.setter
    def status(self, value: AgentStatus) -> None:
        """Thread-safe status update with validation."""
        with self._status_lock:
            self._validate_status_transition(self._status, value)
            self._status = value
    
    def _validate_status_transition(self, from_status: AgentStatus, to_status: AgentStatus) -> None:
        """Validate state machine transitions."""
        valid_transitions = {
            AgentStatus.IDLE: [AgentStatus.ACTIVE, AgentStatus.TERMINATED],
            AgentStatus.ACTIVE: [AgentStatus.IDLE, AgentStatus.PAUSED, AgentStatus.ERROR],
            AgentStatus.PAUSED: [AgentStatus.ACTIVE, AgentStatus.IDLE, AgentStatus.TERMINATED],
            AgentStatus.ERROR: [AgentStatus.IDLE, AgentStatus.TERMINATED],
            AgentStatus.TERMINATED: [],  # Terminal state
        }
        if to_status not in valid_transitions.get(from_status, []):
            raise ValueError(f"Invalid transition: {from_status} -> {to_status}")
    
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type identifier.
        
        Returns:
            String identifier for this agent type (e.g., "CodeReviewAgent")
        """
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return list of agent capabilities.
        
        Returns:
            List of capability strings (e.g., ["code-review", "security-scan"])
        """
        pass
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        """Execute task using configured LLM.
        
        This is the main entry point for agent work. Implementations
        should use self.llm_config to determine which LLM provider to use.
        
        Args:
            task: Task specification dictionary
            
        Returns:
            TaskResult with success status and output
        """
        pass
    
    async def pre_execute(self, task: Dict[str, Any]) -> bool:
        """Hook called before execute. Override for custom validation.
        
        Returns:
            True if execution should proceed, False to abort
        """
        return True
    
    async def post_execute(self, task: Dict[str, Any], result: TaskResult) -> None:
        """Hook called after execute. Override for cleanup/logging."""
        pass
    
    async def health_check(self) -> bool:
        """Verify agent is operational.
        
        Returns:
            True if agent can accept tasks
        """
        return self.status not in [AgentStatus.ERROR, AgentStatus.TERMINATED]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics.
        
        Returns:
            Dictionary with task count, error rate, uptime, etc.
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "task_count": self._task_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._task_count, 1),
            "created_at": self._created_at.isoformat(),
            "last_activity": self._last_activity.isoformat(),
            "llm_provider": self.llm_config.provider,
            "llm_model": self.llm_config.model,
        }
```

**Validation Checklist**:
- [ ] Class can be imported without errors
- [ ] Cannot instantiate directly (abstract)
- [ ] Subclass can be created and instantiated
- [ ] LLM config is properly stored
- [ ] Thread-safe status transitions work
- [ ] All type hints validate with mypy
- [ ] Docstrings are PEP 257 compliant

**Expected Outcome**: Production-ready base class that sets the foundation for all enterprise agents with world-class code quality.

---

### Task 1.3: Create Agent Init Module

**Objective**: Create clean, well-documented module exports

**Quality Gate**: All exports documented, no circular imports

**File**: `apps/backend/agents/enterprise/__init__.py`

**Content**:
```python
"""Enterprise Agents Module - World-Class Agent Foundation.

This module provides LLM-agnostic base classes and utilities
for enterprise agent implementations.

Exports:
    BaseEnterpriseAgent: Abstract base for all enterprise agents
    AgentLLMConfig: Per-agent LLM configuration
    AgentStatus: Agent operational status enum
    TaskResult: Result of agent task execution

Example:
    >>> from apps.backend.agents.enterprise import BaseEnterpriseAgent, AgentLLMConfig
    >>> 
    >>> config = AgentLLMConfig(provider="openrouter", model="gpt-4")
    >>> # Create custom agent extending BaseEnterpriseAgent
"""

from .base_enterprise import (
    BaseEnterpriseAgent,
    AgentLLMConfig,
    AgentStatus,
    TaskResult,
)

__all__ = [
    "BaseEnterpriseAgent",
    "AgentLLMConfig", 
    "AgentStatus",
    "TaskResult",
]

__version__ = "1.0.0"
```

**Expected Outcome**: Clean module interface ready for consumption by other phases.

---

## Section 2: Agent Registry

### Task 2.1: Create AgentRegistry Class

**Objective**: Central registry for agent discovery and management

**Quality Gate**: Thread-safe singleton, O(1) lookups, comprehensive error handling

**File**: `apps/backend/agents/registry.py`

**Class Specification**:

```python
"""AgentRegistry - Enterprise-Grade Agent Discovery System.

This module provides centralized agent registration and discovery
with thread-safe operations and production-ready error handling.

Design Patterns:
    - Singleton Pattern for global registry
    - Factory Pattern for agent instantiation
    - Registry Pattern for type management

Quality Standards:
    - Thread-safe for concurrent access
    - O(1) lookup performance
    - Comprehensive logging
"""

from typing import Dict, List, Optional, Type, Callable
from threading import RLock
import logging

from .enterprise.base_enterprise import BaseEnterpriseAgent, AgentLLMConfig

logger = logging.getLogger(__name__)

class AgentNotFoundError(Exception):
    """Raised when requested agent type is not registered."""
    pass

class AgentAlreadyRegisteredError(Exception):
    """Raised when attempting to register duplicate agent."""
    pass

class AgentRegistry:
    """Central registry for all agents - Singleton Pattern.
    
    Thread-safe implementation supporting concurrent registration
    and discovery operations.
    
    World-Class Features:
    - Singleton ensures single source of truth
    - RLock allows recursive locking
    - Decorator-based registration
    - Type-safe instantiation
    
    Example:
        >>> @AgentRegistry.register
        ... class MyAgent(BaseEnterpriseAgent):
        ...     pass
        >>> 
        >>> agent = AgentRegistry.create_instance(
        ...     "MyAgent", "agent-001", llm_config
        ... )
    """
    
    _instance: Optional['AgentRegistry'] = None
    _lock: RLock = RLock()
    _agents: Dict[str, Type[BaseEnterpriseAgent]] = {}
    _instances: Dict[str, BaseEnterpriseAgent] = {}
    
    def __new__(cls) -> 'AgentRegistry':
        """Singleton pattern implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    @classmethod
    def register(cls, agent_class: Type[BaseEnterpriseAgent]) -> Type[BaseEnterpriseAgent]:
        """Register an agent class. Can be used as decorator.
        
        Args:
            agent_class: Class extending BaseEnterpriseAgent
            
        Returns:
            The registered class (for decorator pattern)
            
        Raises:
            AgentAlreadyRegisteredError: If agent type already registered
            TypeError: If class doesn't extend BaseEnterpriseAgent
        """
        if not issubclass(agent_class, BaseEnterpriseAgent):
            raise TypeError(f"{agent_class.__name__} must extend BaseEnterpriseAgent")
        
        agent_type = agent_class.__name__
        
        with cls._lock:
            if agent_type in cls._agents:
                raise AgentAlreadyRegisteredError(
                    f"Agent type '{agent_type}' already registered"
                )
            cls._agents[agent_type] = agent_class
            logger.info(f"Registered agent type: {agent_type}")
        
        return agent_class
    
    @classmethod
    def unregister(cls, agent_type: str) -> bool:
        """Unregister an agent type.
        
        Args:
            agent_type: Name of agent class to unregister
            
        Returns:
            True if was registered and removed, False if not found
        """
        with cls._lock:
            if agent_type in cls._agents:
                del cls._agents[agent_type]
                logger.info(f"Unregistered agent type: {agent_type}")
                return True
            return False
    
    @classmethod
    def get_agent_class(cls, agent_type: str) -> Optional[Type[BaseEnterpriseAgent]]:
        """Get registered agent class by type.
        
        Args:
            agent_type: Name of agent class
            
        Returns:
            Agent class or None if not found
        """
        with cls._lock:
            return cls._agents.get(agent_type)
    
    @classmethod
    def create_instance(
        cls, 
        agent_type: str, 
        agent_id: str,
        llm_config: AgentLLMConfig
    ) -> BaseEnterpriseAgent:
        """Create agent instance with LLM config.
        
        Args:
            agent_type: Name of registered agent class
            agent_id: Unique identifier for this instance
            llm_config: LLM provider configuration
            
        Returns:
            Configured agent instance
            
        Raises:
            AgentNotFoundError: If agent_type not registered
        """
        with cls._lock:
            agent_class = cls._agents.get(agent_type)
            if not agent_class:
                available = list(cls._agents.keys())
                raise AgentNotFoundError(
                    f"Agent type '{agent_type}' not found. "
                    f"Available: {available}"
                )
            
            instance = agent_class(agent_id, llm_config)
            cls._instances[agent_id] = instance
            logger.info(
                f"Created agent instance: {agent_id} ({agent_type}) "
                f"with LLM {llm_config.provider}/{llm_config.model}"
            )
            return instance
    
    @classmethod
    def get_instance(cls, agent_id: str) -> Optional[BaseEnterpriseAgent]:
        """Get running agent instance by ID.
        
        Args:
            agent_id: Unique agent instance identifier
            
        Returns:
            Agent instance or None if not found
        """
        with cls._lock:
            return cls._instances.get(agent_id)
    
    @classmethod
    def list_types(cls) -> List[str]:
        """List all registered agent types.
        
        Returns:
            List of agent type names
        """
        with cls._lock:
            return list(cls._agents.keys())
    
    @classmethod
    def list_instances(cls) -> List[str]:
        """List all active agent instance IDs.
        
        Returns:
            List of agent instance IDs
        """
        with cls._lock:
            return list(cls._instances.keys())
    
    @classmethod
    def destroy_instance(cls, agent_id: str) -> bool:
        """Remove and cleanup agent instance.
        
        Args:
            agent_id: ID of instance to destroy
            
        Returns:
            True if found and destroyed, False if not found
        """
        with cls._lock:
            if agent_id in cls._instances:
                instance = cls._instances.pop(agent_id)
                instance.status = instance.status.TERMINATED
                logger.info(f"Destroyed agent instance: {agent_id}")
                return True
            return False
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registrations and instances. USE WITH CAUTION."""
        with cls._lock:
            cls._agents.clear()
            cls._instances.clear()
            logger.warning("Registry cleared - all agents removed")
```

**Validation Checklist**:
- [ ] Singleton pattern works correctly
- [ ] Thread-safe for concurrent access
- [ ] Can register agent class
- [ ] Can use decorator pattern
- [ ] Can create instance with LLM config
- [ ] Can list all registered agents
- [ ] Error handling is comprehensive

**Expected Outcome**: Production-ready registry that handles agent lifecycle with world-class thread safety.

---

## Section 3: Episode Store

### Task 3.1: Create Episodes Directory

**Steps**:

| Step | Action | Verification |
|------|--------|--------------|
| 3.1.1 | Create `apps/backend/memory/episodes/` directory | Directory exists |
| 3.1.2 | Create `__init__.py` | File exists with exports |

---

### Task 3.2: Implement EpisodeStore

**Objective**: SQLite-based storage for agent episodes with production-grade reliability

**Quality Gate**: ACID compliant, indexed queries, connection pooling

**File**: `apps/backend/memory/episodes/store.py`

**Class Specification**:

```python
"""EpisodeStore - Enterprise-Grade Agent Memory System.

This module provides persistent storage for agent interactions,
enabling learning from experience and audit trails.

Design Patterns:
    - Repository Pattern for data access
    - Unit of Work Pattern for transactions
    - Connection Pooling for performance

Quality Standards:
    - ACID compliant transactions
    - Indexed queries for performance
    - WAL mode for concurrent access
    - Prepared statements for security
"""

import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from contextlib import contextmanager
import threading
import logging

logger = logging.getLogger(__name__)

@dataclass
class Episode:
    """Record of an agent interaction - Immutable after creation.
    
    Captures complete context of agent task execution for
    learning, debugging, and audit purposes.
    
    Attributes:
        id: Database primary key (auto-assigned)
        agent_id: Identifier of agent that created this episode
        task_id: Identifier of task being executed
        input_text: Input provided to agent
        output_text: Output generated by agent
        tools_used: List of tools invoked during execution
        llm_provider: Which LLM provider was used
        llm_model: Which model was used
        tokens_used: Total tokens consumed
        duration_ms: Execution time in milliseconds
        success: Whether task completed successfully
        error_message: Error details if failed
        created_at: ISO timestamp of creation
        metadata: Additional context (JSON serialized)
    """
    id: Optional[int] = None
    agent_id: str = ""
    task_id: str = ""
    input_text: str = ""
    output_text: str = ""
    tools_used: List[str] = field(default_factory=list)
    llm_provider: str = ""
    llm_model: str = ""
    tokens_used: int = 0
    duration_ms: int = 0
    success: bool = True
    error_message: str = ""
    created_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class EpisodeStore:
    """SQLite-based episode storage - Production Ready.
    
    World-Class Features:
    - WAL mode for concurrent reads during writes
    - Connection pooling via context manager
    - Prepared statements prevent SQL injection
    - Indexed queries for fast retrieval
    - Batch operations for bulk inserts
    - Automatic schema migration support
    
    Example:
        >>> store = EpisodeStore("episodes.db")
        >>> episode = Episode(agent_id="agent-001", task_id="task-123")
        >>> episode_id = await store.store(episode)
        >>> episodes = await store.get_by_agent("agent-001", limit=10)
    """
    
    _local = threading.local()
    
    def __init__(self, db_path: str = "data/episodes.db"):
        """Initialize episode store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"EpisodeStore initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row
            # Enable WAL mode for concurrent access
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        
        try:
            yield self._local.conn
        except Exception:
            self._local.conn.rollback()
            raise
    
    def _init_db(self) -> None:
        """Initialize database schema with migrations support."""
        with self._get_connection() as conn:
            # Create episodes table
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
                    tokens_used INTEGER DEFAULT 0,
                    duration_ms INTEGER DEFAULT 0,
                    success INTEGER DEFAULT 1,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_agent_id 
                ON episodes(agent_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_task_id 
                ON episodes(task_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_created_at 
                ON episodes(created_at DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_agent_created 
                ON episodes(agent_id, created_at DESC)
            """)
            
            conn.commit()
            logger.debug("Episode database schema initialized")
    
    async def store(self, episode: Episode) -> int:
        """Store episode, return assigned ID.
        
        Args:
            episode: Episode to persist
            
        Returns:
            Assigned episode ID
            
        Raises:
            sqlite3.Error: On database failure
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO episodes 
                (agent_id, task_id, input_text, output_text, tools_used,
                 llm_provider, llm_model, tokens_used, duration_ms,
                 success, error_message, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                json.dumps(episode.metadata),
            ))
            conn.commit()
            episode_id = cursor.lastrowid
            logger.debug(f"Stored episode {episode_id} for agent {episode.agent_id}")
            return episode_id
    
    async def store_batch(self, episodes: List[Episode]) -> List[int]:
        """Store multiple episodes in single transaction.
        
        Args:
            episodes: List of episodes to persist
            
        Returns:
            List of assigned episode IDs
        """
        ids = []
        with self._get_connection() as conn:
            for episode in episodes:
                cursor = conn.execute("""
                    INSERT INTO episodes 
                    (agent_id, task_id, input_text, output_text, tools_used,
                     llm_provider, llm_model, tokens_used, duration_ms,
                     success, error_message, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(episode.metadata),
                ))
                ids.append(cursor.lastrowid)
            conn.commit()
        logger.info(f"Batch stored {len(ids)} episodes")
        return ids
    
    async def get_by_id(self, episode_id: int) -> Optional[Episode]:
        """Get episode by ID.
        
        Args:
            episode_id: Primary key
            
        Returns:
            Episode if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM episodes WHERE id = ?",
                (episode_id,)
            )
            row = cursor.fetchone()
            return self._row_to_episode(row) if row else None
    
    async def get_by_agent(
        self, 
        agent_id: str, 
        limit: int = 50,
        offset: int = 0,
        success_only: bool = False
    ) -> List[Episode]:
        """Get episodes for an agent with pagination.
        
        Args:
            agent_id: Agent identifier
            limit: Maximum episodes to return
            offset: Number of episodes to skip
            success_only: If True, only return successful episodes
            
        Returns:
            List of episodes, ordered by created_at DESC
        """
        query = """
            SELECT * FROM episodes 
            WHERE agent_id = ?
        """
        params = [agent_id]
        
        if success_only:
            query += " AND success = 1"
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_episode(row) for row in cursor.fetchall()]
    
    async def get_by_task(self, task_id: str) -> List[Episode]:
        """Get all episodes for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of episodes for the task
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM episodes WHERE task_id = ? ORDER BY created_at",
                (task_id,)
            )
            return [self._row_to_episode(row) for row in cursor.fetchall()]
    
    async def count_by_agent(self, agent_id: str) -> int:
        """Count episodes for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Total episode count
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM episodes WHERE agent_id = ?",
                (agent_id,)
            )
            return cursor.fetchone()[0]
    
    async def get_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get aggregated statistics for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Dictionary with total_episodes, success_rate, avg_duration, etc.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(success) as successes,
                    AVG(duration_ms) as avg_duration,
                    SUM(tokens_used) as total_tokens,
                    MIN(created_at) as first_episode,
                    MAX(created_at) as last_episode
                FROM episodes 
                WHERE agent_id = ?
            """, (agent_id,))
            row = cursor.fetchone()
            
            return {
                "agent_id": agent_id,
                "total_episodes": row["total"] or 0,
                "successful_episodes": row["successes"] or 0,
                "success_rate": (row["successes"] or 0) / max(row["total"] or 1, 1),
                "avg_duration_ms": row["avg_duration"] or 0,
                "total_tokens_used": row["total_tokens"] or 0,
                "first_episode": row["first_episode"],
                "last_episode": row["last_episode"],
            }
    
    async def delete_by_agent(self, agent_id: str) -> int:
        """Delete all episodes for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Number of episodes deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM episodes WHERE agent_id = ?",
                (agent_id,)
            )
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Deleted {deleted} episodes for agent {agent_id}")
            return deleted
    
    async def cleanup_old(self, days: int = 90) -> int:
        """Delete episodes older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of episodes deleted
        """
        cutoff = datetime.utcnow().isoformat()[:10]  # Date only
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM episodes WHERE date(created_at) < date(?, '-' || ? || ' days')",
                (cutoff, days)
            )
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Cleanup: deleted {deleted} episodes older than {days} days")
            return deleted
    
    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        """Convert database row to Episode object."""
        return Episode(
            id=row["id"],
            agent_id=row["agent_id"],
            task_id=row["task_id"],
            input_text=row["input_text"] or "",
            output_text=row["output_text"] or "",
            tools_used=json.loads(row["tools_used"] or "[]"),
            llm_provider=row["llm_provider"] or "",
            llm_model=row["llm_model"] or "",
            tokens_used=row["tokens_used"] or 0,
            duration_ms=row["duration_ms"] or 0,
            success=bool(row["success"]),
            error_message=row["error_message"] or "",
            created_at=row["created_at"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
```

**Validation Checklist**:
- [ ] Database created on init
- [ ] WAL mode enabled
- [ ] Can store episode
- [ ] Can retrieve by agent_id
- [ ] Can batch store episodes
- [ ] Indexes created for performance
- [ ] Connection pooling works
- [ ] Concurrent access is safe

**Expected Outcome**: Enterprise-grade episode storage with world-class performance and reliability.

---

### Task 3.3: Create Episodes Init Module

**File**: `apps/backend/memory/episodes/__init__.py`

```python
"""Episodes Module - Agent Interaction Memory System.

This module provides persistent storage for agent episodes,
enabling learning from experience and maintaining audit trails.

Exports:
    Episode: Data class representing an agent interaction
    EpisodeStore: SQLite-based persistent storage

Example:
    >>> from apps.backend.memory.episodes import Episode, EpisodeStore
    >>> 
    >>> store = EpisodeStore()
    >>> episode = Episode(
    ...     agent_id="agent-001",
    ...     task_id="task-123",
    ...     input_text="Analyze this code",
    ...     output_text="Analysis complete...",
    ...     llm_provider="openrouter",
    ...     llm_model="gpt-4"
    ... )
    >>> episode_id = await store.store(episode)
"""

from .store import Episode, EpisodeStore

__all__ = ["Episode", "EpisodeStore"]

__version__ = "1.0.0"
```

---

## Section 4: Unit Tests

### Task 4.1: Test BaseEnterpriseAgent

**File**: `tests/unit/test_base_enterprise_agent.py`

**Test Cases**:
- Test abstract class cannot be instantiated
- Test subclass can be created
- Test LLM config is stored correctly
- Test status transitions
- Test thread-safe status updates
- Test validation errors for invalid config

### Task 4.2: Test AgentRegistry  

**File**: `tests/unit/test_agent_registry.py`

**Test Cases**:
- Test singleton pattern
- Test register/unregister
- Test decorator pattern
- Test create instance with LLM config
- Test concurrent registration
- Test error handling

### Task 4.3: Test EpisodeStore

**File**: `tests/unit/test_episode_store.py`

**Test Cases**:
- Test database creation
- Test store/retrieve episode
- Test batch operations
- Test pagination
- Test statistics
- Test cleanup
- Test concurrent access

---

## Validation Checklist

| Item | Check | Status |
|------|-------|--------|
| All files created in correct locations | File system check | ⬜ |
| All imports work without errors | Python import test | ⬜ |
| Unit tests pass (100%) | pytest execution | ⬜ |
| Test coverage >95% | coverage report | ⬜ |
| No changes to existing agent files | Git diff | ⬜ |
| Documentation complete (docstrings) | Docstring check | ⬜ |
| Type hints validate (mypy) | mypy execution | ⬜ |
| Code style (PEP 8) | ruff/flake8 | ⬜ |
| World-class patterns used | Architecture review | ⬜ |
| Production-ready error handling | Code review | ⬜ |

---

## Dependencies

**Requires**: None (first phase)

**Enables**: Phase 2 (LLM Agnostic Layer)

---

## ADR References

- ADR-001: Core Repository Selection
- ADR-003: Memory System Architecture
- ADR-005: LLM-Agnostic Architecture
- ADR-013: Per-Agent LLM Configuration

---

*Phase 1 Specification v2.0.0 - Enhanced with World-Class Outcome Expectations*
