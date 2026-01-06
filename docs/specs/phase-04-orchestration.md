# Phase 4: Orchestration

> **Duration**: Week 7-8 | **Priority**: 🟢 HIGH
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| Multi-agent coordination | Parallel execution | ✅ |
| Agent-to-agent messaging | Message delivery | <100ms |
| Pipeline execution | Tasks complete in order | ✅ |
| Error recovery | Failed tasks retry | 3 attempts |
| Resource allocation | Memory limits enforced | ✅ |

### Deliverables

1. `apps/backend/orchestration/orchestrator.py`
2. `apps/backend/orchestration/pipeline.py`
3. `apps/backend/orchestration/task_queue.py`
4. `apps/backend/orchestration/message_bus.py`
5. `apps/backend/orchestration/scheduler.py`
6. `apps/backend/orchestration/resource_manager.py`
7. Unit tests for all modules

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

---

### Task 1.2: Orchestration Models

**File**: `apps/backend/orchestration/models.py`

```python
"""Orchestration models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20

@dataclass
class Task:
    """Unit of work for an agent."""
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

@dataclass
class Pipeline:
    """Sequence of tasks with dependencies."""
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

@dataclass
class AgentMessage:
    """Message between agents."""
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
    """Resource limits for an agent."""
    agent_id: str
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    max_concurrent_tasks: int = 5
    max_tokens_per_minute: int = 100000
```

---

### Task 1.3: Orchestrator Class

**File**: `apps/backend/orchestration/orchestrator.py`

```python
"""Main orchestrator for multi-agent coordination."""
import asyncio
from typing import Dict, List, Optional, Any
from ..agents.registry import AgentRegistry
from .models import Task, Pipeline, TaskStatus, AgentMessage
from .task_queue import TaskQueue
from .message_bus import MessageBus
from .scheduler import Scheduler
from .resource_manager import ResourceManager

class Orchestrator:
    """Coordinates agent execution and communication."""
    
    def __init__(
        self,
        agent_registry: AgentRegistry,
        max_concurrent: int = 10
    ):
        self.registry = agent_registry
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
        await self.task_queue.enqueue(task)
        return task.id
    
    async def submit_pipeline(self, pipeline: Pipeline) -> str:
        """Submit pipeline for execution."""
        # Topologically sort tasks based on dependencies
        sorted_tasks = self._topological_sort(pipeline.tasks)
        
        for task in sorted_tasks:
            await self.task_queue.enqueue(task)
        
        return pipeline.id
    
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get current task status."""
        return await self.task_queue.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            return True
        return await self.task_queue.cancel(task_id)
    
    async def _task_processor(self) -> None:
        """Main task processing loop."""
        while self._is_running:
            if len(self._running_tasks) >= self.max_concurrent:
                await asyncio.sleep(0.1)
                continue
            
            task = await self.task_queue.dequeue()
            if task:
                asyncio_task = asyncio.create_task(
                    self._execute_task(task)
                )
                self._running_tasks[task.id] = asyncio_task
            else:
                await asyncio.sleep(0.1)
    
    async def _execute_task(self, task: Task) -> None:
        """Execute a single task."""
        try:
            # Check resource limits
            if not await self.resources.can_run(task.agent_id):
                task.status = TaskStatus.QUEUED
                await self.task_queue.enqueue(task)
                return
            
            # Get agent
            agent = self.registry.get(task.agent_id)
            if not agent:
                task.status = TaskStatus.FAILED
                task.error = f"Agent {task.agent_id} not found"
                return
            
            # Run with timeout
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow().isoformat()
            
            result = await asyncio.wait_for(
                agent.execute(task.action, task.params),
                timeout=task.timeout_seconds
            )
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow().isoformat()
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = "Task timed out"
        except Exception as e:
            task.error = str(e)
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                await self.task_queue.enqueue(task)
            else:
                task.status = TaskStatus.FAILED
        finally:
            self._running_tasks.pop(task.id, None)
    
    async def _message_processor(self) -> None:
        """Process inter-agent messages."""
        while self._is_running:
            message = await self.message_bus.receive()
            if message:
                agent = self.registry.get(message.to_agent)
                if agent:
                    await agent.handle_message(message)
            else:
                await asyncio.sleep(0.1)
    
    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by dependencies."""
        # Implementation of Kahn's algorithm
        pass
```

---

## Section 2: Task Queue

