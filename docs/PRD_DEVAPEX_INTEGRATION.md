# Product Requirements Document: DEVAPEX Integration

> **Auto-Claude_APEXDEV Enhancement Plan**
>
> Comprehensive technical PRD for integrating DEVAPEX features into Auto-Claude

---

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2026-01-05 |
| **Status** | Draft - Pending Approval |
| **Author** | Auto-Claude Enhancement Team |
| **Reviewers** | Project Stakeholders |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [Source Repository Analysis](#3-source-repository-analysis)
4. [Feature Integration Matrix](#4-feature-integration-matrix)
5. [Implementation Phases](#5-implementation-phases)
6. [Technical Specifications](#6-technical-specifications)
7. [Risk Assessment](#7-risk-assessment)
8. [Success Criteria](#8-success-criteria)
9. [Appendices](#9-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

This PRD defines the technical requirements for integrating DEVAPEX's enterprise features into Auto-Claude_APEXDEV. The goal is to enhance Auto-Claude's autonomous coding capabilities with:

- **Task Orchestration**: Priority-based task queue with agent pooling
- **Episodic Memory**: Cross-session context and pattern learning
- **Enterprise Features**: Project management, secrets handling, team collaboration
- **Enhanced UI**: Visual Kanban with agent linking and memory views

### 1.2 Scope

| In Scope | Out of Scope |
|----------|-------------|
| TaskQueue + AgentPool | Full OAuth implementation |
| Episodic Memory layer | Real-time collaboration |
| Secrets Manager | Video/voice channels |
| Projects Manager | HITL approval gates |
| Enhanced Kanban UI | Auto-updates system |
| Multi-LLM routing | Full APEX councils |

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Unit test coverage | ≥80% new code |
| Regression rate | 0 breaking changes |
| Performance impact | <5% overhead |
| User verification | Sign-off required |

---

## 2. Project Overview

### 2.1 Background

**Auto-Claude** (v2.7.2) is a production autonomous coding framework using Claude Agent SDK. It features:
- Multi-agent system (Planner, Coder, QA Reviewer, QA Fixer)
- Spec creation pipeline with complexity assessment
- Git worktree isolation for safe development
- Graphiti memory with semantic search

**DEVAPEX** (v2.0.0 dev/v2.0-multi-llm) extends Auto-Claude with:
- Enterprise-grade orchestration
- Multi-LLM provider support
- APEX governance framework
- Team collaboration features

### 2.2 Objectives

1. **Enhance Task Management**: Add prioritized queue and parallel execution
2. **Improve Context Retention**: Episodic memory for cross-session learning
3. **Strengthen Security**: Encrypted secrets with scoped access
4. **Modernize UI**: Visual task management with agent visibility

### 2.3 Constraints

- **APEX M1.2.1**: All changes must be ADDITIVE
- **Claude SDK**: Must remain primary AI provider
- **Backward Compatibility**: Existing CLI workflow preserved
- **Testing**: User verification before any merge

---

## 3. Source Repository Analysis

### 3.1 DEVAPEX Structure (dev/v2.0-multi-llm)

```
DEVAPEX/
├── apps/backend/devapex/
│   ├── agents/           # Agent implementations + enterprise agents
│   ├── analytics/        # Usage analytics
│   ├── auth/             # OAuth + SSO
│   ├── core/             # Types, config, utilities
│   ├── engines/          # Execution engines
│   ├── integrations/     # External service integrations
│   ├── llm/              # Multi-LLM router
│   ├── memory/           # Episodic memory store
│   ├── notifications/    # Alert system
│   ├── orchestrator/     # TaskQueue + AgentPool
│   ├── prediction/       # Bug predictor
│   ├── projects/         # Project lifecycle
│   ├── qa/               # QA loop enhancements
│   ├── secrets/          # Encrypted secrets
│   ├── security/         # Security hooks
│   ├── skills/           # Skill framework
│   ├── spec/             # Spec pipeline
│   ├── teams/            # Team collaboration
│   └── tools_pkg/        # Custom MCP tools
└── apps/desktop/         # Electron + React UI
```

### 3.2 Auto-Claude Structure (APEXDEV_MERGE)

```
Auto-Claude_APEXDEV/
├── apps/backend/
│   ├── agents/           # Existing agent implementations
│   ├── core/             # Client, auth, security
│   ├── integrations/     # Graphiti, Linear, GitHub
│   ├── memory/           # Basic memory store
│   ├── merge/            # AI merge conflict resolution
│   ├── prediction/       # Bug prediction
│   ├── qa/               # QA loop
│   ├── spec/             # Spec pipeline
│   └── prompts/          # Agent prompts
└── apps/frontend/        # Electron desktop app
```

### 3.3 Gap Analysis Summary

| Category | Auto-Claude | DEVAPEX | Gap |
|----------|-------------|---------|-----|
| Task Queue | Direct invocation | Priority queue | ❗ Add |
| Agent Pool | Ad-hoc spawning | Managed pool | ❗ Add |
| Memory | Graphiti only | Graphiti + Episodes | ❗ Enhance |
| Secrets | .env files | Encrypted store | ❗ Add |
| Projects | Per-spec | Full lifecycle | ❗ Add |
| Multi-LLM | Claude only | 4 providers | ⚠️ Optional |
| Teams | None | Full collab | ⚠️ Phase 3 |

---

## 4. Feature Integration Matrix

### 4.1 HIGH Priority Features

| Feature | Source | Target | Complexity | Dependencies |
|---------|--------|--------|------------|---------------|
| TaskQueue | `orchestrator/manager.py:70-91` | `orchestrator/task_queue.py` | Medium | None |
| AgentPool | `orchestrator/manager.py:150-178` | `orchestrator/agent_pool.py` | Medium | TaskQueue |
| OrchestratorManager | `orchestrator/manager.py` | `orchestrator/manager.py` | High | Both above |
| EpisodeStore | `memory/store.py` | `memory/episodes.py` | Medium | None |
| SemanticSearch | `memory/search.py` | `memory/search.py` | Medium | EpisodeStore |
| SecretsManager | `secrets/manager.py` | `secrets/manager.py` | High | None |
| SessionMemoryTools | `tools_pkg/session_memory.py` | `tools_pkg/session_memory.py` | Low | EpisodeStore |

### 4.2 MEDIUM Priority Features

| Feature | Source | Target | Complexity | Dependencies |
|---------|--------|--------|------------|---------------|
| ProjectsManager | `projects/manager.py` | `projects/manager.py` | Medium | None |
| LLMRouter | `llm/router.py` | `llm/router.py` | High | Providers |
| SpecialistReviewers | `agents/specialists/` | `agents/specialists/` | Medium | None |
| KanbanEnhancements | `desktop/components/kanban/` | `frontend/components/kanban/` | Medium | Orchestrator |
| APEXGovernance | `integration/` | `integration/` | Low | None |

### 4.3 LOW Priority Features

| Feature | Source | Target | Complexity | Dependencies |
|---------|--------|--------|------------|---------------|
| TeamsManager | `teams/manager.py` | `teams/manager.py` | High | OAuth |
| BugPredictor | `prediction/` | Already exists | N/A | - |
| Notifications | `notifications/` | Optional | Low | None |
| Analytics | `analytics/` | Optional | Low | None |

---

## 5. Implementation Phases

### Phase 1: Task Orchestration (Week 1-2)

**Goal**: Implement prioritized task queue with agent pooling

#### Deliverables

1. **TaskQueue Module**
   - File: `apps/backend/orchestrator/task_queue.py`
   - Priority enum: CRITICAL(0), HIGH(1), MEDIUM(2), LOW(3)
   - Async queue with priority ordering
   - Status tracking: PENDING, RUNNING, COMPLETED, FAILED

2. **AgentPool Module**
   - File: `apps/backend/orchestrator/agent_pool.py`
   - Max agents: 12 (matches terminal grid)
   - Max concurrent: 6 (resource protection)
   - Idle timeout: 300 seconds
   - Agent lifecycle: acquire, execute, release

3. **Orchestrator Manager**
   - File: `apps/backend/orchestrator/manager.py`
   - Task submission API
   - Event emission for UI updates
   - Result collection

#### Acceptance Criteria

- [ ] Tasks can be submitted with priority
- [ ] Tasks execute in priority order
- [ ] Agent pool respects limits
- [ ] Events emitted for UI
- [ ] Unit tests pass (80%+ coverage)

---

### Phase 2: Memory Enhancement (Week 3-4)

**Goal**: Add episodic memory with semantic search

#### Deliverables

1. **EpisodeStore**
   - File: `apps/backend/memory/episodes.py`
   - SQLite persistence
   - EpisodeRecord model
   - CRUD operations

2. **SemanticSearch**
   - File: `apps/backend/memory/search.py`
   - Vector embeddings (OpenAI, Voyage AI, Ollama)
   - Similarity search
   - Result ranking

3. **UnifiedMemory API**
   - File: `apps/backend/memory/unified.py`
   - Merge Graphiti + Episodes
   - Single search interface
   - Pattern extraction

4. **Session Memory Tools**
   - `record_discovery`: API behaviors, quirks
   - `record_gotcha`: Pitfalls with avoidance
   - `record_pattern`: Learned codebase patterns
   - `get_session_context`: Context retrieval

#### Acceptance Criteria

- [ ] Episodes persist across sessions
- [ ] Search returns relevant results
- [ ] Graphiti integration preserved
- [ ] MCP tools functional
- [ ] Unit tests pass (80%+ coverage)

---

### Phase 3: Enterprise Features (Week 5-6)

**Goal**: Add projects and secrets management

#### Deliverables

1. **SecretsManager**
   - File: `apps/backend/secrets/manager.py`
   - PBKDF2 + Fernet encryption
   - Scopes: USER, PROJECT, GLOBAL
   - Version history (10 versions)
   - Audit trail

2. **ProjectsManager**
   - File: `apps/backend/projects/manager.py`
   - Lifecycle: DRAFT → ACTIVE → ARCHIVED
   - Semantic versioning
   - Repository integration

3. **IPC Handlers**
   - `secrets:store`, `secrets:get`, `secrets:list`
   - `projects:create`, `projects:update`, `projects:version`

#### Acceptance Criteria

- [ ] Secrets encrypted at rest
- [ ] Project lifecycle works
- [ ] Version bumping functional
- [ ] IPC handlers respond correctly
- [ ] Unit tests pass (80%+ coverage)

---

### Phase 4: UI/UX Enhancements (Week 7-8)

**Goal**: Enhanced Kanban with agent visibility

#### Deliverables

1. **Enhanced Kanban**
   - Priority color indicators
   - Task-to-agent linking
   - Drag-drop status updates
   - Real-time status via orchestrator events

2. **Memory Panel**
   - Episode history viewer
   - Pattern/gotcha display
   - Search interface

3. **Settings Enhancements**
   - Agent configuration UI
   - Memory settings
   - Secrets management UI

#### Acceptance Criteria

- [ ] Priorities visible on cards
- [ ] Agent assignment shown
- [ ] Drag-drop updates backend
- [ ] Memory searchable in UI
- [ ] Settings persist correctly

---

### Phase 5: Testing & Validation (Week 9-10)

**Goal**: Comprehensive testing and user sign-off

#### Deliverables

1. **Unit Tests**
   - Orchestrator tests
   - Memory tests
   - Secrets tests
   - Projects tests

2. **Integration Tests**
   - Task flow tests
   - Memory integration
   - UI-backend integration

3. **E2E Tests**
   - Full Kanban workflow
   - Secrets encryption/decryption
   - Memory search accuracy

4. **Documentation**
   - Updated CLAUDE.md
   - API documentation
   - User guide updates

#### Acceptance Criteria

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] No regressions detected
- [ ] User verification complete
- [ ] Documentation updated

---

## 6. Technical Specifications

### 6.1 TaskQueue Specification

```python
# apps/backend/orchestrator/task_queue.py

from enum import IntEnum
from dataclasses import dataclass
from datetime import datetime
import asyncio
import heapq

class TaskPriority(IntEnum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueuedTask:
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    spec_id: str | None = None
    agent_type: str = "coder"
    
    def __lt__(self, other):
        return self.priority < other.priority

class TaskQueue:
    def __init__(self):
        self._queue: list[QueuedTask] = []
        self._lock = asyncio.Lock()
    
    async def enqueue(self, task: QueuedTask) -> str:
        async with self._lock:
            heapq.heappush(self._queue, task)
            return task.id
    
    async def dequeue(self) -> QueuedTask | None:
        async with self._lock:
            if self._queue:
                return heapq.heappop(self._queue)
            return None
    
    async def get_status(self, task_id: str) -> TaskStatus | None:
        # Implementation
        pass
```

### 6.2 AgentPool Specification

```python
# apps/backend/orchestrator/agent_pool.py

@dataclass
class AgentPoolConfig:
    max_agents: int = 12
    max_concurrent_tasks: int = 6
    idle_timeout_seconds: int = 300
    agent_types: list[str] = field(default_factory=lambda: ["coder", "reviewer", "fixer"])

class AgentPool:
    def __init__(self, config: AgentPoolConfig):
        self.config = config
        self._agents: dict[str, AgentInstance] = {}
        self._active_tasks: dict[str, str] = {}  # task_id -> agent_id
    
    async def acquire(self, agent_type: str) -> AgentInstance:
        # Find idle or create new
        pass
    
    async def release(self, agent_id: str) -> None:
        # Return to pool
        pass
    
    async def cleanup_idle(self) -> int:
        # Remove stale agents
        pass
```

### 6.3 EpisodeStore Specification

```python
# apps/backend/memory/episodes.py

@dataclass
class EpisodeRecord:
    id: str
    agent_id: str
    input_text: str
    output: str
    tools_used: list[str]
    success: bool
    timestamp: datetime
    spec_id: str | None = None
    duration_ms: float = 0.0
    metadata: dict = field(default_factory=dict)

class EpisodeStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    async def store(self, episode: EpisodeRecord) -> str:
        # SQLite insert
        pass
    
    async def search(self, query: str, limit: int = 10) -> list[EpisodeRecord]:
        # Full-text search
        pass
    
    async def get_by_agent(self, agent_id: str, limit: int = 50) -> list[EpisodeRecord]:
        # Filter by agent
        pass
```

---

## 7. Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking changes | High | Low | Feature toggles, phased rollout |
| Performance regression | Medium | Medium | Benchmarking, lazy loading |
| Integration conflicts | Medium | Medium | Staged merging, thorough testing |
| Claude SDK incompatibility | High | Low | SDK version pinning |
| Memory bloat | Medium | Medium | Retention policies, cleanup |

---

## 8. Success Criteria

### 8.1 Technical Criteria

- [ ] All 5 phases completed
- [ ] ≥80% test coverage on new code
- [ ] Zero regressions in existing features
- [ ] <5% performance overhead
- [ ] All ADRs implemented per Decision.md

### 8.2 User Verification

- [ ] Task orchestration demo completed
- [ ] Memory search demo completed
- [ ] Secrets management demo completed
- [ ] Kanban UI demo completed
- [ ] Sign-off received

### 8.3 Documentation

- [ ] CLAUDE.md updated
- [ ] API docs complete
- [ ] Decision.md finalized
- [ ] Changelog maintained

---

## 9. Appendices

### Appendix A: Related Documents

- [Decision Log](Decision.md)
- [Integration Changelog](DEVAPEX_CHANGELOG.md)
- [Archive Guidelines](../archive/README.md)
- [DEVAPEX Architecture](https://github.com/Greenmachine84/DEVAPEX/blob/dev/v2.0-multi-llm/docs/ARCHITECTURE.md)

### Appendix B: Environment Variables

```bash
# Phase 1: Orchestration
DEVAPEX_TASK_QUEUE_ENABLED=true
DEVAPEX_AGENT_POOL_MAX=12
DEVAPEX_CONCURRENT_TASKS_MAX=6

# Phase 2: Memory
DEVAPEX_EPISODIC_MEMORY_ENABLED=true
DEVAPEX_MEMORY_RETENTION_DAYS=30

# Phase 3: Enterprise
DEVAPEX_SECRETS_ENABLED=true
DEVAPEX_SECRETS_MASTER_KEY=<encrypted>
DEVAPEX_PROJECTS_ENABLED=true
```

### Appendix C: File Creation Checklist

```
Phase 1:
[ ] apps/backend/orchestrator/__init__.py
[ ] apps/backend/orchestrator/task_queue.py
[ ] apps/backend/orchestrator/agent_pool.py
[ ] apps/backend/orchestrator/manager.py
[ ] apps/backend/orchestrator/types.py
[ ] tests/test_orchestrator.py

Phase 2:
[ ] apps/backend/memory/episodes.py
[ ] apps/backend/memory/search.py
[ ] apps/backend/memory/unified.py
[ ] apps/backend/tools_pkg/session_memory.py
[ ] tests/test_unified_memory.py

Phase 3:
[ ] apps/backend/secrets/__init__.py
[ ] apps/backend/secrets/manager.py
[ ] apps/backend/secrets/encryption.py
[ ] apps/backend/projects/__init__.py
[ ] apps/backend/projects/manager.py
[ ] tests/test_secrets.py
[ ] tests/test_projects.py

Phase 4:
[ ] apps/frontend/src/renderer/components/kanban/EnhancedKanban.tsx
[ ] apps/frontend/src/renderer/components/memory/MemoryPanel.tsx
[ ] apps/frontend/src/renderer/components/settings/SecretsSettings.tsx
[ ] apps/frontend/src/main/ipc-handlers/orchestrator-handlers.ts
[ ] apps/frontend/src/main/ipc-handlers/memory-handlers.ts
[ ] apps/frontend/src/main/ipc-handlers/secrets-handlers.ts
```

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Lead | | | |
| Technical Lead | | | |
| QA Lead | | | |
| User Representative | | | |

---

*Document generated: 2026-01-05*
