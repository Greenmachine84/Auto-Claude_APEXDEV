# Phase 8: Analytics & Tools

> **Duration**: Week 15-16 | **Priority**: 🟡 MEDIUM
>
> **Status**: 📋 Specification Ready

---

## Outcome Expectations

### Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| Usage metrics collected | Events tracked | ✅ |
| Cost tracking works | Per-provider/model | ✅ |
| Dashboard API functional | Metrics endpoints | ✅ |
| Tool registry works | CRUD operations | ✅ |
| Tool execution works | Agent tool calls | ✅ |

### Deliverables

1. `apps/backend/analytics/metrics/collector.py`
2. `apps/backend/analytics/metrics/aggregator.py`
3. `apps/backend/analytics/cost/cost_tracker.py`
4. `apps/backend/analytics/dashboard/api.py`
5. `apps/backend/tools/registry/tool_registry.py`
6. `apps/backend/tools/executor/tool_executor.py`
7. `apps/backend/tools/builtin/` (file, web, git tools)
8. Unit tests for all modules

---

## Section 1: Analytics Architecture

### Task 1.1: Directory Structure

```
apps/backend/analytics/
├── __init__.py
├── models.py
├── metrics/
│   ├── __init__.py
│   ├── collector.py
│   └── aggregator.py
├── cost/
│   ├── __init__.py
│   ├── cost_tracker.py
│   └── pricing.py
└── dashboard/
    ├── __init__.py
    └── api.py

apps/backend/tools/
├── __init__.py
├── models.py
├── registry/
│   ├── __init__.py
│   └── tool_registry.py
├── executor/
│   ├── __init__.py
│   └── tool_executor.py
└── builtin/
    ├── __init__.py
    ├── file_tools.py
    ├── web_tools.py
    └── git_tools.py
```

---

### Task 1.2: Analytics Models

**File**: `apps/backend/analytics/models.py`

```python
"""Analytics models."""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MetricType(Enum):
    COUNTER = "counter"      # Cumulative count
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution
    TIMER = "timer"          # Duration

class EventType(Enum):
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    TOOL_CALLED = "tool_called"
    MEMORY_ACCESS = "memory_access"
    USER_LOGIN = "user_login"

@dataclass
class MetricEvent:
    """Single metric event."""
    id: str
    event_type: EventType
    timestamp: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    provider: Optional[str] = None  # LLM provider
    model: Optional[str] = None     # LLM model
    value: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenUsage:
    """Token usage for a request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    @property
    def cost(self) -> float:
        """Calculate cost (set by pricing module)."""
        return 0.0  # Calculated by cost tracker

@dataclass
class UsageMetrics:
    """Aggregated usage metrics."""
    period_start: str
    period_end: str
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    requests_by_provider: Dict[str, int] = field(default_factory=dict)
    tokens_by_provider: Dict[str, int] = field(default_factory=dict)
    cost_by_provider: Dict[str, float] = field(default_factory=dict)
    requests_by_agent: Dict[str, int] = field(default_factory=dict)
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0

@dataclass
class CostRecord:
    """Cost record for billing."""
    id: str
    user_id: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: str
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
```

---

## Section 2: Metrics Collection

### Task 2.1: Metrics Collector

**File**: `apps/backend/analytics/metrics/collector.py`

```python
"""Metrics collection."""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import uuid
from ..models import MetricEvent, EventType

class MetricsCollector:
    """Collects and stores metrics events."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    agent_id TEXT,
                    provider TEXT,
                    model TEXT,
                    value REAL,
                    metadata TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user ON events(user_id)")
    
    async def record(self, event: MetricEvent) -> str:
        """Record a metric event."""
        if not event.id:
            event.id = str(uuid.uuid4())
        if not event.timestamp:
            event.timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO events
                (id, event_type, timestamp, user_id, agent_id, 
                 provider, model, value, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.event_type.value,
                event.timestamp,
                event.user_id,
                event.agent_id,
                event.provider,
                event.model,
                event.value,
                json.dumps(event.metadata),
            ))
        
        return event.id
    
    async def record_llm_request(
        self,
        user_id: str,
        agent_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        success: bool = True
    ) -> str:
        """Record an LLM request."""
        event = MetricEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.LLM_RESPONSE if success else EventType.AGENT_FAILED,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            agent_id=agent_id,
            provider=provider,
            model=model,
            value=prompt_tokens + completion_tokens,
            metadata={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency_ms": latency_ms,
                "success": success,
            },
        )
        return await self.record(event)
    
    async def query(
        self,
        event_type: Optional[EventType] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[MetricEvent]:
        """Query events."""
        conditions = ["1=1"]
        params = []
        
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type.value)
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.isoformat())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.isoformat())
        
        params.append(limit)
        
        sql = f"""
            SELECT * FROM events
            WHERE {' AND '.join(conditions)}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            return [
                MetricEvent(
                    id=row["id"],
                    event_type=EventType(row["event_type"]),
                    timestamp=row["timestamp"],
                    user_id=row["user_id"],
                    agent_id=row["agent_id"],
                    provider=row["provider"],
                    model=row["model"],
                    value=row["value"],
                    metadata=json.loads(row["metadata"] or "{}"),
                )
                for row in cursor.fetchall()
            ]
```

