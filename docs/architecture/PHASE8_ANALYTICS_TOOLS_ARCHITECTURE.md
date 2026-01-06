# Phase 8: Analytics & Tools Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 8 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026
> Reference: `docs/specs/phase-08-analytics-tools.md`

---

## Overview

Phase 8 implements comprehensive analytics for usage tracking, cost calculation, and dashboard visualization, plus an extensible tools system. All analytics are **LLM-Agnostic** with per-provider usage and cost tracking for all 8 supported providers.

---

## Quality Standards

| Standard | Target | Verification |
|----------|--------|-------------|
| Real-time Visibility | <5s event-to-dashboard | Integration test |
| Financial-grade Accuracy | <0.1% cost error | Financial audit |
| Tool Execution | <100ms P99 | Load testing |
| Data Retention | 90 days | Audit trail |

---

## LLM-Agnostic Analytics Design

> **CRITICAL**: Track usage and costs for ALL 8 LLM providers equally.
> Each provider has distinct pricing models.
> NO default provider - all tracked equally.

### Provider Pricing Model
| Provider | Type | Pricing |
|----------|------|--------|
| copilot | Subscription | Included |
| openrouter | Pay-per-use | Variable |
| ollama | Local | Free |
| lmstudio | Local | Free |
| gemini | Pay-per-use | Per-model |
| openai | Pay-per-use | Per-model |
| anthropic | Pay-per-use | Per-model |
| azure | Pay-per-use | Per-model |

---

## Directory Structure

```
apps/
└── backend/
    ├── analytics/
    │   ├── __init__.py                    # Analytics module exports
    │   ├── models.py                      # Analytics data models
    │   ├── config.py                      # Analytics configuration
    │   │
    │   ├── metrics/
    │   │   ├── __init__.py                # Metrics exports
    │   │   ├── collector.py               # Event collection
    │   │   ├── aggregator.py              # Metric aggregation
    │   │   ├── time_series.py             # Time series data
    │   │   └── storage.py                 # Metrics persistence
    │   │
    │   ├── cost/
    │   │   ├── __init__.py                # Cost tracking exports
    │   │   ├── cost_tracker.py            # Multi-provider cost tracking
    │   │   ├── pricing.py                 # Provider pricing models
    │   │   ├── budget_manager.py          # Budget limits and alerts
    │   │   └── cost_report.py             # Cost reporting
    │   │
    │   ├── dashboard/
    │   │   ├── __init__.py                # Dashboard exports
    │   │   ├── api.py                     # Dashboard API endpoints
    │   │   ├── data_builder.py            # Dashboard data construction
    │   │   ├── chart_data.py              # Chart-ready data formats
    │   │   └── export.py                  # CSV/JSON export
    │   │
    │   └── provider_analytics/
    │       ├── __init__.py                # Provider analytics exports
    │       ├── provider_comparison.py     # Cross-provider comparison
    │       ├── provider_metrics.py        # Per-provider metrics
    │       └── usage_optimizer.py         # Cost optimization suggestions
    │
    └── tools/
        ├── __init__.py                    # Tools module exports
        ├── models.py                      # Tool data models
        ├── config.py                      # Tools configuration
        │
        ├── registry/
        │   ├── __init__.py                # Registry exports
        │   ├── tool_registry.py           # Central tool registry
        │   ├── tool_loader.py             # Dynamic tool loading
        │   ├── tool_validator.py          # Tool definition validation
        │   └── tool_discovery.py          # Auto-discovery of tools
        │
        ├── executor/
        │   ├── __init__.py                # Executor exports
        │   ├── tool_executor.py           # Sandboxed tool execution
        │   ├── sandbox.py                 # Execution sandbox
        │   ├── timeout_handler.py         # Execution timeout handling
        │   └── result_handler.py          # Execution result processing
        │
        └── builtin/
            ├── __init__.py                # Built-in tools exports
            ├── file_tools.py              # File operations
            ├── web_tools.py               # Web/HTTP operations
            ├── git_tools.py               # Git operations
            ├── search_tools.py            # Code/text search
            └── shell_tools.py             # Safe shell execution
```

