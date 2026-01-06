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
| ADR-029 | Security Module Architecture | ⚠️ Superseded | 5 | 2026-01-06 |
| ADR-030 | Automated Documentation Generation | ✅ Accepted | 5 | 2026-01-06 |
| ADR-031 | Prompt Injection Defense System | ✅ Accepted | 5 | 2026-01-06 |
| ADR-032 | Phase 5/6 Security Deduplication | ✅ Accepted | 5/6 | 2026-01-06 |
| ADR-033 | LLM-Agnostic Security Architecture | ✅ Accepted | 6 | 2026-01-06 |
| ADR-034 | Multi-Provider Credential Vault | ✅ Accepted | 6 | 2026-01-06 |
| ADR-035 | RBAC with Provider Permissions | ✅ Accepted | 6 | 2026-01-06 |
| ADR-036 | Enterprise Agent Specialization | ✅ Accepted | 7 | 2026-01-06 |
| ADR-037 | Multi-Agent Task Decomposition | ✅ Accepted | 7 | 2026-01-06 |
| ADR-038 | Advanced Analytics Pipeline | ✅ Accepted | 8 | 2026-01-06 |
| ADR-039 | Extended Tool Categories | ✅ Accepted | 8 | 2026-01-06 |
| ADR-040 | Governance Engine Architecture | ✅ Accepted | 9 | 2026-01-06 |
| ADR-041 | Compliance Framework | ✅ Accepted | 9 | 2026-01-06 |
| ADR-042 | 10-Phase Architecture Strategy | ✅ Accepted | 10 | 2026-01-06 |
| ADR-043 | Extended Testing Patterns | ✅ Accepted | 10 | 2026-01-06 |
| ADR-044 | LLM-Agnostic Provider Equality | ✅ Accepted | All | 2026-01-06 |
| ADR-045 | Architecture Header Standardization | ✅ Accepted | QA | 2026-01-06 |
| ADR-046 | Naming Alignment Verification | ✅ Accepted | QA | 2026-01-06 |

---

## Phase 6 Decisions

### ADR-032: Phase 5/6 Security Deduplication

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 5/6 - Quality Review

#### Context
Original Phase 5 Architecture contained detailed security implementation that duplicated Phase 6's dedicated security content.

#### Decision
- **Phase 5** retains: Testing infrastructure, Documentation system
- **Phase 6** owns: Complete security module implementation (`apps/backend/security/`)
- Phase 5 references Phase 6 for security details rather than duplicating

#### Rationale
- Single source of truth for security implementation
- Clear separation of concerns
- Reduced maintenance burden

#### Consequences
- Phase 5 now titled "Testing & Documentation Architecture"
- Cross-reference added to Phase 5 pointing to Phase 6

---

### ADR-033: LLM-Agnostic Security Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 6 - Security Architecture

#### Context
Security must treat all 8 LLM providers equally without vendor lock-in.

#### Decision
Implement security with provider parity:

| Provider | Credentials Protected | Secrets Patterns |
|----------|----------------------|------------------|
| copilot | GITHUB_TOKEN | `gh[pousr]_*` |
| openrouter | OPENROUTER_API_KEY | `sk-or-*` |
| ollama | (local) | N/A |
| lmstudio | (local) | N/A |
| gemini | GOOGLE_API_KEY | `AIza*` |
| openai | OPENAI_API_KEY | `sk-*` |
| anthropic | ANTHROPIC_API_KEY | `sk-ant-*` |
| azure | AZURE_OPENAI_API_KEY | Context-based |

#### Rationale
- No provider treated as "primary"
- Equal security coverage across all providers
- Future provider additions follow same pattern

---

### ADR-034: Multi-Provider Credential Vault

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 6 - Security Architecture

#### Context
Multiple LLM providers require secure credential storage.

#### Decision
Implement `CredentialVault` class:
- AES-256-GCM encryption for all stored credentials
- Per-provider credential isolation
- Key rotation support
- User-scoped credential access

#### Rationale
- Enterprise-grade encryption
- Audit logging of credential access
- Support for local providers (no keys needed)

---