---

### Task 2.2: Cost Tracker

**File**: `apps/backend/analytics/cost/cost_tracker.py`

```python
"""Cost tracking for LLM usage."""
import sqlite3
import json
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime, timedelta
import uuid
from ..models import CostRecord, UsageMetrics

class CostTracker:
    """Tracks LLM costs per user/provider."""
    
    # Pricing per 1M tokens (approximate)
    PRICING = {
        # Provider: {model_pattern: (input_per_1m, output_per_1m)}
        "openai": {
            "gpt-4o": (5.0, 15.0),
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4-turbo": (10.0, 30.0),
        },
        "anthropic": {
            "claude-3-5-sonnet": (3.0, 15.0),
            "claude-3-opus": (15.0, 75.0),
            "claude-3-haiku": (0.25, 1.25),
        },
        "gemini": {
            "gemini-1.5-pro": (3.5, 10.5),
            "gemini-1.5-flash": (0.35, 1.05),
        },
        "openrouter": {
            "default": (1.0, 2.0),  # Varies by model
        },
        "ollama": {
            "default": (0.0, 0.0),  # Local, no cost
        },
        "lmstudio": {
            "default": (0.0, 0.0),  # Local, no cost
        },
        "copilot": {
            "default": (0.0, 0.0),  # Included in subscription
        },
        "azure": {
            "default": (5.0, 15.0),  # Varies by deployment
        },
    }
    
    def __init__(self, db_path: str = "costs.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS costs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    cost_usd REAL,
                    timestamp TEXT,
                    agent_id TEXT,
                    task_id TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user ON costs(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON costs(timestamp)")
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost for token usage."""
        provider_pricing = self.PRICING.get(provider.lower(), {})
        
        # Find matching model or use default
        pricing = None
        for pattern, prices in provider_pricing.items():
            if pattern in model.lower() or pattern == "default":
                pricing = prices
                break
        
        if not pricing:
            pricing = (1.0, 2.0)  # Default fallback
        
        input_cost = (prompt_tokens / 1_000_000) * pricing[0]
        output_cost = (completion_tokens / 1_000_000) * pricing[1]
        
        return round(input_cost + output_cost, 6)
    
    async def record(
        self,
        user_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> CostRecord:
        """Record a cost entry."""
        cost = self.calculate_cost(provider, model, prompt_tokens, completion_tokens)
        
        record = CostRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            timestamp=datetime.utcnow().isoformat(),
            agent_id=agent_id,
            task_id=task_id,
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO costs
                (id, user_id, provider, model, prompt_tokens, 
                 completion_tokens, cost_usd, timestamp, agent_id, task_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.user_id,
                record.provider,
                record.model,
                record.prompt_tokens,
                record.completion_tokens,
                record.cost_usd,
                record.timestamp,
                record.agent_id,
                record.task_id,
            ))
        
        return record
    
    async def get_user_usage(
        self,
        user_id: str,
        days: int = 30
    ) -> UsageMetrics:
        """Get user's usage metrics."""
        start = (datetime.utcnow() - timedelta(days=days)).isoformat()
        end = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Aggregate by provider
            cursor = conn.execute("""
                SELECT 
                    provider,
                    COUNT(*) as requests,
                    SUM(prompt_tokens + completion_tokens) as tokens,
                    SUM(cost_usd) as cost
                FROM costs
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY provider
            """, (user_id, start))
            
            rows = cursor.fetchall()
            
            metrics = UsageMetrics(
                period_start=start,
                period_end=end,
            )
            
            for row in rows:
                metrics.total_requests += row["requests"]
                metrics.total_tokens += row["tokens"] or 0
                metrics.total_cost += row["cost"] or 0
                metrics.requests_by_provider[row["provider"]] = row["requests"]
                metrics.tokens_by_provider[row["provider"]] = row["tokens"] or 0
                metrics.cost_by_provider[row["provider"]] = row["cost"] or 0
            
            return metrics
```

---

## Section 3: Tool System

### Task 3.1: Tool Models

**File**: `apps/backend/tools/models.py`

```python
"""Tool models."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Awaitable
from enum import Enum

class ToolCategory(Enum):
    FILE = "file"
    WEB = "web"
    GIT = "git"
    DATABASE = "database"
    CUSTOM = "custom"

@dataclass
class ToolParameter:
    """Tool parameter definition."""
    name: str
    type: str  # string, number, boolean, array, object
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None

@dataclass
class Tool:
    """Tool definition."""
    id: str
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: str = "string"
    handler: Optional[Callable[..., Awaitable[Any]]] = None
    requires_permission: Optional[str] = None
    is_dangerous: bool = False
    max_execution_time: int = 30

@dataclass
class ToolCall:
    """Tool invocation."""
    id: str
    tool_id: str
    parameters: Dict[str, Any]
    agent_id: str
    timestamp: str = ""

@dataclass
class ToolResult:
    """Tool execution result."""
    call_id: str
    tool_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: int = 0
```

---