---

## File Specifications

### 1. Analytics Core (`analytics/`)

#### `models.py`
**Purpose**: Analytics data models
**Key Components**:
```python
class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class EventType(Enum):
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    TOOL_CALLED = "tool_called"
    PROVIDER_SWITCH = "provider_switch"


@dataclass
class MetricEvent:
    """Single metric event with provider tracking."""
    id: str
    event_type: EventType
    timestamp: str
    user_id: Optional[str]
    agent_id: Optional[str]
    provider: Optional[str]  # One of 8 LLM providers
    model: Optional[str]
    value: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostRecord:
    """Cost record for billing with provider attribution."""
    id: str
    user_id: str
    provider: str  # copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: str
    agent_id: Optional[str] = None
```

---

### 2. Metrics Module (`analytics/metrics/`)

#### `collector.py`
**Purpose**: Collect metrics events from all system components
**Key Components**:
```python
class MetricsCollector:
    """Collects metrics from all sources."""
    
    async def record_event(self, event: MetricEvent) -> None
    async def record_llm_request(self, provider: str, model: str, tokens: int) -> None
    async def record_agent_execution(self, agent_id: str, duration_ms: float) -> None
    async def record_tool_call(self, tool_name: str, success: bool) -> None
    
    def increment_counter(self, name: str, value: float = 1.0) -> None
    def set_gauge(self, name: str, value: float) -> None
    def record_histogram(self, name: str, value: float) -> None
```

#### `aggregator.py`
**Purpose**: Aggregate raw metrics into summaries
**Key Components**:
```python
class MetricsAggregator:
    async def aggregate_by_provider(self, user_id: str, period: str) -> Dict[str, ProviderMetrics]
    async def aggregate_by_agent(self, user_id: str, period: str) -> Dict[str, AgentMetrics]
    async def aggregate_by_time(self, user_id: str, granularity: str) -> List[TimeSeriesPoint]
    async def get_summary(self, user_id: str) -> MetricsSummary
```

#### `time_series.py`
**Purpose**: Time series data management
**Key Components**:
- Time-bucketed storage
- Downsampling for historical data
- Rolling averages

#### `storage.py`
**Purpose**: Metrics persistence
**Key Components**:
- SQLite storage backend
- Retention policy
- Efficient querying

---

### 3. Cost Module (`analytics/cost/`)

#### `cost_tracker.py`
**Purpose**: Multi-provider cost tracking
**Key Components**:
```python
class CostTracker:
    """
    Tracks LLM costs across all 8 providers.
    
    Supports:
    - copilot (subscription-based)
    - openrouter (pay-per-use)
    - ollama (free, local)
    - lmstudio (free, local)
    - gemini (Google pricing)
    - openai (OpenAI pricing)
    - anthropic (Anthropic pricing)
    - azure (Azure pricing)
    """
    
    SUPPORTED_PROVIDERS = [
        "copilot", "openrouter", "ollama", "lmstudio",
        "gemini", "openai", "anthropic", "azure"
    ]
    
    def calculate_cost(self, provider: str, model: str, 
                       prompt_tokens: int, completion_tokens: int) -> float
    async def record_usage(self, user_id: str, provider: str, model: str,
                          prompt_tokens: int, completion_tokens: int) -> CostRecord
    async def get_user_total(self, user_id: str, period: str) -> float
    async def get_provider_breakdown(self, user_id: str, period: str) -> Dict[str, float]
```