### ADR-035: RBAC with Provider Permissions

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 6 - Security Architecture

#### Context
Different users may have access to different LLM providers.

#### Decision
Add provider-specific permissions to RBAC:
```python
PROVIDER_PERMISSIONS = {
    "use_copilot", "use_openrouter", "use_ollama", "use_lmstudio",
    "use_gemini", "use_openai", "use_anthropic", "use_azure",
}
```

#### Rationale
- Cost control (expensive providers restricted)
- Compliance (some providers may be prohibited)
- Organization policy enforcement

---

## Phase 7 Decisions

### ADR-036: Enterprise Agent Specialization

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 7 - Enterprise Agents Architecture

#### Context
Beyond 4 core agents, enterprise needs specialized agents for complex workflows.

#### Decision
Add 16 enterprise agents:

| Category | Agents | Count |
|----------|--------|-------|
| Testing | TestWriter, TestExecutor, CoverageAnalyzer | 3 |
| DevOps | PipelineBuilder, DeploymentManager, InfraAgent | 3 |
| Analysis | SecurityAuditor, PerformanceAnalyzer, DependencyManager | 3 |
| Documentation | DocWriter, APIDocGenerator, ChangelogBuilder | 3 |
| Integration | GitHubAgent, GitLabAgent, LinearAgent, SlackAgent | 4 |

#### Rationale
- Specialized agents perform better than generalists
- Enterprise workflows require dedicated capabilities
- Parallel agent execution improves throughput

---

### ADR-037: Multi-Agent Task Decomposition

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 7 - Enterprise Agents Architecture

#### Context
Complex tasks need to be broken down for parallel agent execution.

#### Decision
Implement TaskDecomposer:
- Analyzes complex tasks
- Creates sub-tasks for specialized agents
- Manages dependencies between sub-tasks
- Aggregates results

#### Rationale
- Parallel execution improves speed
- Specialized agents improve quality
- Clear task boundaries

---

## Phase 8 Decisions

### ADR-038: Advanced Analytics Pipeline

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 8 - Analytics & Tools Architecture

#### Context
Enterprise needs detailed analytics on agent performance and project health.

#### Decision
Implement analytics system:
- Real-time metrics collection
- Agent performance tracking
- Project health dashboard
- Cost attribution per provider

#### Rationale
- Visibility into system performance
- Cost optimization opportunities
- Trend analysis for planning

---

### ADR-039: Extended Tool Categories

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 8 - Analytics & Tools Architecture

#### Context
Enterprise agents need additional specialized tools.

#### Decision
Add tool categories:
- Database tools (query, migrate)
- Cloud tools (deploy, scale)
- Monitoring tools (metrics, alerts)
- Communication tools (notify, webhook)

#### Rationale
- Comprehensive capability coverage
- Sandboxed execution for safety
- Extensible tool framework

---

## Phase 9 Decisions

### ADR-040: Governance Engine Architecture

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 9 - Governance Architecture

#### Context
APEX Constitution requires governance enforcement at runtime.

#### Decision
Implement Governance Engine:
- Policy evaluation engine
- Compliance checker
- Approval workflows
- Audit trail

#### Rationale
- Constitution enforcement is automatic
- Compliance is verifiable
- Governance is transparent

---

### ADR-041: Compliance Framework

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 9 - Governance Architecture

#### Context
Enterprise deployments require compliance certifications.

#### Decision
Support compliance frameworks:
- SOC 2 Type II readiness
- OWASP Top 10 coverage
- GDPR data handling
- Audit logging for compliance

#### Rationale
- Enterprise requirement
- Security audit readiness
- Trust establishment

---

## Phase 10 Decisions

### ADR-042: 10-Phase Architecture Strategy

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 10 - Testing & Documentation

#### Context
Original 5-phase plan was expanded to 10 phases for better separation of concerns.

#### Decision
Expand from 5 to 10 phases:

