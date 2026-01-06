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
| ADR-020 | Skills Framework Architecture | ✅ Accepted | 3 | 2026-01-06 |
| ADR-021 | Tool Permission and Sandbox System | ✅ Accepted | 3 | 2026-01-06 |
| ADR-022 | Priority TaskQueue Implementation | ✅ Accepted | 3 | 2026-01-06 |
| ADR-023 | Workflow Engine with DSL | ✅ Accepted | 3 | 2026-01-06 |
| ADR-024 | Electron IPC Architecture | ✅ Accepted | 4 | 2026-01-06 |
| ADR-025 | React Component Architecture | ✅ Accepted | 4 | 2026-01-06 |
| ADR-026 | Zustand State Management | ✅ Accepted | 4 | 2026-01-06 |
| ADR-027 | Multi-Platform Integration Strategy | ✅ Accepted | 4 | 2026-01-06 |

---

## Phase 4 Decisions

### ADR-024: Electron IPC Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 4 - UI, Integrations & Analytics

#### Context
Desktop app needs secure communication between Electron main process and renderer. DEVAPEX uses IPC bridge pattern.

#### Decision
Implement structured IPC with domain-specific handlers:

**IPC Channels**:
| Domain | Channel Prefix | Handlers |
|--------|----------------|----------|
| Tasks | `task:` | create, update, delete, list |
| Agents | `agent:` | start, stop, status, logs |
| Memory | `memory:` | search, get, store |
| Settings | `settings:` | get, set, reset |

**Architecture**:
```
Renderer (React)
    ↓
  Preload API (contextBridge)
    ↓
  IPC Handlers (main process)
    ↓
  Backend Service (Python)
```

#### Rationale
- Security: contextBridge prevents direct node access
- Type safety: TypeScript interfaces both sides
- Domain separation: Clear handler responsibilities

#### Consequences
- Must maintain sync between preload and main
- Serialization overhead for complex objects
- Testing requires mocking IPC

---

### ADR-025: React Component Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 4 - UI, Integrations & Analytics

#### Context
Need modular, reusable UI components. DEVAPEX uses domain-organized components.

#### Decision
Organize components by feature domain:

```
components/
├── common/      # Shared primitives (Button, Card, Modal)
├── kanban/      # Task board components
├── terminal/    # Terminal grid components
├── agents/      # Agent monitoring
├── memory/      # Memory viewer
├── workflow/    # Workflow visualization
├── settings/    # Settings pages
└── analytics/   # Analytics dashboard
```

**Component Patterns**:
- Hooks for data fetching
- Store slices for state
- TypeScript for props
- CSS modules for styling

#### Rationale
- Feature folders enable team ownership
- Shared common prevents duplication
- Clear import paths

#### Consequences
- Index files needed for exports
- May have cross-domain dependencies
- Component naming must be unique

---

### ADR-026: Zustand State Management

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 4 - UI, Integrations & Analytics

#### Context
Need state management that's simpler than Redux but robust enough for complex app.

#### Decision
Use Zustand with domain slices:

**Store Slices**:
| Slice | State | Persistence |
|-------|-------|-----------|
| `taskSlice` | Tasks, filters | No |
| `agentSlice` | Agents, pool | No |
| `memorySlice` | Episodes, search | No |
| `uiSlice` | Modals, sidebar | No |
| `settingsSlice` | All settings | Yes (persist middleware) |

**Features**:
- Devtools integration for debugging
- Persist middleware for settings
- Subscriptions for real-time updates

#### Rationale
- Simpler than Redux (no boilerplate)
- TypeScript-first design
- Persist for settings only
- Good React integration

#### Consequences
- Team must learn Zustand patterns
- Less ecosystem than Redux
- Careful with large state updates

---

### ADR-027: Multi-Platform Integration Strategy

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 4 - UI, Integrations & Analytics

#### Context
Need to integrate with multiple external platforms for task sync and notifications.

#### Decision
Support 5 integration platforms with consistent patterns:

| Platform | Purpose | Auth Method |
|----------|---------|-------------|
| GitHub | PR/Issue sync | OAuth, PAT |
| GitLab | MR/Issue sync | OAuth, PAT |
| Linear | Issue sync | OAuth |
| Slack | Notifications | OAuth (workspace) |
| JIRA | Issue sync | API Token, OAuth |

**Integration Pattern**:
```python
class IntegrationClient(ABC):
    async def authenticate() -> Token
    async def sync_tasks() -> List[Task]
    async def handle_webhook(event: dict) -> None
```

**Webhook Support**:
- Each integration has webhook handler
- Bidirectional sync supported
- Rate limiting implemented

#### Rationale
- Covers major dev tools
- Consistent interface across platforms
- Webhook enables real-time sync

#### Consequences
- Multiple OAuth flows to implement
- Webhook server needed
- Rate limits per platform

---

## Previous Phases (Reference)

### Phase 3 (ADR-020 to ADR-023)
- Skills Framework, Tool Sandbox, TaskQueue, Workflow Engine

### Phase 2 (ADR-016 to ADR-019)
- H-MEM Memory, Multi-Provider LLM, Semantic Search, Tool Calling

### Phase 1 (ADR-012 to ADR-015)
- 20-Agent Architecture, Module Structure, Registry, Lifecycle

### Initial (ADR-001 to ADR-011)
- Core principles and foundational decisions

---

*Document maintained as part of APEX governance requirements*