#### `pricing.py`
**Purpose**: Provider pricing models
**Key Components**:
```python
# Provider pricing per 1M tokens (input, output)
PROVIDER_PRICING = {
    "copilot": {"default": (0.0, 0.0)},  # Subscription
    "openrouter": {
        "anthropic/claude-3-opus": (15.0, 75.0),
        "openai/gpt-4": (30.0, 60.0),
        "meta-llama/llama-3-70b": (0.9, 0.9),
    },
    "ollama": {"default": (0.0, 0.0)},  # Local, free
    "lmstudio": {"default": (0.0, 0.0)},  # Local, free
    "gemini": {
        "gemini-1.5-pro": (3.5, 10.5),
        "gemini-1.5-flash": (0.35, 1.05),
    },
    "openai": {
        "gpt-4o": (5.0, 15.0),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.0, 30.0),
    },
    "anthropic": {
        "claude-sonnet-4-20250514": (3.0, 15.0),
        "claude-3-opus": (15.0, 75.0),
    },
    "azure": {
        "gpt-4o": (5.0, 15.0),
        "gpt-4": (30.0, 60.0),
    },
}
```

#### `budget_manager.py`
**Purpose**: Budget limits and alerts
**Key Components**:
```python
class BudgetManager:
    def set_budget(self, user_id: str, provider: str, monthly_limit: float) -> None
    def check_budget(self, user_id: str, provider: str) -> BudgetStatus
    def get_remaining(self, user_id: str, provider: str) -> float
    def trigger_alert(self, user_id: str, provider: str, threshold: float) -> None
```

#### `cost_report.py`
**Purpose**: Generate cost reports
**Key Components**:
- Daily/weekly/monthly reports
- Provider breakdown
- Agent attribution
- Trend analysis

---

### 4. Dashboard Module (`analytics/dashboard/`)

#### `api.py`
**Purpose**: Dashboard API endpoints
**Key Components**:
```python
router = APIRouter(prefix="/api/analytics")

@router.get("/dashboard")
async def get_dashboard(days: int = 30, user_id: str = Depends(get_current_user))

@router.get("/providers")
async def get_provider_comparison(user_id: str = Depends(get_current_user))

@router.get("/costs")
async def get_costs(period: str = "month", user_id: str = Depends(get_current_user))

@router.get("/export")
async def export_data(format: str = "csv", user_id: str = Depends(get_current_user))
```

#### `data_builder.py`
**Purpose**: Construct dashboard data
**Key Components**:
```python
@dataclass
class DashboardData:
    period_start: str
    period_end: str
    total_requests: int
    total_tokens: int
    total_cost: float
    by_provider: Dict[str, ProviderUsageMetrics]
    by_agent: Dict[str, Dict]
    hourly_requests: List[Dict]
    hourly_cost: List[Dict]
    recommendations: List[str]
```

#### `chart_data.py`
**Purpose**: Format data for charts
**Key Components**:
- Line chart data (time series)
- Bar chart data (comparisons)
- Pie chart data (distributions)

#### `export.py`
**Purpose**: Export functionality
**Key Components**:
- CSV export
- JSON export
- PDF reports

---

### 5. Provider Analytics (`analytics/provider_analytics/`)

#### `provider_comparison.py`
**Purpose**: Cross-provider comparison
**Key Components**:
```python
class ProviderComparison:
    async def compare_cost(self, user_id: str, period: str) -> Dict[str, float]
    async def compare_latency(self, user_id: str, period: str) -> Dict[str, float]
    async def compare_reliability(self, user_id: str, period: str) -> Dict[str, float]
    async def get_recommendations(self, user_id: str) -> List[Recommendation]
```

#### `usage_optimizer.py`
**Purpose**: Cost optimization suggestions
**Key Components**:
```python
class UsageOptimizer:
    def analyze_usage(self, user_id: str) -> UsageAnalysis
    def suggest_model_switch(self, current: str, task_type: str) -> str
    def estimate_savings(self, user_id: str, suggested_changes: List) -> float
```

---

### 6. Tools Core (`tools/`)

