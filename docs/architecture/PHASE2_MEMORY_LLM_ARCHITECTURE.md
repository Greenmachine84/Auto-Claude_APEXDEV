# Phase 2: Memory System & LLM Integration Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 2 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026

---

## Overview

Phase 2 establishes the memory subsystem and LLM integration layer, incorporating DEVAPEX's episodic memory, H-MEM tiered architecture, and multi-provider LLM support.

---

## Directory Structure

```
apps/
└── backend/
    ├── memory/
    │   ├── __init__.py                    # Memory system exports
    │   │
    │   ├── core/
    │   │   ├── __init__.py                # Core memory exports
    │   │   ├── memory_manager.py          # Central memory coordinator
    │   │   ├── memory_config.py           # Memory configuration
    │   │   └── memory_bridge.py           # Cross-system sync interface
    │   │
    │   ├── episodic/
    │   │   ├── __init__.py                # Episodic memory exports
    │   │   ├── episode_store.py           # SQLite-based episode storage
    │   │   ├── episode_record.py          # Episode data model
    │   │   ├── episode_query.py           # Query builder for episodes
    │   │   ├── reflexion_pattern.py       # Lessons learned storage
    │   │   └── retention_policy.py        # Automatic cleanup policies
    │   │
    │   ├── semantic/
    │   │   ├── __init__.py                # Semantic memory exports
    │   │   ├── semantic_store.py          # Vector-based semantic storage
    │   │   ├── semantic_search.py         # Embedding similarity search
    │   │   ├── semantic_index.py          # Index management
    │   │   └── chunk_processor.py         # Text chunking for embeddings
    │   │
    │   ├── hmem/
    │   │   ├── __init__.py                # H-MEM tier exports
    │   │   ├── tier_manager.py            # L1/L2/L3 tier coordination
    │   │   ├── l1_cache.py                # In-memory hot cache
    │   │   ├── l2_session.py              # Session-scoped memory
    │   │   ├── l3_persistent.py           # Long-term persistent storage
    │   │   └── tier_promotion.py          # Auto-promotion between tiers
    │   │
    │   ├── context/
    │   │   ├── __init__.py                # Context management exports
    │   │   ├── context_builder.py         # Build context for LLM calls
    │   │   ├── context_window.py          # Token-aware windowing
    │   │   ├── context_compressor.py      # Compress context to fit limits
    │   │   └── relevance_scorer.py        # Score context relevance
    │   │
    │   └── types/
    │       ├── __init__.py                # Type exports
    │       ├── memory_types.py            # Memory type enums
    │       ├── episode_types.py           # Episode-related types
    │       └── query_types.py             # Query parameter types
    │
    └── llm/
        ├── __init__.py                    # LLM system exports
        │
        ├── core/
        │   ├── __init__.py                # Core LLM exports
        │   ├── llm_client.py              # Abstract LLM client interface
        │   ├── llm_config.py              # LLM configuration
        │   ├── llm_router.py              # Route requests to providers
        │   ├── model_selector.py          # Dynamic model selection
        │   └── cost_tracker.py            # Token usage and cost tracking
        │
        ├── providers/
        │   ├── __init__.py                # Provider exports
        │   ├── base_provider.py           # Abstract provider base
        │   ├── anthropic_provider.py      # Claude (Opus, Sonnet, Haiku)
        │   ├── openai_provider.py         # GPT-4, GPT-4o, GPT-4o-mini
        │   ├── azure_provider.py          # Azure OpenAI Service
        │   ├── ollama_provider.py         # Local LLMs (Llama, Mistral)
        │   ├── google_provider.py         # Gemini models
        │   ├── groq_provider.py           # Groq inference
        │   └── openrouter_provider.py     # OpenRouter gateway
        │
        ├── embeddings/
        │   ├── __init__.py                # Embedding exports
        │   ├── base_embedder.py           # Abstract embedder interface
        │   ├── openai_embedder.py         # OpenAI text-embedding-3
        │   ├── ollama_embedder.py         # Local Ollama embeddings
        │   ├── voyage_embedder.py         # Voyage AI embeddings
        │   ├── google_embedder.py         # Google embeddings
        │   └── azure_embedder.py          # Azure OpenAI embeddings
        │
        ├── prompts/
        │   ├── __init__.py                # Prompt exports
        │   ├── prompt_template.py         # Template engine
        │   ├── prompt_registry.py         # Named prompt storage
        │   ├── system_prompts.py          # Agent system prompts
        │   └── prompt_composer.py         # Multi-part prompt builder
        │
        ├── streaming/
        │   ├── __init__.py                # Streaming exports
        │   ├── stream_handler.py          # Handle streaming responses
        │   ├── stream_buffer.py           # Buffer partial responses
        │   └── stream_parser.py           # Parse streaming chunks
        │
        ├── tools/
        │   ├── __init__.py                # Tool calling exports
        │   ├── tool_definition.py         # Tool schema definitions
        │   ├── tool_executor.py           # Execute tool calls
        │   ├── tool_result.py             # Tool result handling
        │   └── tool_validator.py          # Validate tool parameters
        │
        └── types/
            ├── __init__.py                # Type exports
            ├── llm_types.py               # LLM-related types
            ├── message_types.py           # Message format types
            ├── response_types.py          # Response structure types
            └── token_types.py             # Token counting types
```

