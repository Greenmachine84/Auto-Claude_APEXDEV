# Architecture Decision Records (ADR)

> **Auto-Claude_APEXDEV Enhancement Project**
> Decision tracking for DEVAPEX integration
> Last Updated: January 6, 2026

---

## ADR Index

| ID | Decision | Status | Date |
|----|----------|--------|------|
| ADR-001 | Use Extension Over Modification principle | ✅ Accepted | 2026-01-05 |
| ADR-002 | Adopt Memory-First architecture pattern | ✅ Accepted | 2026-01-05 |
| ADR-003 | Implement DEVAPEX TaskQueue for prioritization | ✅ Accepted | 2026-01-05 |
| ADR-004 | Use AgentPool pattern for concurrency | ✅ Accepted | 2026-01-05 |
| ADR-005 | SQLite for episodic memory storage | ✅ Accepted | 2026-01-05 |
| ADR-006 | Electron IPC bridge pattern for UI-Backend | ✅ Accepted | 2026-01-05 |
| ADR-007 | React Kanban for task visualization | ✅ Accepted | 2026-01-05 |
| ADR-008 | Git worktrees for agent isolation | ✅ Accepted | 2026-01-05 |
| ADR-009 | APEX Constitution governance model | ✅ Accepted | 2026-01-05 |
| ADR-010 | Phased implementation approach | ✅ Accepted | 2026-01-05 |
| ADR-011 | APEXDEV_MERGE branch strategy | ✅ Accepted | 2026-01-05 |
| ADR-012 | 20-Agent Architecture (4 Core + 16 Enterprise) | ✅ Accepted | 2026-01-06 |
| ADR-013 | Hierarchical Agent Module Structure | ✅ Accepted | 2026-01-06 |
| ADR-014 | Agent Registry and Factory Pattern | ✅ Accepted | 2026-01-06 |
| ADR-015 | Agent Lifecycle Management System | ✅ Accepted | 2026-01-06 |

---

## ADR-012: 20-Agent Architecture (4 Core + 16 Enterprise)

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 1 - Agent System Architecture

### Context
DEVAPEX provides a comprehensive agent system with specialized agents for different development tasks. Auto-Claude needs to incorporate these capabilities.

### Decision
Adopt DEVAPEX's full 20-agent architecture:

**Core Agents (4)**:
1. CoderAgent - Primary autonomous coding
2. ReviewerAgent - Automated code review
3. FixerAgent - Automated issue resolution
4. OrchestratorAgent - Task coordination

**Enterprise Agents (16)**:
- Architecture (7): System, Refactor, Performance, Integration, Data, Cloud, DevOps
- Security (3): Security Architect, Red Team, Blue Team
- Quality (2): QA Verification, Compliance Auditor
- Documentation (1): Documentation Lead
- API (1): API Design
- Orchestration (1): MDA Orchestrator
- Base (1): Base Enterprise Agent

### Rationale
- Complete coverage of software development lifecycle
- Specialized agents for enterprise needs
- Modular architecture allows selective deployment
- Aligns with DEVAPEX proven patterns

### Consequences
- 37 files in Phase 1 agent system
- Requires careful dependency management
- Enterprise agents optional for basic usage

---

## ADR-013: Hierarchical Agent Module Structure

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 1 - Agent System Architecture

### Context
16 enterprise agents need logical organization for maintainability.

### Decision
Organize enterprise agents into domain-specific submodules:

```
agents/enterprise/
├── architecture/   # 7 architect agents
├── security/       # 3 security agents  
├── quality/        # 2 QA/compliance agents
├── documentation/  # 1 doc agent
├── api/            # 1 API design agent
└── orchestration/  # 1 MDA orchestrator
```

### Rationale
- Clear separation of concerns
- Easier navigation and discovery
- Supports team ownership boundaries
- Follows Python package best practices

### Consequences
- Deeper import paths for enterprise agents
- May need re-export modules for convenience

---

## ADR-014: Agent Registry and Factory Pattern

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 1 - Agent System Architecture

### Context
With 20 agent types, need a centralized way to discover and instantiate agents.

### Decision
Implement Agent Registry and Factory:

1. **AgentRegistry**: Singleton containing all registered agent types
   - Dynamic registration via decorators
   - Lookup by type, capability, or name
   - Supports plugin architecture

2. **AgentFactory**: Creates configured agent instances
   - Dependency injection for LLM, memory, tools
   - Configuration validation
   - Optional instance caching

### Rationale
- Decouples agent creation from usage
- Enables dynamic agent discovery
- Supports testing with mock agents
- Follows established enterprise patterns

### Consequences
- Slight indirection in agent creation
- Registry must be initialized at startup

---

## ADR-015: Agent Lifecycle Management System

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 1 - Agent System Architecture

### Context
Agents need proper startup, health monitoring, and graceful shutdown.

### Decision
Implement dedicated lifecycle module with:

1. **agent_lifecycle.py**: Start/stop agent instances
2. **health_check.py**: Heartbeat and failure detection
3. **graceful_shutdown.py**: Clean termination with state persistence

### Rationale
- Prevents resource leaks
- Enables recovery from failures
- Supports long-running agent processes
- Critical for production reliability

### Consequences
- All agents must implement lifecycle interface
- Health checks add minimal overhead

---

## Previous Decisions (ADR-001 to ADR-011)

### ADR-001: Extension Over Modification
**Decision**: New features extend existing modules rather than modifying core

### ADR-002: Memory-First Architecture
**Decision**: All agent operations store episodes for learning

### ADR-003: DEVAPEX TaskQueue
**Decision**: Priority-based task queue (CRITICAL > HIGH > MEDIUM > LOW)

### ADR-004: AgentPool Pattern
**Decision**: Pool of reusable agent instances with concurrency limits

### ADR-005: SQLite for Memory
**Decision**: SQLite for episodic memory with full-text search

### ADR-006: Electron IPC Bridge
**Decision**: IPC pattern for UI-Backend communication

### ADR-007: React Kanban
**Decision**: Kanban board for task visualization

### ADR-008: Git Worktrees
**Decision**: Isolated workspaces per agent via git worktrees

### ADR-009: APEX Constitution
**Decision**: Governance model with HITL hooks and compliance

### ADR-010: Phased Implementation
**Decision**: 5-phase rollout for manageable delivery

### ADR-011: APEXDEV_MERGE Branch
**Decision**: All work on dedicated branch until verified

---

*Document maintained as part of APEX governance requirements*