| Phase | Focus |
|-------|-------|
| 1 | Agent System |
| 2 | Memory & LLM |
| 3 | Skills, Tools, Orchestration |
| 4 | UI, Integrations, Analytics |
| 5 | Testing & Documentation |
| 6 | Security |
| 7 | Enterprise Agents |
| 8 | Analytics & Tools |
| 9 | Governance |
| 10 | Testing & Documentation (Extended) |

#### Rationale
- Better separation of concerns
- Clearer ownership per phase
- More focused implementation

---

### ADR-043: Extended Testing Patterns

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: 10 - Testing & Documentation

#### Context
Enterprise-grade system needs advanced testing patterns.

#### Decision
Add extended testing:
- Property-based testing
- Mutation testing
- Chaos testing
- Load testing

#### Rationale
- Higher confidence in system reliability
- Edge case discovery
- Performance validation

---

## Quality Review Decisions

### ADR-044: LLM-Agnostic Provider Equality

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: All Phases

#### Context
Quality review identified inconsistent provider representation across documents.

#### Decision
Standardize on 8 equal LLM providers:
```
copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
```

All architecture documents must treat providers equally:
- No "primary" or "fallback" language
- Equal mention in lists
- Same configuration structure

#### Rationale
- User choice is paramount
- Vendor neutrality
- Consistent user experience

---

### ADR-045: Architecture Header Standardization

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: Quality Review

#### Context
Phases 1-5 architecture files had headers saying "Phase X of 5" instead of "Phase X of 10".

#### Decision
- All architecture files must state "Phase X of 10"
- Quality review process added to verify headers
- Commit per file for clear history

#### Files Updated (Commits):
| File | Commit |
|------|--------|
| PHASE1_AGENT_SYSTEM_ARCHITECTURE.md | `3a29403` |
| PHASE2_MEMORY_LLM_ARCHITECTURE.md | `b4b6d61` |
| PHASE3_SKILLS_TOOLS_ORCHESTRATION_ARCHITECTURE.md | `2b28f67` |
| PHASE4_UI_INTEGRATIONS_ANALYTICS_ARCHITECTURE.md | `1b829fe` |
| PHASE5_TESTING_SECURITY_DOCUMENTATION_ARCHITECTURE.md | `41ae2f5` |

#### Rationale
- Consistency across documentation
- Accurate phase count for planning
- Clear scope communication

---

### ADR-046: Naming Alignment Verification

**Status**: ✅ Accepted  
**Date**: 2026-01-06  
**Phase**: Quality Review - Priority 3

#### Context
NAMING_ALIGNMENT_STANDARDS.md established canonical naming conventions. All architecture files needed verification against these standards.

#### Decision
Systematic verification of all 10 phase architecture files:

**8 Canonical LLM Providers**:
```
copilot | openrouter | ollama | lmstudio | gemini | openai | anthropic | azure
```

**Key Naming Rule**: Use `gemini` for Google's LLM product, `google` only for OAuth authentication.

#### Verification Results

| Phase | File | Status | Issues Found |
|-------|------|--------|--------------|
| 1 | PHASE1_AGENT_SYSTEM_ARCHITECTURE.md | ✅ Compliant | None |
| 2 | PHASE2_MEMORY_LLM_ARCHITECTURE.md | ✅ Fixed | `google_provider.py` → `gemini_provider.py`, `google_embedder.py` → `gemini_embedder.py`, LLMProvider enum corrected |
| 3 | PHASE3_SKILLS_TOOLS_ORCHESTRATION_ARCHITECTURE.md | ✅ Compliant | None |
| 4 | PHASE4_UI_INTEGRATIONS_ANALYTICS_ARCHITECTURE.md | ✅ Compliant | None |
| 5 | PHASE5_TESTING_SECURITY_DOCUMENTATION_ARCHITECTURE.md | ✅ Compliant | None |
| 6 | PHASE6_SECURITY_ARCHITECTURE.md | ✅ Compliant | None |
| 7 | PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md | ✅ Compliant | None |
| 8 | PHASE8_ANALYTICS_TOOLS_ARCHITECTURE.md | ✅ Compliant | None |
| 9 | PHASE9_GOVERNANCE_ARCHITECTURE.md | ✅ Compliant | None |
| 10 | PHASE10_TESTING_DOCUMENTATION_ARCHITECTURE.md | ✅ Compliant | None |