---

## File Specifications

### 1. Memory Core Module (`memory/core/`)

#### `memory_manager.py`
**Purpose**: Central coordinator for all memory operations
**Key Components**:
- `MemoryManager` class (singleton)
- Coordinate episodic, semantic, and H-MEM tiers
- Unified API for store/retrieve operations
- Background maintenance tasks

**Key Methods**:
```python
class MemoryManager:
    def store_episode(self, episode: EpisodeRecord) -> str
    def search_episodes(self, query: MemoryQuery) -> List[EpisodeRecord]
    def store_embedding(self, text: str, metadata: dict) -> str
    def semantic_search(self, query: str, limit: int) -> List[SearchResult]
    def get_context(self, task_id: str) -> Context
```

#### `memory_config.py`
**Purpose**: Configuration for memory subsystem
**Key Components**:
- Database paths
- Retention policies
- Cache sizes
- Embedding dimensions

#### `memory_bridge.py`
**Purpose**: Cross-system memory synchronization
**Key Components**:
- Sync with external memory systems (Graphiti)
- Import/export functionality
- Conflict resolution

---

### 2. Episodic Memory Module (`memory/episodic/`)

#### `episode_store.py`
**Purpose**: SQLite-based persistent episode storage
**Key Components**:
- SQLite connection management
- CRUD operations for episodes
- Full-text search (FTS5)
- Transaction support

**Schema**:
```sql
CREATE TABLE episodes (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    task_id TEXT,
    input_text TEXT,
    output_text TEXT,
    success BOOLEAN,
    tools_used TEXT,  -- JSON array
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT  -- JSON object
);

CREATE VIRTUAL TABLE episodes_fts USING fts5(
    input_text, output_text, content=episodes
);
```

#### `episode_record.py`
**Purpose**: Episode data model
**Key Components**:
```python
@dataclass
class EpisodeRecord:
    id: str
    agent_id: str
    task_id: Optional[str]
    input_text: str
    output_text: str
    success: bool
    tools_used: List[str]
    duration_ms: int
    created_at: datetime
    metadata: Dict[str, Any]
```

#### `episode_query.py`
**Purpose**: Fluent query builder for episodes
**Key Methods**:
```python
class EpisodeQuery:
    def by_agent(self, agent_id: str) -> EpisodeQuery
    def by_task(self, task_id: str) -> EpisodeQuery
    def search_text(self, query: str) -> EpisodeQuery
    def since(self, timestamp: datetime) -> EpisodeQuery
    def limit(self, n: int) -> EpisodeQuery
    def execute(self) -> List[EpisodeRecord]
```

#### `reflexion_pattern.py`
**Purpose**: Store and retrieve lessons learned
**Key Components**:
- Pattern extraction from failed episodes
- Success pattern recognition
- Lesson application to new tasks

#### `retention_policy.py`
**Purpose**: Automatic cleanup based on policies
**Policies**:
- Time-based (delete after N days)
- Count-based (keep last N per agent)
- Importance-based (preserve high-value episodes)

---

### 3. Semantic Memory Module (`memory/semantic/`)

#### `semantic_store.py`
**Purpose**: Vector-based semantic storage
**Key Components**:
- Vector database integration
- Embedding storage and retrieval
- Metadata filtering

#### `semantic_search.py`
**Purpose**: Embedding-based similarity search
**Key Methods**:
```python
class SemanticSearch:
    def search(self, query: str, limit: int = 10, 
               filters: Optional[Dict] = None) -> List[SearchResult]
    def similar_to(self, embedding: List[float], limit: int) -> List[SearchResult]
```

#### `semantic_index.py`
**Purpose**: Manage semantic indices
**Key Components**:
- Index creation and updates
- Batch indexing
- Index optimization

#### `chunk_processor.py`
**Purpose**: Process text into embeddable chunks
**Key Methods**:
```python
class ChunkProcessor:
    def chunk_text(self, text: str, chunk_size: int = 512, 
                   overlap: int = 50) -> List[TextChunk]
    def chunk_code(self, code: str, language: str) -> List[CodeChunk]
```

