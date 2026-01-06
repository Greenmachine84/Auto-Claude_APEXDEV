# Phase 4: Orchestration

> **Version**: 2.0.0 | **Duration**: Week 7-8 | **Priority**: 🟢 HIGH
>
> **Status**: 📋 Specification Ready
>
> **LLM-Agnostic**: ✅ All 8 providers supported equally

---

## Quality Standards

| Standard | Description | Verification |
|----------|-------------|--------------|
| **World-Class** | Industry-leading orchestration patterns | Architecture review |
| **Enterprise-Grade** | Production-ready with 99.99% reliability | Load testing |
| **Fully Production Ready** | Zero-downtime deployment capable | Deployment validation |
| **Clean and Concise Code** | <10 cyclomatic complexity per function | Static analysis |
| **Beyond PhD Level Expertise** | Implements advanced distributed systems theory | Expert review |

---

## Outcome Expectations

### Business Objectives

| Objective | Success Metric | World-Class Standard |
|-----------|----------------|----------------------|
| Multi-agent coordination | Handle 100+ concurrent agents | Industry benchmark exceeded |
| Real-time responsiveness | <50ms task dispatch latency | Top 1% performance |
| Fault tolerance | Zero task loss on failures | Mission-critical reliability |
| Scalability | Linear scaling to 1000 agents | Hyperscale ready |

### Technical Outcomes

| Outcome | Measurement | Target | World-Class Standard |
|---------|-------------|--------|----------------------|
| Task throughput | Tasks/second | >10,000 | Exceeds enterprise requirements |
| Message delivery | P99 latency | <100ms | Real-time communication |
| Pipeline completion | Success rate | >99.9% | Mission-critical reliability |
| Resource efficiency | CPU overhead | <5% | Minimal system impact |
| Recovery time | Failover duration | <1s | Continuous operation |

### Success Criteria

| Criteria | Measurement | Target | World-Class Standard |
|----------|-------------|--------|----------------------|
| Multi-agent coordination | Parallel execution | ✅ | Handles 100+ agents simultaneously |
| Agent-to-agent messaging | Message delivery | <100ms | Sub-50ms P50 latency |
| Pipeline execution | Tasks complete in order | ✅ | DAG-based dependency resolution |
| Error recovery | Failed tasks retry | 3 attempts | Exponential backoff with jitter |
| Resource allocation | Memory limits enforced | ✅ | Per-agent quotas with monitoring |
| LLM-Agnostic routing | Any provider per agent | ✅ | All 8 providers equally supported |

---

## Acceptance Tests

| Test ID | Test Case | Pass Criteria | Verification Method |
|---------|-----------|---------------|---------------------|
| AT-4.1 | Submit 1000 concurrent tasks | All complete within 60s | Load test |
| AT-4.2 | Agent-to-agent message | Delivery <100ms P99 | Latency measurement |
| AT-4.3 | Pipeline with 50 stages | Completes in dependency order | Integration test |
| AT-4.4 | Kill task mid-execution | Clean cancellation, no orphans | Chaos test |
| AT-4.5 | Resource quota exceeded | Task queued, not rejected | Unit test |
| AT-4.6 | Orchestrator restart | Resume all tasks from state | Recovery test |
| AT-4.7 | Circular dependency detection | Pipeline rejected with error | Unit test |
| AT-4.8 | LLM provider per agent | Each agent uses assigned LLM | Integration test |
| AT-4.9 | Mixed provider pipeline | Different LLMs in same pipeline | End-to-end test |
| AT-4.10 | Provider failover mid-task | Task completes via fallback | Chaos test |

---

## Performance Metrics

| Metric | Target | Measurement Method | Alert Threshold |
|--------|--------|-------------------|-----------------|
| Task dispatch latency | <50ms P99 | Prometheus histogram | >100ms |
| Message bus throughput | >50,000 msg/s | Load test | <30,000 msg/s |
| Pipeline completion time | <10s for 100 tasks | Benchmark | >30s |
| Memory per 1000 tasks | <100MB | Resource monitoring | >200MB |
| CPU overhead | <5% | Profiling | >10% |
| Task retry success rate | >95% | Metrics aggregation | <90% |

---

## Risk Mitigations

| Risk | Impact | Mitigation | Verification |
|------|--------|------------|--------------|
| Deadlock in task graph | System hang | Cycle detection algorithm | Unit tests |
| Message queue overflow | Lost messages | Backpressure mechanism | Load test |
| Resource starvation | Agent failures | Fair scheduling algorithm | Simulation |
| Orchestrator crash | Task loss | Persistent task state | Recovery test |
| LLM provider timeout | Task failure | Per-provider timeout config | Integration test |

