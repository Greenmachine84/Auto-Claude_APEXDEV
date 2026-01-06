# Architecture Decision Records (ADR)

> **Auto-Claude_APEXDEV Enhancement Project**
> Decision tracking for DEVAPEX integration
> Last Updated: January 6, 2026

---

## ADR Index

| ID | Decision | Status | Phase | Date |
|----|----------|--------|-------|------|
| ADR-001 | Use Extension Over Modification principle | ✅ Accepted | - | 2026-01-05 |
| ADR-002 | Adopt Memory-First architecture pattern | ✅ Accepted | - | 2026-01-05 |
| ADR-003 | Implement DEVAPEX TaskQueue for prioritization | ✅ Accepted | - | 2026-01-05 |
| ADR-004 | Use AgentPool pattern for concurrency | ✅ Accepted | - | 2026-01-05 |
| ADR-005 | SQLite for episodic memory storage | ✅ Accepted | - | 2026-01-05 |
| ADR-006 | Electron IPC bridge pattern for UI-Backend | ✅ Accepted | - | 2026-01-05 |
| ADR-007 | React Kanban for task visualization | ✅ Accepted | - | 2026-01-05 |
| ADR-008 | Git worktrees for agent isolation | ✅ Accepted | - | 2026-01-05 |
| ADR-009 | APEX Constitution governance model | ✅ Accepted | - | 2026-01-05 |
| ADR-010 | Phased implementation approach | ✅ Accepted | - | 2026-01-05 |
| ADR-011 | APEXDEV_MERGE branch strategy | ✅ Accepted | - | 2026-01-05 |
| ADR-012 | 20-Agent Architecture (4 Core + 16 Enterprise) | ✅ Accepted | 1 | 2026-01-06 |
| ADR-013 | Hierarchical Agent Module Structure | ✅ Accepted | 1 | 2026-01-06 |
| ADR-014 | Agent Registry and Factory Pattern | ✅ Accepted | 1 | 2026-01-06 |
| ADR-015 | Agent Lifecycle Management System | ✅ Accepted | 1 | 2026-01-06 |
| ADR-016 | H-MEM Tiered Memory Architecture | ✅ Accepted | 2 | 2026-01-06 |
| ADR-017 | Multi-Provider LLM Strategy | ✅ Accepted | 2 | 2026-01-06 |
| ADR-018 | Semantic Search with Vector Embeddings | ✅ Accepted | 2 | 2026-01-06 |
| ADR-019 | Tool Calling Framework | ✅ Accepted | 2 | 2026-01-06 |

---

## Phase 2 Decisions

### ADR-016: H-MEM Tiered Memory Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 2 - Memory System Architecture

#### Context
DEVAPEX implements hierarchical memory (H-MEM) with L1/L2/L3 tiers for performance optimization. Different memory access patterns require different storage strategies.

#### Decision
Implement 3-tier memory architecture:

| Tier | Storage | Speed | Capacity | Use Case |
|------|---------|-------|----------|----------|
| L1 | In-memory LRU | <1ms | Limited | Hot cache, frequent access |
| L2 | Session store | ~10ms | Medium | Working memory per task |
| L3 | SQLite + FTS5 | ~50ms | Unlimited | Long-term persistence |

**Tier Promotion Logic**:
- Items accessed 3+ times promoted to L1
- Session-critical data kept in L2
- All data persisted to L3

#### Rationale
- Optimizes memory access latency
- Reduces database load for hot data
- Maintains full persistence guarantees
- Follows DEVAPEX proven patterns

#### Consequences
- Additional complexity in tier management
- Memory usage needs monitoring
- Background promotion jobs required

---

### ADR-017: Multi-Provider LLM Strategy

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 2 - LLM Integration Architecture

#### Context
Different tasks require different LLM capabilities. Cost, latency, and quality vary by provider.

#### Decision
Support 7 LLM providers with intelligent routing:

| Provider | Models | Best For |
|----------|--------|----------|
| Anthropic | Claude Opus, Sonnet, Haiku | Complex reasoning, code |
| OpenAI | GPT-4o, GPT-4o-mini | General tasks |
| Azure | Azure OpenAI | Enterprise compliance |
| Ollama | Llama, Mistral | Local/private, cost |
| Google | Gemini | Long context |
| Groq | Llama (fast) | Low latency |
| OpenRouter | Multi-provider | Flexibility |

**Routing Strategy**:
- Model selector chooses based on task complexity
- Fallback chains for resilience
- Cost tracking per provider

#### Rationale
- No single provider is best for all tasks
- Local models enable privacy/cost control
- Fallbacks prevent service interruptions

#### Consequences
- Multiple API keys to manage
- Provider-specific code in adapters
- Cost tracking across providers

---

### ADR-018: Semantic Search with Vector Embeddings

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 2 - Memory System Architecture

#### Context
Episodic memory needs semantic search for context-aware retrieval beyond keyword matching.

#### Decision
Implement semantic search layer with:

1. **5 Embedding Providers**:
   - OpenAI text-embedding-3
   - Ollama (local)
   - Voyage AI
   - Google
   - Azure

2. **Chunk Processing**:
   - Text chunking (512 tokens, 50 overlap)
   - Code-aware chunking by AST

3. **Similarity Search**:
   - Cosine similarity scoring
   - Metadata filtering
   - Relevance ranking

#### Rationale
- Semantic search finds conceptually similar content
- Multiple providers prevent lock-in
- Code chunking preserves function boundaries

#### Consequences
- Embedding costs add up
- Vector storage needed (SQLite with extensions or dedicated DB)
- Reindexing required when switching providers

---

### ADR-019: Tool Calling Framework

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 2 - LLM Integration Architecture

#### Context
LLM function calling is core to agent capabilities. Need standardized tool definition and execution.

#### Decision
Implement tool calling framework:

1. **Tool Definition**: JSON Schema-based parameter definitions
2. **Tool Registry**: Central registry of available tools
3. **Tool Executor**: Safe execution with timeout and error handling
4. **Tool Validator**: Parameter validation before execution

**Tool Result Format**:
```python
@dataclass
class ToolResult:
    tool_name: str
    success: bool
    result: Any
    error: Optional[str]
    duration_ms: int
```

#### Rationale
- Standardized format across all providers
- Validation prevents malformed calls
- Duration tracking for performance
- Error handling for reliability

#### Consequences
- All tools must conform to schema
- Schema changes need migration
- Provider-specific adaptations needed

---

## Phase 1 Decisions (Reference)

### ADR-012: 20-Agent Architecture
**Decision**: 4 core agents + 16 enterprise agents covering full SDLC

### ADR-013: Hierarchical Agent Module Structure
**Decision**: Enterprise agents organized by domain (architecture, security, quality, etc.)

### ADR-014: Agent Registry and Factory Pattern
**Decision**: Centralized agent discovery and instantiation

### ADR-015: Agent Lifecycle Management System
**Decision**: Startup, health check, and graceful shutdown management

---

## Initial Decisions (Reference)

### ADR-001 through ADR-011
See initial project setup documentation for foundational decisions including:
- Extension Over Modification principle
- Memory-First architecture
- TaskQueue and AgentPool patterns
- SQLite for storage
- Electron IPC bridge
- React Kanban UI
- Git worktrees isolation
- APEX Constitution governance
- Phased implementation
- APEXDEV_MERGE branch strategy

---

*Document maintained as part of APEX governance requirements*