#### Phase 2 Fixes Applied (Commit: `c6dcfea`)
1. **File Naming**:
   - `google_provider.py` → `gemini_provider.py`
   - `google_embedder.py` → `gemini_embedder.py`
   - Added `copilot_provider.py`, `lmstudio_provider.py`
   - Added `openrouter_embedder.py`

2. **LLMProvider Enum Corrected**:
```python
# Before (incorrect)
class LLMProvider(Enum):
    GOOGLE = "google"  # Wrong
    GROQ = "groq"      # Not in canonical 8

# After (correct)
class LLMProvider(Enum):
    COPILOT = "copilot"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    GEMINI = "gemini"      # Correct
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
```

3. **Cross-Reference Added**: Link to NAMING_ALIGNMENT_STANDARDS.md

#### Implementation Specs Status
- `docs/specs/` folder: Empty (specs inline in architecture files)
- All specs content embedded in respective architecture documents

#### Rationale
- Ensures consistency with NAMING_ALIGNMENT_STANDARDS.md
- Prevents confusion between `google` (OAuth) and `gemini` (LLM)
- All 8 providers represented equally

#### Consequences
- Phase 2 architecture file updated with correct naming
- Clear separation: `gemini` = LLM, `google` = OAuth only
- All phases verified naming-compliant

---

## Decision Summary by Phase

### Foundational (ADR-001 to ADR-011)
- Extension over modification
- Memory-first architecture
- TaskQueue prioritization
- AgentPool concurrency
- SQLite episodic memory
- Electron IPC bridge
- React Kanban visualization
- Git worktrees isolation
- APEX Constitution governance
- Phased implementation
- APEXDEV_MERGE branch strategy

### Phase 1: Agent System (ADR-012 to ADR-015)
- 20-agent architecture (4 core + 16 enterprise)
- Hierarchical module structure
- Registry and factory patterns
- Lifecycle management

### Phase 2: Memory & LLM (ADR-016 to ADR-019)
- H-MEM tiered memory (L1/L2/L3)
- Multi-provider LLM strategy (8 providers)
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

### Phase 5: Testing & Documentation (ADR-028, ADR-030, ADR-031)
- Comprehensive testing strategy
- Automated documentation generation
- Prompt injection defense
- ⚠️ ADR-029 superseded by ADR-032

### Phase 6: Security (ADR-032 to ADR-035)
- Phase 5/6 deduplication
- LLM-agnostic security
- Multi-provider credential vault
- RBAC with provider permissions

### Phase 7: Enterprise Agents (ADR-036 to ADR-037)
- Enterprise agent specialization (16 agents)
- Multi-agent task decomposition

### Phase 8: Analytics & Tools (ADR-038 to ADR-039)
- Advanced analytics pipeline
- Extended tool categories

### Phase 9: Governance (ADR-040 to ADR-041)
- Governance engine architecture
- Compliance framework

### Phase 10: Testing & Documentation Extended (ADR-042 to ADR-043)
- 10-phase architecture strategy
- Extended testing patterns

### Quality Review (ADR-044 to ADR-046)
- LLM-agnostic provider equality
- Architecture header standardization
- Naming alignment verification

---

## Total Decisions: 46

| Category | Count |
|----------|-------|
| Foundational (ADR-001 to ADR-011) | 11 |
| Phase 1 - Agents | 4 |
| Phase 2 - Memory/LLM | 4 |
| Phase 3 - Skills/Tools/Orchestration | 4 |
| Phase 4 - UI/Integrations | 4 |
| Phase 5 - Testing/Docs | 3 |
| Phase 6 - Security | 4 |
| Phase 7 - Enterprise Agents | 2 |
| Phase 8 - Analytics/Tools | 2 |
| Phase 9 - Governance | 2 |
| Phase 10 - Extended Testing | 2 |
| Quality Review | 3 |
| **TOTAL** | **46** |

---

*Architecture Decision Records complete. All 46 decisions documented.*

*Document maintained as part of APEX governance requirements*