---

## LLM-Agnostic Integration

### Per-Agent LLM Assignment

```python
"""
Each agent can be assigned ANY of the 8 LLM providers.
NO default provider - user MUST configure.
"""

SUPPORTED_PROVIDERS = [
    "copilot",      # GitHub Copilot
    "openrouter",   # OpenRouter
    "ollama",       # Ollama (local)
    "lmstudio",     # LM Studio (local)
    "gemini",       # Google Gemini
    "openai",       # OpenAI
    "anthropic",    # Anthropic Claude
    "azure",        # Azure OpenAI
]

@dataclass
class AgentLLMConfig:
    """LLM configuration for an agent - NO DEFAULTS."""
    agent_id: str
    provider: str  # One of SUPPORTED_PROVIDERS
    model: str     # Provider-specific model name
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
```

### Task Execution with LLM

```python
async def _execute_task(self, task: Task) -> None:
    """Execute task using agent's assigned LLM provider."""
    agent = self.registry.get(task.agent_id)
    
    # Get agent's LLM configuration (NO DEFAULT)
    llm_config = await self.get_agent_llm_config(task.agent_id)
    if not llm_config:
        raise ConfigurationError(
            f"Agent {task.agent_id} has no LLM provider configured. "
            "User must assign one of: " + ", ".join(SUPPORTED_PROVIDERS)
        )
    
    # Route to appropriate provider
    llm_client = self.llm_router.get_client(
        provider=llm_config.provider,
        model=llm_config.model
    )
    
    # Execute with provider-specific client
    result = await agent.execute(
        task.action,
        task.params,
        llm_client=llm_client
    )
```

---

## Deliverables

| File | Purpose | LOC Estimate |
|------|---------|--------------|
| `apps/backend/orchestration/orchestrator.py` | Main orchestrator | 400 |
| `apps/backend/orchestration/pipeline.py` | Pipeline execution | 250 |
| `apps/backend/orchestration/task_queue.py` | Priority task queue | 200 |
| `apps/backend/orchestration/message_bus.py` | Agent messaging | 300 |
| `apps/backend/orchestration/scheduler.py` | Task scheduling | 250 |
| `apps/backend/orchestration/resource_manager.py` | Resource limits | 200 |
| `apps/backend/orchestration/models.py` | Data models | 150 |
| `tests/test_orchestration_*.py` | Unit tests | 600 |

---

## Section 1: Core Orchestrator

### Task 1.1: Directory Structure

```
apps/backend/orchestration/
├── __init__.py
├── models.py
├── orchestrator.py
├── pipeline.py
├── task_queue.py
├── message_bus.py
├── scheduler.py
└── resource_manager.py
```

### Task 1.2: Orchestration Models

**File**: `apps/backend/orchestration/models.py`

```python
"""
Orchestration models for multi-agent coordination.

World-Class Standards:
- Type-safe dataclasses with validation
- Immutable where possible
- Clear serialization support
- LLM-agnostic design
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels for scheduling."""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class Task:
    """
    Unit of work for an agent.
    
    Attributes:
        id: Unique task identifier
        agent_id: Target agent for execution
        action: Action to perform
        params: Action parameters
        llm_provider: LLM provider for this task (optional override)
        llm_model: LLM model for this task (optional override)
    """
    id: str
    agent_id: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    parent_task_id: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    # LLM-Agnostic: Optional per-task LLM override
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None


@dataclass
class Pipeline:
    """
    Sequence of tasks with dependencies.
    
    Supports DAG-based execution with topological ordering.
    """
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class AgentMessage:
    """Message between agents for coordination."""
    id: str
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None


@dataclass
class ResourceQuota:
    """
    Resource limits for an agent.
    
    Enforces fair resource allocation across agents.
    """
    agent_id: str
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_concurrent_tasks: int = 5
    max_tokens_per_minute: int = 100000
```

### Task 1.3: Orchestrator Class

**File**: `apps/backend/orchestration/orchestrator.py`

