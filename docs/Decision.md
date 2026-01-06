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
| ADR-028 | Comprehensive Testing Strategy | ✅ Accepted | 5 | 2026-01-06 |
| ADR-029 | Security Module Architecture | ✅ Accepted | 5 | 2026-01-06 |
| ADR-030 | Automated Documentation Generation | ✅ Accepted | 5 | 2026-01-06 |
| ADR-031 | Prompt Injection Defense System | ✅ Accepted | 5 | 2026-01-06 |

---

## Phase 5 Decisions

### ADR-028: Comprehensive Testing Strategy

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 5 - Testing, Security & Documentation

#### Context
Enterprise-grade application requires thorough testing at multiple levels.

#### Decision
Implement 3-tier testing strategy:

| Level | Test Count | Coverage Target | Run Time |
|-------|------------|-----------------|----------|
| Unit | 37 files | 90% | < 2 min |
| Integration | 7 files | 80% | < 5 min |
| E2E | 5 files | 70% | < 10 min |

**Testing Stack**:
- pytest for Python tests
- pytest-asyncio for async tests
- pytest-cov for coverage
- Mock fixtures for LLM/external APIs

**Coverage Requirements**:
- Security module: 90% minimum
- Core agents: 85% minimum
- Overall: 80% minimum

#### Rationale
- Unit tests catch component issues early
- Integration tests verify component interaction
- E2E tests validate user workflows
- High security coverage is critical

#### Consequences
- Significant test code to maintain
- CI pipeline time increases
- Mock complexity for LLM tests

---

### ADR-029: Security Module Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 5 - Testing, Security & Documentation

#### Context
AI agents executing code and accessing files require robust security controls.

#### Decision
Implement comprehensive security module with 6 sub-domains:

| Domain | Files | Purpose |
|--------|-------|---------|
| Core | 3 | Security coordination |
| Scanning | 5 | Secret/vulnerability detection |
| Audit | 4 | Event logging and compliance |
| Auth | 4 | Authentication/authorization |
| Encryption | 3 | Data encryption |
| Validation | 4 | Input/output validation |

**Security Layers**:
1. **Input Validation**: Sanitize all inputs
2. **Permission Checks**: Verify capabilities before action
3. **Audit Logging**: Log all sensitive operations
4. **Output Validation**: Redact PII, validate format

#### Rationale
- Defense in depth approach
- Audit trail for compliance
- Encryption for sensitive data
- Validation prevents injection

#### Consequences
- Performance overhead for checks
- Storage for audit logs
- Key management complexity

---

### ADR-030: Automated Documentation Generation

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 5 - Testing, Security & Documentation

#### Context
Manual documentation becomes stale. Need automated generation from source.

#### Decision
Implement documentation generation system:

**Generators**:
| Generator | Input | Output |
|-----------|-------|--------|
| API Doc | Python modules | Markdown/HTML |
| Schema Doc | Pydantic models | Markdown |
| Agent Doc | Agent classes | Markdown |
| Tool Doc | Tool definitions | Markdown |
| OpenAPI | FastAPI routes | openapi.json |

**Documentation Structure**:
```
docs/
├── api/           # API reference (generated)
├── guides/        # User guides (manual)
├── architecture/  # Architecture specs (manual)
├── security/      # Security docs (semi-auto)
└── development/   # Dev docs (manual)
```

#### Rationale
- Auto-generation keeps docs current
- Consistent format across APIs
- Reduces documentation burden
- Single source of truth

#### Consequences
- Docstrings must be high quality
- Build step for doc generation
- Some manual content still needed

---

### ADR-031: Prompt Injection Defense System

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 5 - Testing, Security & Documentation

#### Context
LLM-based agents are vulnerable to prompt injection attacks via user input.

#### Decision
Implement multi-layer prompt injection defense:

**Defense Layers**:
1. **Detection**: Pattern matching for known injection attempts
2. **Sanitization**: Remove/escape dangerous patterns
3. **Delimiting**: Wrap user input with clear boundaries
4. **Validation**: Verify output doesn't contain injected instructions

**Implementation**:
```python
class PromptInjectionGuard:
    def check(self, input_text: str) -> ValidationResult
    def sanitize(self, input_text: str) -> str
    def wrap_user_input(self, input_text: str) -> str
    def validate_output(self, output: str) -> ValidationResult
```

**Detection Patterns**:
- "Ignore previous instructions"
- "You are now..."
- System prompt extraction attempts
- Delimiter escape attempts

#### Rationale
- LLM security is critical
- Multiple layers provide defense in depth
- Pattern evolution requires updates

#### Consequences
- False positives possible
- Pattern maintenance needed
- Performance overhead for checking

---

## Decision Summary by Phase

### Phase 1: Agent System (ADR-012 to ADR-015)
- 20-agent architecture (4 core + 16 enterprise)
- Hierarchical module structure
- Registry and factory patterns
- Lifecycle management

### Phase 2: Memory & LLM (ADR-016 to ADR-019)
- H-MEM tiered memory (L1/L2/L3)
- Multi-provider LLM strategy (7 providers)
- Semantic search with embeddings
- Tool calling framework

### Phase 3: Skills, Tools, Orchestration (ADR-020 to ADR-023)
- Skills framework (5 categories, 16 skills)
- Tool permission and sandbox system
- Priority TaskQueue (4 levels)
- Workflow engine with DSL

### Phase 4: UI, Integrations, Analytics (ADR-024 to ADR-027)
- Electron IPC architecture
- React component architecture (8 domains)
- Zustand state management
- Multi-platform integrations (5 platforms)

### Phase 5: Testing, Security, Documentation (ADR-028 to ADR-031)
- Comprehensive testing strategy
- Security module architecture
- Automated documentation generation
- Prompt injection defense

---

## Total Decisions: 31

| Category | Count |
|----------|-------|
| Foundational (ADR-001 to ADR-011) | 11 |
| Phase 1 - Agents | 4 |
| Phase 2 - Memory/LLM | 4 |
| Phase 3 - Skills/Tools/Orchestration | 4 |
| Phase 4 - UI/Integrations | 4 |
| Phase 5 - Testing/Security/Docs | 4 |

---

*Architecture Decision Records complete. All 31 decisions documented.*

*Document maintained as part of APEX governance requirements*