#### `models.py`
**Purpose**: Tool data models
**Key Components**:
```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, ParameterDef]
    returns: ReturnType
    permissions: List[str]
    timeout_ms: int = 30000


@dataclass
class ToolResult:
    success: bool
    result: Any
    error: Optional[str]
    execution_time_ms: float
```

---

### 7. Tool Registry (`tools/registry/`)

#### `tool_registry.py`
**Purpose**: Central tool registration and lookup
**Key Components**:
```python
class ToolRegistry:
    def register(self, tool: ToolDefinition) -> None
    def unregister(self, tool_name: str) -> None
    def get(self, tool_name: str) -> ToolDefinition
    def list_all(self) -> List[ToolDefinition]
    def list_by_permission(self, permission: str) -> List[ToolDefinition]
```

#### `tool_loader.py`
**Purpose**: Dynamic tool loading
**Key Components**:
- Load from Python modules
- Load from JSON/YAML definitions
- Hot-reload support

#### `tool_discovery.py`
**Purpose**: Auto-discover tools
**Key Components**:
- Scan directories for tool definitions
- Plugin architecture

---

### 8. Tool Executor (`tools/executor/`)

#### `tool_executor.py`
**Purpose**: Execute tools safely
**Key Components**:
```python
class ToolExecutor:
    async def execute(self, tool_name: str, params: Dict) -> ToolResult
    async def execute_with_timeout(self, tool_name: str, params: Dict, timeout_ms: int) -> ToolResult
    def validate_params(self, tool_name: str, params: Dict) -> bool
```

#### `sandbox.py`
**Purpose**: Sandboxed execution environment
**Key Components**:
- Resource limits (CPU, memory)
- File system isolation
- Network restrictions

---

### 9. Built-in Tools (`tools/builtin/`)

#### `file_tools.py`
**Purpose**: File operations
**Tools**: `read_file`, `write_file`, `list_directory`, `create_directory`, `delete_file`

#### `web_tools.py`
**Purpose**: Web/HTTP operations
**Tools**: `http_get`, `http_post`, `fetch_page`

#### `git_tools.py`
**Purpose**: Git operations
**Tools**: `git_clone`, `git_commit`, `git_push`, `git_branch`, `git_diff`

#### `search_tools.py`
**Purpose**: Search operations
**Tools**: `grep_search`, `find_files`, `semantic_search`

#### `shell_tools.py`
**Purpose**: Safe shell execution
**Tools**: `run_command` (with allowlist validation)

---

## Integration Points

### With LLM Layer (Phase 2)
- Every LLM call recorded by collector
- Cost calculated per request

### With Agents (Phase 7)
- Agent execution metrics
- Per-agent cost attribution

### With Governance (Phase 9)
- Usage data feeds policy decisions
- Budget enforcement

### With UI (Frontend)
- Dashboard API consumed by React components
- Real-time updates via WebSocket

---

## Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Event ingestion | >10K events/s | <5K events/s |
| Cost calculation | <1ms | >5ms |
| Dashboard API | <100ms P99 | >500ms |
| Tool execution | <100ms P99 | >500ms |
| Aggregation query | <500ms | >2s |
| Export generation | <10s for 1M rows | >30s |

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `analytics/` (core) | 3 | Analytics core |
| `analytics/metrics/` | 5 | Metrics collection |
| `analytics/cost/` | 5 | Cost tracking |
| `analytics/dashboard/` | 5 | Dashboard API |
| `analytics/provider_analytics/` | 4 | Provider comparison |
| `tools/` (core) | 3 | Tools core |
| `tools/registry/` | 5 | Tool registry |
| `tools/executor/` | 5 | Tool execution |
| `tools/builtin/` | 6 | Built-in tools |
| **Total** | **41** | Phase 8 files |

---

## Next Steps

→ Phase 9: Governance Architecture

---

*Phase 8 Architecture complete. 41 files specified for analytics and tools.*