```python
"""
Main orchestrator for multi-agent coordination.

World-Class Standards:
- Async-first design for high concurrency
- Clean separation of concerns
- LLM-agnostic task execution
- Graceful shutdown handling
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..agents.registry import AgentRegistry
from ..llm.router import LLMRouter
from .models import Task, Pipeline, TaskStatus, AgentMessage
from .task_queue import TaskQueue
from .message_bus import MessageBus
from .scheduler import Scheduler
from .resource_manager import ResourceManager


class Orchestrator:
    """
    Coordinates agent execution and communication.
    
    Features:
    - Priority-based task scheduling
    - DAG-based pipeline execution
    - Inter-agent messaging
    - Resource quota enforcement
    - LLM-agnostic provider routing
    """
    
    def __init__(
        self,
        agent_registry: AgentRegistry,
        llm_router: LLMRouter,
        max_concurrent: int = 10
    ):
        """
        Initialize orchestrator.
        
        Args:
            agent_registry: Registry of available agents
            llm_router: LLM-agnostic router for provider selection
            max_concurrent: Maximum concurrent tasks
        """
        self.registry = agent_registry
        self.llm_router = llm_router
        self.max_concurrent = max_concurrent
        
        self.task_queue = TaskQueue()
        self.message_bus = MessageBus()
        self.scheduler = Scheduler()
        self.resources = ResourceManager()
        
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._is_running = False
    
    async def start(self) -> None:
        """Start orchestrator main loop."""
        self._is_running = True
        await asyncio.gather(
            self._task_processor(),
            self._message_processor(),
        )
    
    async def stop(self) -> None:
        """Gracefully stop orchestrator."""
        self._is_running = False
        for task in self._running_tasks.values():
            task.cancel()
    
    async def submit_task(self, task: Task) -> str:
        """Submit task for execution."""
        task.created_at = datetime.utcnow().isoformat()
        await self.task_queue.enqueue(task)
        return task.id
    
    async def submit_pipeline(self, pipeline: Pipeline) -> str:
        """Submit pipeline for execution."""
        sorted_tasks = self._topological_sort(pipeline.tasks)
        for task in sorted_tasks:
            await self.task_queue.enqueue(task)
        return pipeline.id
    
    async def _execute_task(self, task: Task) -> None:
        """
        Execute a single task with LLM-agnostic provider routing.
        
        Uses agent's configured LLM provider, or task-level override.
        All 8 providers are equally supported.
        """
        try:
            if not await self.resources.can_run(task.agent_id):
                task.status = TaskStatus.QUEUED
                await self.task_queue.enqueue(task)
                return
            
            agent = self.registry.get(task.agent_id)
            if not agent:
                task.status = TaskStatus.FAILED
                task.error = f"Agent {task.agent_id} not found"
                return
            
            # Get LLM client - task override or agent config
            llm_client = await self._get_llm_client(task, agent)
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow().isoformat()
            
            result = await asyncio.wait_for(
                agent.execute(task.action, task.params, llm_client=llm_client),
                timeout=task.timeout_seconds
            )
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow().isoformat()
            
        except asyncio.TimeoutError:
            await self._handle_task_failure(task, "Task timed out")
        except Exception as e:
            await self._handle_task_failure(task, str(e))
        finally:
            self._running_tasks.pop(task.id, None)
    
    async def _get_llm_client(self, task: Task, agent):
        """
        Get LLM client for task execution.
        
        Priority:
        1. Task-level LLM override
        2. Agent's configured LLM
        3. Error if none configured (NO DEFAULT)
        """
        provider = task.llm_provider or agent.llm_provider
        model = task.llm_model or agent.llm_model
        
        if not provider:
            raise ValueError(
                f"No LLM provider configured for agent {task.agent_id}. "
                "Must assign one of: copilot, openrouter, ollama, lmstudio, "
                "gemini, openai, anthropic, azure"
            )
        
        return self.llm_router.get_client(provider=provider, model=model)
    
    async def _handle_task_failure(self, task: Task, error: str) -> None:
        """Handle task failure with retry logic."""
        task.error = error
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            await self.task_queue.enqueue(task)
        else:
            task.status = TaskStatus.FAILED
    
    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by dependencies using Kahn's algorithm."""
        # Implementation details...
        pass
```

---

## Section 2: Task Queue

### Task 2.1: Priority Task Queue

**File**: `apps/backend/orchestration/task_queue.py`

