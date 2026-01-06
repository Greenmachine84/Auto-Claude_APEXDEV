# Decision Log

> **Auto-Claude_APEXDEV Enhancement Plan** - Architectural Decision Records (ADR)
> 
> This document captures key decisions, rationales, and trade-offs for the DEVAPEX feature integration into Auto-Claude.

---

## Document Info

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2026-01-05 |
| **Last Updated** | 2026-01-05 |
| **Status** | Active |
| **Source Repositories** | [DEVAPEX (dev/v2.0-multi-llm)](https://github.com/Greenmachine84/DEVAPEX/tree/dev/v2.0-multi-llm), [Auto-Claude_APEXDEV](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/tree/APEXDEV_MERGE) |

---

## Table of Contents

1. [ADR-001: Core Repository Selection](#adr-001-core-repository-selection)
2. [ADR-002: Integration Strategy](#adr-002-integration-strategy)
3. [ADR-003: Memory System Architecture](#adr-003-memory-system-architecture)
4. [ADR-004: Task Orchestration Model](#adr-004-task-orchestration-model)
5. [ADR-005: Multi-LLM Provider Support](#adr-005-multi-llm-provider-support)
6. [ADR-006: Kanban UI Integration](#adr-006-kanban-ui-integration)
7. [ADR-007: Agent Pool Management](#adr-007-agent-pool-management)
8. [ADR-008: APEX Governance Compliance](#adr-008-apex-governance-compliance)
9. [ADR-009: Enterprise Features Selection](#adr-009-enterprise-features-selection)
10. [ADR-010: Security Model Harmonization](#adr-010-security-model-harmonization)
11. [ADR-011: Merge Strategy and Testing](#adr-011-merge-strategy-and-testing)

---

## ADR-001: Core Repository Selection

### Context

Two repositories need harmonization:
- **Auto-Claude_APEXDEV** (APEXDEV_MERGE branch) - Production-ready autonomous coding framework
- **DEVAPEX** (dev/v2.0-multi-llm branch) - Enterprise platform with enhanced features

### Decision

**Use Auto-Claude_APEXDEV as the core base, incorporating DEVAPEX features as additive enhancements.**

### Rationale

1. **Production Stability**: Auto-Claude v2.7.2 is a proven, released product with active users
2. **APEX Principle M1.2.1**: "All enhancements are ADDITIVE" - aligns with extension philosophy
3. **User Expectations**: Auto-Claude users expect compatibility with existing workflows
4. **Claude SDK Integration**: Auto-Claude uses Claude Agent SDK as its foundation - critical to preserve

### Consequences

- DEVAPEX features must be adapted to Auto-Claude's architecture
- Some DEVAPEX patterns may need modification for compatibility
- Testing burden increases to ensure existing features remain functional

### Status: APPROVED

---

## ADR-002: Integration Strategy

### Context

Determining how to merge DEVAPEX's 27+ backend modules into Auto-Claude's existing structure.

### Decision

**Phased additive integration with feature toggles:**

```
Phase 1: Task Orchestration (TaskQueue, AgentPool, Orchestrator)
Phase 2: Memory Enhancement (Episodic Memory, Semantic Search)
Phase 3: Enterprise Features (Projects, Secrets, Teams)
Phase 4: UI/UX (Kanban Board, Terminal Grid enhancements)
Phase 5: Integration Testing & Validation
```

### Rationale

1. **Risk Mitigation**: Phased approach limits blast radius of issues
2. **User Verification**: Each phase can be validated before proceeding
3. **Rollback Capability**: Feature toggles allow disabling problematic additions
4. **APEX Part 14**: Event Bus Architecture supports modular integration

### Implementation

```python
# Feature flags in config
DEVAPEX_FEATURES = {
    "task_queue": True,
    "agent_pool": True,
    "episodic_memory": True,
    "multi_llm": False,  # Phase 2
    "enterprise_teams": False,  # Phase 3
}
```

### Status: APPROVED

---

## ADR-003: Memory System Architecture

### Context

Auto-Claude has Graphiti Memory with LadybugDB. DEVAPEX has SQLite-based episodic memory with semantic search.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| Keep Graphiti only | Minimal change | Missing episode structure |
| Replace with DEVAPEX SQLite | Unified system | Lose Graphiti graph queries |
| **Hybrid approach** | Best of both | Complexity |

### Decision

**Hybrid memory architecture:**

1. **Preserve Graphiti** for semantic search and knowledge graphs
2. **Add EpisodeRecord layer** for agent interaction tracking
3. **Unified search API** that queries both stores

### Implementation

```python
# apps/backend/memory/unified.py
class UnifiedMemory:
    def __init__(self, graphiti: GraphitiMemory, episodes: EpisodeStore):
        self.graphiti = graphiti
        self.episodes = episodes
    
    async def search(self, query: str, limit: int = 10):
        """Search both stores, merge and rank results."""
        graphiti_results = await self.graphiti.search(query)
        episode_results = await self.episodes.search(query)
        return self._merge_ranked(graphiti_results, episode_results, limit)
    
    async def store_episode(self, agent_id: str, input_text: str, 
                           output: str, tools_used: list):
        """Store agent interaction as episode."""
        episode = EpisodeRecord(
            agent_id=agent_id,
            input_text=input_text,
            output=output,
            tools_used=tools_used,
            timestamp=datetime.now()
        )
        await self.episodes.store(episode)
        # Also extract and store patterns in Graphiti
        patterns = extract_patterns(output)
        for pattern in patterns:
            await self.graphiti.add_pattern(pattern)
```

### References

- DEVAPEX: `apps/backend/devapex/memory/`
- Auto-Claude: `apps/backend/integrations/graphiti/`
- APEX Part 1: Episodic Memory Architecture

### Status: APPROVED

---

## ADR-004: Task Orchestration Model

### Context

DEVAPEX has a sophisticated TaskQueue + AgentPool + Orchestrator pattern. Auto-Claude uses direct agent invocation through spec_runner and run.py.

### Decision

**Adopt DEVAPEX orchestration as an optional layer:**

```
Existing Flow (preserve):
  User → spec_runner.py → agent.py → Claude SDK

New Enhanced Flow (additive):
  User → Kanban UI → TaskQueue → Orchestrator → AgentPool → agent.py → Claude SDK
```

### Priority System

From DEVAPEX `orchestrator/manager.py`:

```python
class TaskPriority(IntEnum):
    CRITICAL = 0   # Security fixes, blocking issues
    HIGH = 1       # User-facing features
    MEDIUM = 2     # Technical debt, refactoring
    LOW = 3        # Nice-to-have improvements
```

### Agent Pool Design

```python
class AgentPoolConfig:
    max_agents: int = 12           # Match terminal grid
    max_concurrent_tasks: int = 6  # Prevent resource exhaustion
    idle_timeout_seconds: int = 300
    agent_types: list[str] = ["coder", "reviewer", "fixer"]
```

### Rationale

1. **Parallel Execution**: Enables multi-build scenarios from Kanban
2. **Resource Management**: Prevents overloading the system
3. **Backward Compatibility**: CLI still works without orchestrator

### Status: APPROVED

---

## ADR-005: Multi-LLM Provider Support

### Context

DEVAPEX v2.0 supports OpenAI, Anthropic, Google Gemini, and Ollama. Auto-Claude is primarily Claude-focused via Claude Agent SDK.

### Decision

**Implement LLM Router with Claude as primary, others as fallback/specialized:**

```python
class LLMRouter:
    providers = {
        "anthropic": AnthropicProvider(),  # Primary - Claude Sonnet/Opus
        "openai": OpenAIProvider(),        # Fallback - GPT-4o
        "ollama": OllamaProvider(),        # Local - Llama, Mistral
        "google": GeminiProvider(),        # Optional - Gemini Flash
    }
    
    async def route(self, task, preferences):
        # Claude for core autonomous work
        if task.type in ["coding", "review", "planning"]:
            return await self.providers["anthropic"].complete(task)
        
        # Use routing strategy for other tasks
        provider = self._select_provider(task, preferences)
        return await provider.complete(task)
```

### Provider Selection Criteria

| Provider | Use Case | Thinking Support |
|----------|----------|------------------|
| Claude (Anthropic) | Core coding, QA | ultrathink ✓ |
| GPT-4o (OpenAI) | Fast iterations, embeddings | chain-of-thought |
| Ollama (Local) | Privacy-sensitive, offline | model-dependent |
| Gemini (Google) | Research, long context | standard |

### Rationale

1. **Claude SDK Preservation**: Core Auto-Claude identity maintained
2. **Cost Optimization**: Route simpler tasks to cheaper models
3. **Fallback Resilience**: System works if one provider is down

### Status: APPROVED (Phase 2)

---

## ADR-006: Kanban UI Integration

### Context

DEVAPEX includes React Kanban components from Vibe Kanban. Auto-Claude has a basic Kanban board.

### Decision

**Enhance existing Kanban with DEVAPEX patterns:**

1. Add task priority indicators (Critical/High/Medium/Low colors)
2. Integrate task-to-agent linking (show which agent is working on task)
3. Add memory/context viewer panel for selected tasks
4. Implement drag-drop status updates with API calls

### UI State Flow

```typescript
// Kanban task tied to orchestrator
interface KanbanTask {
  id: string;
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'todo' | 'in_progress' | 'in_review' | 'done';
  assignedAgent?: AgentInfo;
  episodeHistory?: Episode[];
  specId?: string;
}
```

### Rationale

1. **Visual Clarity**: Priority colors improve task scanning
2. **Agent Visibility**: Users see which agents are active
3. **Memory Access**: Context/history available without leaving board

### Status: APPROVED (Phase 4)

---

## ADR-007: Agent Pool Management

### Context

DEVAPEX manages agent instances in a pool with reuse and spawning logic. Auto-Claude spawns agent sessions directly.

### Decision

**Implement AgentPool with configurable limits:**

```python
class AgentPool:
    """Manages agent lifecycle and resource allocation."""
    
    def __init__(self, config: AgentPoolConfig):
        self.config = config
        self.agents: dict[str, AgentInstance] = {}
        self.active_tasks: dict[str, str] = {}  # task_id → agent_id
    
    async def acquire(self, agent_type: str) -> AgentInstance:
        """Get or create an agent instance."""
        # Check for idle agent of this type
        idle = self._find_idle_agent(agent_type)
        if idle:
            return idle
        
        # Create new if under limit
        if len(self.agents) < self.config.max_agents:
            return await self._create_agent(agent_type)
        
        # Wait for agent to become available
        return await self._wait_for_available(agent_type)
    
    async def release(self, agent_id: str):
        """Return agent to pool."""
        agent = self.agents.get(agent_id)
        if agent:
            agent.status = AgentStatus.IDLE
            agent.last_used = datetime.now()
```

### Configuration Alignment

From Auto-Claude's 12-terminal grid:

```python
DEFAULT_POOL_CONFIG = AgentPoolConfig(
    max_agents=12,           # Matches terminal grid
    max_concurrent_tasks=6,  # Conservative for stability
    idle_timeout_seconds=300,
)
```

### Status: APPROVED

---

## ADR-008: APEX Governance Compliance

### Context

DEVAPEX enforces APEX Constitution rules. Auto-Claude needs compatible governance.

### Decision

**Adopt APEX governance principles:**

| APEX Part | Implementation |
|-----------|----------------|
| Part 1 - Episodic Memory | Unified Memory with episodes |
| Part 5 - Long-Running Harness | AgentPool with lifecycle |
| Part 7 - Dynamic Selection | Agent routing by task type |
| Part 11 - Implementation Patterns | Phased integration |
| Part 13 - Security Guardrails | Enhanced security hooks |
| Part 14 - Event Bus | Orchestrator events |

### Governance Rules to Implement

```python
class ApexGovernance:
    """APEX compliance validator."""
    
    rules = {
        "M1.1.1": "Architect folder is IMMUTABLE",
        "M1.2.1": "All enhancements are ADDITIVE",
        "M2.1": "Memory-First operation",
    }
    
    def validate_change(self, path: str, operation: str) -> bool:
        if path.startswith("Architect/") and operation != "read":
            raise ApexViolation("M1.1.1: Cannot modify Architect folder")
        return True
```

### Status: APPROVED

---

## ADR-009: Enterprise Features Selection

### Context

DEVAPEX v2.0 includes Projects, Secrets, Teams, OAuth. Determine which to include.

### Decision

**Selective adoption with prioritization:**

| Feature | Priority | Include | Rationale |
|---------|----------|---------|------------|
| Projects Manager | High | ✅ Yes | Improves project lifecycle |
| Secrets Manager | High | ✅ Yes | Security requirement |
| Teams Collaboration | Medium | ⏳ Phase 3 | Requires OAuth first |
| OAuth (Google/GitHub/MS) | Medium | ⏳ Phase 3 | Complex integration |
| Auto-Updates | Low | ❌ No | Already implemented |

### Secrets Management Design

From DEVAPEX `secrets/manager.py`:

```python
class SecretScope(Enum):
    USER = "user"           # Personal API keys
    PROJECT = "project"     # Project-specific secrets
    GLOBAL = "global"       # Shared across projects

class SecretsManager:
    async def store(self, name: str, value: str, 
                   scope: SecretScope, owner_id: str):
        encrypted = self._encrypt(value, self.master_key)
        # Store with audit trail
        ...
```

### Status: APPROVED

---

## ADR-010: Security Model Harmonization

### Context

Both systems have security layers. Need unified approach.

### Auto-Claude Security (Current)

1. OS Sandbox - Bash command isolation
2. Filesystem Permissions - Project directory only
3. Command Allowlist - Dynamic from project analysis

### DEVAPEX Security (To Add)

1. Secret Encryption - PBKDF2 + Fernet
2. Scoped Access Control - User/Team/Project/Enterprise
3. Audit Trails - Complete action logging

### Decision

**Layer DEVAPEX security on top of Auto-Claude's:**

```python
class SecurityLayer:
    """Unified security with Auto-Claude base + DEVAPEX enhancements."""
    
    def __init__(self):
        # Auto-Claude base
        self.command_allowlist = DynamicAllowlist()
        self.filesystem_guard = FilesystemGuard()
        
        # DEVAPEX additions
        self.secrets_manager = SecretsManager()
        self.audit_logger = AuditLogger()
    
    async def validate_operation(self, operation: Operation) -> bool:
        # Auto-Claude checks
        if not self.command_allowlist.is_allowed(operation.command):
            return False
        if not self.filesystem_guard.is_allowed(operation.path):
            return False
        
        # DEVAPEX checks
        if operation.requires_secret:
            if not await self.secrets_manager.can_access(
                operation.secret_id, operation.user_id
            ):
                return False
        
        # Log for audit
        await self.audit_logger.log(operation)
        return True
```

### Status: APPROVED

---

## ADR-011: Merge Strategy and Testing

### Context

Defining how to safely merge DEVAPEX features without breaking Auto-Claude.

### Decision

**Branch-based integration with staged merging:**

```
APEXDEV_MERGE (working branch)
    ↓ Feature additions
    ↓ Unit tests pass
    ↓ Integration tests pass
    ↓ User verification
develop (main development)
    ↓ Full regression
main (stable release)
```

### Testing Requirements

| Phase | Test Type | Coverage Target |
|-------|-----------|----------------|
| Pre-merge | Unit tests | 80% new code |
| Pre-merge | Integration tests | All APIs |
| Post-merge | Regression tests | Full suite |
| Post-merge | E2E tests | Critical flows |

### Merge Validation Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] No regression in existing features
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] User verification sign-off
- [ ] No APEX governance violations

### Status: APPROVED

---

## Decision Summary

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Auto-Claude as core, DEVAPEX additive | ✅ Approved |
| ADR-002 | Phased integration with toggles | ✅ Approved |
| ADR-003 | Hybrid Graphiti + Episode memory | ✅ Approved |
| ADR-004 | Optional orchestration layer | ✅ Approved |
| ADR-005 | Claude primary, multi-LLM fallback | ✅ Approved |
| ADR-006 | Enhanced Kanban with priorities | ✅ Approved |
| ADR-007 | Agent pool with 12-agent limit | ✅ Approved |
| ADR-008 | APEX governance compliance | ✅ Approved |
| ADR-009 | Selective enterprise features | ✅ Approved |
| ADR-010 | Layered security model | ✅ Approved |
| ADR-011 | Branch-based staged merge | ✅ Approved |

---

## References

- [DEVAPEX Architecture Specification](https://github.com/Greenmachine84/DEVAPEX/blob/dev/v2.0-multi-llm/docs/planning/ARCHITECTURE-SPECIFICATION.md)
- [DEVAPEX Auto-Claude Integration Plan](https://github.com/Greenmachine84/DEVAPEX/blob/dev/v2.0-multi-llm/docs/planning/AUTO-CLAUDE-INTEGRATION-PLAN.md)
- [Auto-Claude CLAUDE.md](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/blob/APEXDEV_MERGE/CLAUDE.md)
- [APEX Constitution](https://github.com/Greenmachine84/DEVAPEX/blob/dev/v2.0-multi-llm/integration/APEX-AGENTS-INTEGRATION-CONSTITUTION.md)

---

## Change Log

| Date | Version | Changes |
|------|---------|----------|
| 2026-01-05 | 1.0.0 | Initial decision log created |