### Task 2.1: Priority Task Queue

**File**: `apps/backend/orchestration/task_queue.py`

```python
"""Priority-based task queue."""
import asyncio
from heapq import heappush, heappop
from typing import Optional, Dict, List
from datetime import datetime
from .models import Task, TaskStatus, TaskPriority

class TaskQueue:
    """Async priority queue for tasks."""
    
    def __init__(self):
        self._heap: List[tuple] = []  # (priority, timestamp, task)
        self._tasks: Dict[str, Task] = {}  # id -> task
        self._lock = asyncio.Lock()
    
    async def enqueue(self, task: Task) -> None:
        """Add task to queue."""
        async with self._lock:
            # Higher priority = lower number in heap
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
                
                # Check dependencies satisfied
                if await self._deps_satisfied(task):
                    return task
                else:
                    # Re-enqueue if deps not met
                    heappush(self._heap, (-task.priority.value, datetime.utcnow().timestamp(), task_id))
            
            return None
    
    async def _deps_satisfied(self, task: Task) -> bool:
        """Check if all dependencies completed."""
        for dep_id in task.depends_on:
            dep_task = self._tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    async def cancel(self, task_id: str) -> bool:
        """Cancel queued task."""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.QUEUED:
            task.status = TaskStatus.CANCELLED
            return True
        return False
```

---

## Section 3: Message Bus

### Task 3.1: Inter-Agent Messaging

**File**: `apps/backend/orchestration/message_bus.py`

```python
"""Message bus for inter-agent communication."""
import asyncio
from typing import Optional, Dict, List, Callable, Awaitable
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
    
    async def receive(self, timeout: float = 0.1) -> Optional[AgentMessage]:
        """Receive next message."""
        try:
            return await asyncio.wait_for(
                self._queue.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
    
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
    
    async def reply(self, original: AgentMessage, payload: Dict) -> None:
        """Reply to a message."""
        reply = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=original.to_agent,
            to_agent=original.from_agent,
            message_type="reply",
            payload=payload,
            timestamp="",
            correlation_id=original.correlation_id,
            reply_to=original.id,
        )
        
        # Resolve pending future if exists
        if original.correlation_id and original.correlation_id in self._pending_replies:
            self._pending_replies[original.correlation_id].set_result(reply)
        else:
            await self.send(reply)
    
    def subscribe(self, message_type: str, handler: Callable) -> None:
        """Subscribe to message type."""
        self._subscriptions[message_type].append(handler)
```

---

## Section 4: Resource Manager

### Task 4.1: Resource Allocation

**File**: `apps/backend/orchestration/resource_manager.py`

```python
"""Resource management for agents."""
import asyncio
from typing import Dict, Optional
from collections import defaultdict
from .models import ResourceQuota

class ResourceManager:
    """Manages resource allocation and limits."""
    
    def __init__(self):
        self._quotas: Dict[str, ResourceQuota] = {}
        self._usage: Dict[str, Dict] = defaultdict(lambda: {
            "current_tasks": 0,
            "tokens_used": 0,
            "last_reset": None,
        })
        self._lock = asyncio.Lock()
    
    async def set_quota(self, quota: ResourceQuota) -> None:
        """Set resource quota for agent."""
        self._quotas[quota.agent_id] = quota
    
    async def can_run(self, agent_id: str) -> bool:
        """Check if agent can run another task."""
        quota = self._quotas.get(agent_id)
        if not quota:
            return True  # No quota = no limit
        
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
    
    async def record_tokens(self, agent_id: str, tokens: int) -> None:
        """Record token usage."""
        self._usage[agent_id]["tokens_used"] += tokens
    
    async def get_usage(self, agent_id: str) -> Dict:
        """Get current resource usage."""
        return dict(self._usage[agent_id])
```

---

## Validation Checklist

- [ ] Tasks execute in priority order
- [ ] Dependencies respected
- [ ] Parallel execution works
- [ ] Messages delivered between agents
- [ ] Request/reply pattern works
- [ ] Resource limits enforced
- [ ] Timeout handling works
- [ ] Retry logic correct
- [ ] Graceful shutdown
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 1 (Foundation - AgentRegistry)

**Enables**: Phase 5 (Memory), Phase 7 (Enterprise Agents)

---

## ADR References

- ADR-003: System Architecture Standards
- ADR-007: Testing Strategy

---

*Phase 4 Specification v1.0.0*