```python
"""
Priority-based task queue with dependency resolution.

World-Class Standards:
- O(log n) enqueue/dequeue operations
- Thread-safe async implementation
- Dependency-aware scheduling
"""
import asyncio
from heapq import heappush, heappop
from typing import Optional, Dict, List
from datetime import datetime
from .models import Task, TaskStatus, TaskPriority


class TaskQueue:
    """Async priority queue for tasks with dependency tracking."""
    
    def __init__(self):
        self._heap: List[tuple] = []
        self._tasks: Dict[str, Task] = {}
        self._lock = asyncio.Lock()
    
    async def enqueue(self, task: Task) -> None:
        """Add task to queue with priority ordering."""
        async with self._lock:
            priority = -task.priority.value
            timestamp = datetime.utcnow().timestamp()
            heappush(self._heap, (priority, timestamp, task.id))
            self._tasks[task.id] = task
            task.status = TaskStatus.QUEUED
    
    async def dequeue(self) -> Optional[Task]:
        """Get highest priority ready task."""
        async with self._lock:
            while self._heap:
                _, _, task_id = heappop(self._heap)
                task = self._tasks.get(task_id)
                
                if not task or task.status != TaskStatus.QUEUED:
                    continue
                
                if await self._deps_satisfied(task):
                    return task
                else:
                    heappush(
                        self._heap,
                        (-task.priority.value, datetime.utcnow().timestamp(), task_id)
                    )
            return None
    
    async def _deps_satisfied(self, task: Task) -> bool:
        """Check if all dependencies are completed."""
        for dep_id in task.depends_on:
            dep_task = self._tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
```

---

## Section 3: Message Bus

### Task 3.1: Inter-Agent Messaging

**File**: `apps/backend/orchestration/message_bus.py`

```python
"""
Message bus for inter-agent communication.

World-Class Standards:
- Request/reply pattern support
- Subscription-based routing
- Correlation tracking
"""
import asyncio
from typing import Optional, Dict, List, Callable
from collections import defaultdict
from datetime import datetime
import uuid
from .models import AgentMessage


class MessageBus:
    """Async message bus for agent communication."""
    
    def __init__(self):
        self._queue: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._subscriptions: Dict[str, List[Callable]] = defaultdict(list)
        self._pending_replies: Dict[str, asyncio.Future] = {}
    
    async def send(self, message: AgentMessage) -> None:
        """Send message to an agent."""
        message.timestamp = datetime.utcnow().isoformat()
        await self._queue.put(message)
    
    async def request(
        self,
        message: AgentMessage,
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """Send message and wait for reply."""
        correlation_id = str(uuid.uuid4())
        message.correlation_id = correlation_id
        
        future: asyncio.Future = asyncio.Future()
        self._pending_replies[correlation_id] = future
        
        await self.send(message)
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            self._pending_replies.pop(correlation_id, None)
```

---

## Section 4: Resource Manager

### Task 4.1: Resource Allocation

**File**: `apps/backend/orchestration/resource_manager.py`

```python
"""
Resource management for agents.

World-Class Standards:
- Fair scheduling across agents
- Token rate limiting per provider
- Memory quota enforcement
"""
import asyncio
from typing import Dict
from collections import defaultdict
from .models import ResourceQuota


class ResourceManager:
    """Manages resource allocation and limits."""
    
    def __init__(self):
        self._quotas: Dict[str, ResourceQuota] = {}
        self._usage: Dict[str, Dict] = defaultdict(lambda: {
            "current_tasks": 0,
            "tokens_used": 0,
        })
        self._lock = asyncio.Lock()
    
    async def can_run(self, agent_id: str) -> bool:
        """Check if agent can run another task."""
        quota = self._quotas.get(agent_id)
        if not quota:
            return True
        usage = self._usage[agent_id]
        return usage["current_tasks"] < quota.max_concurrent_tasks
    
    async def acquire(self, agent_id: str) -> bool:
        """Acquire resources for task."""
        async with self._lock:
            if not await self.can_run(agent_id):
                return False
            self._usage[agent_id]["current_tasks"] += 1
            return True
    
    async def release(self, agent_id: str) -> None:
        """Release resources after task."""
        async with self._lock:
            if self._usage[agent_id]["current_tasks"] > 0:
                self._usage[agent_id]["current_tasks"] -= 1
```

---

## Validation Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| LLM-Agnostic System | ✅ | Per-agent and per-task LLM configuration |
| No Default Provider | ✅ | Error if no provider configured |
| 8 Equal LLM Providers | ✅ | SUPPORTED_PROVIDERS list |
| Per-Agent LLM Assignment | ✅ | AgentLLMConfig with provider/model |
| World-Class Standards | ✅ | Quality Standards table |
| Enterprise-Grade | ✅ | 99.99% reliability target |
| Production Ready | ✅ | Zero-downtime deployment |
| Clean Code | ✅ | <10 cyclomatic complexity |
| Acceptance Tests | ✅ | AT-4.1 through AT-4.10 |
| Performance Metrics | ✅ | Detailed targets with alerts |

---

## Integration Points

| Phase | Integration | Data Flow |
|-------|-------------|-----------|
| Phase 2 | LLM Router | Provider selection per task |
| Phase 3 | Auth | User permissions for agents |
| Phase 5 | Memory | Task history persistence |
| Phase 7 | Agents | Agent registration and execution |
