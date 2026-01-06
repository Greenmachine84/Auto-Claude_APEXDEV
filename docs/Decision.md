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

---

## Phase 3 Decisions

### ADR-020: Skills Framework Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 3 - Skills, Tools & Orchestration

#### Context
DEVAPEX provides a comprehensive skills framework with 10+ skill types. Skills represent high-level capabilities that compose tools.

#### Decision
Implement 5-category skills framework:

| Category | Skills | Description |
|----------|--------|-------------|
| Coding | 4 | Code generation, refactoring, explanation, translation |
| Testing | 3 | Test generation, execution, coverage analysis |
| Review | 3 | Code review, security review, architecture review |
| Documentation | 3 | Docstrings, README, API docs |
| Analysis | 3 | Dependency, complexity, impact analysis |

**Skill Architecture**:
```
BaseSkill (abstract)
  ├── execute(context) -> SkillResult
  ├── validate_input(data) -> bool
  └── get_dependencies() -> List[str]
```

#### Rationale
- Skills abstract complex multi-tool operations
- Category organization aids discovery
- Dependency tracking enables chaining
- Validation ensures quality inputs

#### Consequences
- 16 skill implementations needed
- Skills depend on tool availability
- Must handle tool failures gracefully

---

### ADR-021: Tool Permission and Sandbox System

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 3 - Skills, Tools & Orchestration

#### Context
Tools can execute dangerous operations (file writes, commands). Need safety mechanisms.

#### Decision
Implement permission-based sandboxed execution:

**Permission Levels**:
```python
class Permission(Enum):
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_COMMANDS = "execute_commands"
    NETWORK_ACCESS = "network_access"
    GIT_OPERATIONS = "git_operations"
    SPAWN_PROCESSES = "spawn_processes"
```

**Sandbox Features**:
- Resource limits (CPU, memory, time)
- Filesystem isolation (allow-list paths)
- Network restrictions
- Complete audit logging

#### Rationale
- Defense in depth for security
- Audit trail for compliance
- Resource limits prevent runaway
- Isolation limits blast radius

#### Consequences
- Performance overhead for sandboxing
- Agent capabilities limited by permissions
- Admin must configure permissions

---

### ADR-022: Priority TaskQueue Implementation

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 3 - Skills, Tools & Orchestration

#### Context
Tasks have varying urgency. Need priority-based scheduling with persistence.

#### Decision
Implement priority queue with 4 levels:

| Priority | Value | Behavior |
|----------|-------|----------|
| CRITICAL | 0 | Immediate execution, preempt if needed |
| HIGH | 1 | Next in queue after critical |
| MEDIUM | 2 | Standard priority |
| LOW | 3 | Background, when resources available |

**Features**:
- Persistent queue (survives restarts)
- Starvation prevention (age-based boost)
- Queue metrics and monitoring
- Deadline-aware scheduling

#### Rationale
- Critical tasks need immediate attention
- Persistence prevents task loss
- Starvation prevention ensures fairness
- Metrics enable optimization

#### Consequences
- Queue ordering overhead
- Persistence adds I/O
- Priority inversion possible

---

### ADR-023: Workflow Engine with DSL

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 3 - Skills, Tools & Orchestration

#### Context
Complex tasks require multi-step workflows with conditionals, loops, and parallelism.

#### Decision
Implement workflow engine with builder DSL:

```python
WorkflowBuilder()
    .step("generate", AgentType.CODER)
    .step("review", AgentType.REVIEWER)
    .conditional(
        lambda r: r.issues_count > 0,
        if_true=Step("fix", AgentType.FIXER),
        if_false=Step("complete", None)
    )
    .build()
```

**Control Flow**:
- Sequential steps
- Parallel execution
- Conditional branching
- Loop with condition

**Pre-built Templates**:
- CodeReviewWorkflow
- FeatureWorkflow
- RefactorWorkflow
- SecurityAuditWorkflow

#### Rationale
- DSL is readable and maintainable
- Templates accelerate common patterns
- Parallelism improves throughput
- State tracking enables pause/resume

#### Consequences
- DSL learning curve
- Complex error handling
- State persistence required

---

## Previous Phases (Reference)

### Phase 2 Decisions (ADR-016 to ADR-019)
- H-MEM Tiered Memory Architecture
- Multi-Provider LLM Strategy
- Semantic Search with Vector Embeddings
- Tool Calling Framework

### Phase 1 Decisions (ADR-012 to ADR-015)
- 20-Agent Architecture
- Hierarchical Agent Module Structure
- Agent Registry and Factory Pattern
- Agent Lifecycle Management System

### Initial Decisions (ADR-001 to ADR-011)
- Extension Over Modification
- Memory-First Architecture
- APEX Constitution Governance
- And more...

---

*Document maintained as part of APEX governance requirements*