---

### 4. H-MEM Tiered Memory Module (`memory/hmem/`)

#### `tier_manager.py`
**Purpose**: Coordinate L1/L2/L3 memory tiers
**Key Components**:
- Tier selection based on access patterns
- Cross-tier data movement
- Performance optimization

#### `l1_cache.py`
**Purpose**: In-memory hot cache (fastest)
**Characteristics**:
- LRU eviction
- Sub-millisecond access
- Limited capacity (configurable)

#### `l2_session.py`
**Purpose**: Session-scoped memory (medium)
**Characteristics**:
- Per-task working memory
- Cleared on task completion
- Supports complex queries

#### `l3_persistent.py`
**Purpose**: Long-term persistent storage (slowest)
**Characteristics**:
- SQLite-backed
- Unlimited capacity
- Full-text search

#### `tier_promotion.py`
**Purpose**: Automatic data movement between tiers
**Key Components**:
- Access frequency tracking
- Promotion criteria
- Demotion policies

---

### 5. Context Management Module (`memory/context/`)

#### `context_builder.py`
**Purpose**: Build context for LLM calls
**Key Methods**:
```python
class ContextBuilder:
    def with_episodes(self, episodes: List[EpisodeRecord]) -> ContextBuilder
    def with_semantic_results(self, results: List[SearchResult]) -> ContextBuilder
    def with_files(self, file_contents: Dict[str, str]) -> ContextBuilder
    def build(self, max_tokens: int) -> Context
```

#### `context_window.py`
**Purpose**: Token-aware context windowing
**Key Components**:
- Token counting per provider
- Sliding window management
- Priority-based truncation

#### `context_compressor.py`
**Purpose**: Compress context to fit limits
**Strategies**:
- Summarization
- Selective inclusion
- Importance ranking

#### `relevance_scorer.py`
**Purpose**: Score context relevance to current task
**Key Methods**:
```python
class RelevanceScorer:
    def score(self, context_item: Any, task: Task) -> float
    def rank(self, items: List[Any], task: Task) -> List[ScoredItem]
```

---

### 6. LLM Core Module (`llm/core/`)

#### `llm_client.py`
**Purpose**: Abstract LLM client interface
**Key Methods**:
```python
class LLMClient(ABC):
    @abstractmethod
    async def complete(self, messages: List[Message], **kwargs) -> Response
    
    @abstractmethod
    async def stream(self, messages: List[Message], **kwargs) -> AsyncIterator[Chunk]
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]
```

#### `llm_config.py`
**Purpose**: LLM configuration management
**Key Components**:
- Provider credentials
- Default models per task type
- Rate limits
- Retry policies

#### `llm_router.py`
**Purpose**: Route requests to appropriate providers
**Key Components**:
- Provider selection logic
- Fallback chains
- Load balancing

#### `model_selector.py`
**Purpose**: Dynamic model selection based on task
**Selection Criteria**:
- Task complexity
- Cost constraints
- Latency requirements
- Capability requirements

#### `cost_tracker.py`
**Purpose**: Track token usage and costs
**Key Methods**:
```python
class CostTracker:
    def record_usage(self, provider: str, model: str, 
                     input_tokens: int, output_tokens: int)
    def get_usage_report(self, period: str) -> UsageReport
    def get_estimated_cost(self) -> float
```

---

### 7. LLM Providers Module (`llm/providers/`)

| File | Provider | Models Supported |
|------|----------|------------------|
| `anthropic_provider.py` | Anthropic | Claude Opus, Sonnet, Haiku |
| `openai_provider.py` | OpenAI | GPT-4, GPT-4o, GPT-4o-mini |
| `azure_provider.py` | Azure | Azure OpenAI deployments |
| `ollama_provider.py` | Ollama | Llama, Mistral, Qwen, etc. |
| `google_provider.py` | Google | Gemini Pro, Gemini Flash |
| `groq_provider.py` | Groq | Llama, Mixtral (fast inference) |
| `openrouter_provider.py` | OpenRouter | Multi-provider gateway |

---

### 8. Embeddings Module (`llm/embeddings/`)

| File | Provider | Models |
|------|----------|--------|
| `openai_embedder.py` | OpenAI | text-embedding-3-small/large |
| `ollama_embedder.py` | Ollama | nomic-embed-text, all-minilm |
| `voyage_embedder.py` | Voyage AI | voyage-3, voyage-code-3 |
| `google_embedder.py` | Google | text-embedding-004 |
| `azure_embedder.py` | Azure | Azure embedding deployments |

---