### Task 3.2: Tool Registry

**File**: `apps/backend/tools/registry/tool_registry.py`

```python
"""Tool registry."""
from typing import Dict, List, Optional, Callable, Awaitable, Any
from ..models import Tool, ToolCategory, ToolParameter

class ToolRegistry:
    """Central registry for all tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.id] = tool
    
    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool."""
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False
    
    def get(self, tool_id: str) -> Optional[Tool]:
        """Get tool by ID."""
        return self._tools.get(tool_id)
    
    def list_all(self) -> List[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def list_by_category(self, category: ToolCategory) -> List[Tool]:
        """List tools by category."""
        return [t for t in self._tools.values() if t.category == category]
    
    def to_openai_format(self, tool_ids: Optional[List[str]] = None) -> List[Dict]:
        """Export tools in OpenAI function calling format."""
        tools = [self._tools[tid] for tid in tool_ids] if tool_ids else self._tools.values()
        
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.id,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            p.name: {
                                "type": p.type,
                                "description": p.description,
                                **({
                                    "enum": p.enum
                                } if p.enum else {}),
                            }
                            for p in tool.parameters
                        },
                        "required": [p.name for p in tool.parameters if p.required],
                    },
                },
            }
            for tool in tools
        ]
    
    def decorator(
        self,
        tool_id: str,
        description: str,
        category: ToolCategory = ToolCategory.CUSTOM,
        **kwargs
    ) -> Callable:
        """Decorator to register a function as a tool."""
        def wrapper(func: Callable[..., Awaitable[Any]]) -> Callable:
            tool = Tool(
                id=tool_id,
                name=func.__name__,
                description=description,
                category=category,
                handler=func,
                **kwargs,
            )
            self.register(tool)
            return func
        return wrapper
```

---

### Task 3.3: Tool Executor

**File**: `apps/backend/tools/executor/tool_executor.py`

```python
"""Tool execution engine."""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from ..models import ToolCall, ToolResult
from ..registry.tool_registry import ToolRegistry

class ToolExecutor:
    """Executes tool calls safely."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    async def execute(self, call: ToolCall) -> ToolResult:
        """Execute a tool call."""
        start_time = datetime.utcnow()
        
        tool = self.registry.get(call.tool_id)
        if not tool:
            return ToolResult(
                call_id=call.id,
                tool_id=call.tool_id,
                success=False,
                error=f"Tool {call.tool_id} not found",
            )
        
        if not tool.handler:
            return ToolResult(
                call_id=call.id,
                tool_id=call.tool_id,
                success=False,
                error=f"Tool {call.tool_id} has no handler",
            )
        
        try:
            result = await asyncio.wait_for(
                tool.handler(**call.parameters),
                timeout=tool.max_execution_time
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ToolResult(
                call_id=call.id,
                tool_id=call.tool_id,
                success=True,
                result=result,
                execution_time_ms=int(elapsed),
            )
            
        except asyncio.TimeoutError:
            return ToolResult(
                call_id=call.id,
                tool_id=call.tool_id,
                success=False,
                error=f"Tool execution timed out after {tool.max_execution_time}s",
            )
        except Exception as e:
            return ToolResult(
                call_id=call.id,
                tool_id=call.tool_id,
                success=False,
                error=str(e),
            )
```

---

### Task 3.4: Built-in Tools

**File**: `apps/backend/tools/builtin/file_tools.py`

```python
"""File operation tools."""
from pathlib import Path
from typing import Optional, List
from ..registry.tool_registry import ToolRegistry
from ..models import ToolCategory, ToolParameter

def register_file_tools(registry: ToolRegistry) -> None:
    """Register file operation tools."""
    
    @registry.decorator(
        tool_id="read_file",
        description="Read contents of a file",
        category=ToolCategory.FILE,
    )
    async def read_file(path: str, encoding: str = "utf-8") -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return p.read_text(encoding=encoding)
    
    @registry.decorator(
        tool_id="write_file",
        description="Write content to a file",
        category=ToolCategory.FILE,
        is_dangerous=True,
    )
    async def write_file(
        path: str, 
        content: str, 
        encoding: str = "utf-8"
    ) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding=encoding)
        return f"Written {len(content)} bytes to {path}"
    
    @registry.decorator(
        tool_id="list_directory",
        description="List files in a directory",
        category=ToolCategory.FILE,
    )
    async def list_directory(
        path: str, 
        pattern: str = "*"
    ) -> List[str]:
        p = Path(path)
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        return [str(f.relative_to(p)) for f in p.glob(pattern)]
```

---

## Validation Checklist

- [ ] Metrics events recorded correctly
- [ ] Cost calculation accurate
- [ ] Usage aggregation works
- [ ] Tool registration works
- [ ] Tool execution with timeout works
- [ ] Built-in tools functional
- [ ] OpenAI format export works
- [ ] Unit tests pass (100%)

---

## Dependencies

**Requires**: Phase 1, 2, 4

**Enables**: Phase 9 (Governance), Phase 10 (Testing)

---

## ADR References

- ADR-006: Integration Points Definition

---

*Phase 8 Specification v1.0.0*