### 9. Prompts Module (`llm/prompts/`)

#### `prompt_template.py`
**Purpose**: Jinja2-based template engine
**Features**:
- Variable substitution
- Conditional sections
- Loop support
- Includes

#### `prompt_registry.py`
**Purpose**: Named prompt storage and retrieval
**Key Methods**:
```python
class PromptRegistry:
    def register(self, name: str, template: str, metadata: dict)
    def get(self, name: str, **variables) -> str
    def list_prompts(self, category: str) -> List[PromptInfo]
```

#### `system_prompts.py`
**Purpose**: Agent-specific system prompts
**Contents**:
- Coder agent system prompt
- Reviewer agent system prompt
- Fixer agent system prompt
- Enterprise agent prompts

#### `prompt_composer.py`
**Purpose**: Build multi-part prompts
**Key Methods**:
```python
class PromptComposer:
    def with_system(self, system: str) -> PromptComposer
    def with_context(self, context: str) -> PromptComposer
    def with_examples(self, examples: List[Example]) -> PromptComposer
    def with_task(self, task: str) -> PromptComposer
    def compose(self) -> List[Message]
```

---

### 10. Streaming Module (`llm/streaming/`)

#### `stream_handler.py`
**Purpose**: Handle streaming LLM responses
**Key Components**:
- Async stream consumption
- Event emission for UI updates
- Error handling

#### `stream_buffer.py`
**Purpose**: Buffer partial responses
**Features**:
- Accumulate chunks
- Detect tool calls
- Handle interrupts

#### `stream_parser.py`
**Purpose**: Parse streaming chunks
**Formats**:
- SSE (Server-Sent Events)
- JSON Lines
- Provider-specific formats

---

### 11. Tool Calling Module (`llm/tools/`)

#### `tool_definition.py`
**Purpose**: Define tool schemas for LLM
**Key Components**:
```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: JSONSchema
    required: List[str]
```

#### `tool_executor.py`
**Purpose**: Execute tool calls from LLM
**Key Methods**:
```python
class ToolExecutor:
    def execute(self, tool_name: str, parameters: dict) -> ToolResult
    def validate_call(self, tool_name: str, parameters: dict) -> bool
```

#### `tool_result.py`
**Purpose**: Handle tool execution results
**Key Components**:
- Success/error result types
- Result serialization for LLM

#### `tool_validator.py`
**Purpose**: Validate tool parameters
**Key Components**:
- JSON Schema validation
- Type coercion
- Error messages

---

### 12. Types Module (`llm/types/`)

#### `llm_types.py`
```python
class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE = "azure"
    OLLAMA = "ollama"
    GOOGLE = "google"
    GROQ = "groq"
    OPENROUTER = "openrouter"
```

#### `message_types.py`
```python
@dataclass
class Message:
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
```

#### `response_types.py`
```python
@dataclass
class LLMResponse:
    content: str
    model: str
    usage: TokenUsage
    finish_reason: str
    tool_calls: Optional[List[ToolCall]] = None
```

#### `token_types.py`
```python
@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
@dataclass
class TokenCost:
    input_cost: float
    output_cost: float
    total_cost: float
```

---

## Integration Points

### With Agent System (Phase 1)
- Agents use `MemoryManager` for episode storage
- Agents receive `LLMClient` via dependency injection
- Enterprise agents use `SemanticSearch` for context

### With Orchestration (Phase 3)
- `ContextBuilder` provides task-relevant context
- `CostTracker` informs task scheduling decisions

### With UI (Phase 4)
- Memory viewer displays episodes
- Analytics dashboard shows usage/costs
- Streaming enables real-time output

---

## APEX Compliance

### Memory-First Principle
- All agent interactions stored as episodes
- Semantic indexing enables learning
- H-MEM ensures performance at scale

### Governance
- Cost tracking per agent/task
- Token limits enforced
- Usage reports for audit

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `memory/core/` | 4 | Core memory |
| `memory/episodic/` | 6 | Episode storage |
| `memory/semantic/` | 5 | Semantic memory |
| `memory/hmem/` | 6 | Tiered memory |
| `memory/context/` | 5 | Context building |
| `memory/types/` | 4 | Memory types |
| `llm/core/` | 6 | LLM core |
| `llm/providers/` | 8 | LLM providers |
| `llm/embeddings/` | 6 | Embedders |
| `llm/prompts/` | 5 | Prompt system |
| `llm/streaming/` | 4 | Streaming |
| `llm/tools/` | 5 | Tool calling |
| `llm/types/` | 5 | LLM types |
| **Total** | **69** | Phase 2 files |

---

## Next Steps

→ Phase 3: Skills, Tools & Orchestration Architecture
