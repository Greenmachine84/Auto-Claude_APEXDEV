# Decision Log

> **Auto-Claude_APEXDEV Enhancement Plan** - Architectural Decision Records (ADR)
> 
> This document captures key decisions, rationales, and trade-offs for the DEVAPEX feature integration into Auto-Claude.

---

## Document Info

| Field | Value |
|-------|-------|
| **Version** | 3.0.0 |
| **Created** | 2026-01-05 |
| **Last Updated** | 2026-01-06 |
| **Status** | Active |
| **Source Repositories** | [DEVAPEX (dev/v2.0-multi-llm)](https://github.com/Greenmachine84/DEVAPEX/tree/dev/v2.0-multi-llm), [Auto-Claude_APEXDEV](https://github.com/Greenmachine84/Auto-Claude_APEXDEV/tree/APEXDEV_MERGE) |

---

## Table of Contents

1. [ADR-001: Core Repository Selection](#adr-001-core-repository-selection)
2. [ADR-002: Integration Strategy](#adr-002-integration-strategy)
3. [ADR-003: Memory System Architecture](#adr-003-memory-system-architecture)
4. [ADR-004: Task Orchestration Model](#adr-004-task-orchestration-model)
5. [ADR-005: LLM-Agnostic Architecture](#adr-005-llm-agnostic-architecture) ⚠️ CRITICAL
6. [ADR-006: Kanban UI Integration](#adr-006-kanban-ui-integration)
7. [ADR-007: Agent Pool Management](#adr-007-agent-pool-management)
8. [ADR-008: APEX Governance Compliance](#adr-008-apex-governance-compliance)
9. [ADR-009: Enterprise Features Selection](#adr-009-enterprise-features-selection)
10. [ADR-010: Security Model Harmonization](#adr-010-security-model-harmonization)
11. [ADR-011: Merge Strategy and Testing](#adr-011-merge-strategy-and-testing)
12. [ADR-012: Multi-Provider Authentication](#adr-012-multi-provider-authentication) ⚠️ CRITICAL
13. [ADR-013: Per-Agent LLM Configuration](#adr-013-per-agent-llm-configuration) ⚠️ CRITICAL
14. [ADR-014: World-Class Quality Standards](#adr-014-world-class-quality-standards) ⚠️ NEW

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
4. **Foundation Preservation**: Core architecture is preserved while becoming LLM-agnostic

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

**Phased additive integration with feature toggles over 10 phases (20 weeks):**

```
Phase 1: Foundation (Weeks 1-2)
Phase 2: LLM-Agnostic Layer (Weeks 3-4) ← CRITICAL
Phase 3: Authentication (Weeks 5-6) ← CRITICAL
Phase 4: Orchestration (Weeks 7-8)
Phase 5: Memory Enhancement (Weeks 9-10)
Phase 6: Security (Weeks 11-12)
Phase 7: Enterprise Agents (Weeks 13-14)
Phase 8: Analytics &amp; Tools (Weeks 15-16)
Phase 9: Governance (Weeks 17-18)
Phase 10: Testing &amp; Documentation (Weeks 19-20)
```

### Phase Specification Files

| Phase | Specification File |
|-------|-------------------|
| 1 | `docs/specs/phase-01-foundation.md` |
| 2 | `docs/specs/phase-02-llm-agnostic.md` |
| 3 | `docs/specs/phase-03-authentication.md` |
| 4 | `docs/specs/phase-04-orchestration.md` |
| 5 | `docs/specs/phase-05-memory.md` |
| 6 | `docs/specs/phase-06-security.md` |
| 7 | `docs/specs/phase-07-enterprise-agents.md` |
| 8 | `docs/specs/phase-08-analytics-tools.md` |
| 9 | `docs/specs/phase-09-governance.md` |
| 10 | `docs/specs/phase-10-testing-docs.md` |

### Rationale

1. **Risk Mitigation**: Phased approach limits blast radius of issues
2. **User Verification**: Each phase can be validated before proceeding
3. **Rollback Capability**: Feature toggles allow disabling problematic additions
4. **LLM-First Priority**: Phases 2-3 prioritize LLM agnosticism and authentication

### Implementation

```python
# Feature flags in config
DEVAPEX_FEATURES = {
    "llm_agnostic": True,          # Phase 2 - CRITICAL
    "multi_auth": True,            # Phase 3 - CRITICAL
    "task_queue": True,            # Phase 4
    "agent_pool": True,            # Phase 4
    "episodic_memory": True,       # Phase 5
    "enterprise_agents": False,    # Phase 7
    "enterprise_teams": False,     # Optional
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
4. **Multi-provider embeddings** for all 8 LLM providers

### Reference

See `docs/specs/phase-05-memory.md` for complete specification.

### Status: APPROVED

---

## ADR-004: Task Orchestration Model

### Context

DEVAPEX has a sophisticated TaskQueue + AgentPool + Orchestrator pattern. Auto-Claude uses direct agent invocation through spec_runner and run.py.

### Decision

**Adopt DEVAPEX orchestration as an optional layer with per-task LLM override:**

```
Existing Flow (preserve):
  User → spec_runner.py → agent.py → Claude SDK

New Enhanced Flow (additive):
  User → Kanban UI → TaskQueue → Orchestrator → AgentPool → agent.py → LLM Router
```

### Reference

See `docs/specs/phase-04-orchestration.md` for complete specification.

### Status: APPROVED

---

## ADR-005: LLM-Agnostic Architecture

> ⚠️ **CRITICAL ADR** - Defines core architectural principle

### Context

The current system relies heavily on Anthropic/Claude. Users need complete control over their LLM providers, and the system must be **provider-agnostic**.

### Problem Statement

1. Users want to choose their own LLM providers
2. Different agents may benefit from different models
3. Cost optimization requires routing to appropriate providers
4. Vendor lock-in prevents adoption by organizations with existing provider contracts

### Decision

**Implement a fully LLM-agnostic architecture with NO default provider.**

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **No Default Provider** | Users explicitly configure their preferred provider(s) |
| **Provider Abstraction** | All LLM calls through unified `LLMProvider` interface |
| **Per-Agent Config** | Each agent can use a different provider/model |
| **Equal Priority** | All 8 providers are equal - no "primary" or "fallback" |
| **Hot-Swappable** | Providers can be changed at runtime |
| **Graceful Failover** | Automatic failover based on user-defined chain |

### Supported LLM Providers (8 Equal Providers)

| Provider | Models | Configuration |
|----------|--------|---------------|
| **Copilot** | Copilot models via VS Code LM API | GitHub login |
| **OpenRouter** | 100+ models (OpenAI, Claude, Llama, Mistral, etc.) | API key |
| **Ollama** | Llama, Mistral, CodeLlama, local models | Local endpoint |
| **LMStudio** | Local models via OpenAI-compatible API | Local endpoint |
| **Gemini** | Gemini Pro, Ultra, Flash | API key |
| **OpenAI** | GPT-4, GPT-4o, GPT-4o-mini, o1 | API key |
| **Anthropic** | Claude 3 Opus, Sonnet, Haiku | API key |
| **Azure** | Azure-hosted OpenAI models | API key + endpoint |

### Architecture

```python
from abc import ABC, abstractmethod
from typing import List, Dict

SUPPORTED_PROVIDERS = [
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
]

class LLMProvider(ABC):
    """Abstract base class for ALL LLM providers - no favorites."""
    
    @abstractmethod
    async def complete(self, messages: List[Message], **kwargs) -> Response:
        """Generate completion - provider agnostic."""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models for this provider."""
        pass


class LLMRouter:
    """Route requests to user-configured providers. NO DEFAULT."""
    
    def __init__(self, providers: Dict[str, LLMProvider]):
        self.providers = providers  # User-configured only
        # NO default_provider attribute
    
    async def route(self, task: Task, agent_config: AgentLLMConfig) -> Response:
        """Route to agent's configured provider."""
        provider_id = agent_config.provider
        if not provider_id:
            raise ValueError("Provider is required - no default provider")
        
        provider = self.providers.get(provider_id)
        if not provider:
            raise ProviderNotConfigured(f"Provider '{provider_id}' not configured")
        
        return await provider.complete(task.messages)
```

### Reference

See `docs/specs/phase-02-llm-agnostic.md` for complete specification.

### Status: APPROVED (Critical Priority)

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
5. **Add LLM provider configuration UI**
6. **Add login/authentication screen for 4 providers**

### Status: APPROVED (Phase 4)

---

## ADR-007: Agent Pool Management

### Context

DEVAPEX manages agent instances in a pool with reuse and spawning logic. Auto-Claude spawns agent sessions directly.

### Decision

**Implement AgentPool with configurable limits and LLM-agnostic routing:**

```python
class AgentPool:
    """Manages agent lifecycle and resource allocation."""
    
    def __init__(self, config: AgentPoolConfig, llm_router: LLMRouter):
        self.config = config
        self.llm_router = llm_router  # LLM-agnostic router
        self.agents: dict[str, AgentInstance] = {}
    
    async def acquire(self, agent_type: str, llm_config: AgentLLMConfig) -> AgentInstance:
        """Get or create an agent instance with specified LLM config."""
        # Each agent has its own LLM provider configuration
        pass
```

### Status: APPROVED

---

## ADR-008: APEX Governance Compliance

### Context

DEVAPEX enforces APEX Constitution rules. Auto-Claude needs compatible governance.

### Decision

**Adopt APEX governance principles with LLM-agnostic policies:**

| APEX Part | Implementation |
|-----------|----------------|
| Part 1 - Episodic Memory | Unified Memory with episodes |
| Part 5 - Long-Running Harness | AgentPool with lifecycle |
| Part 7 - Dynamic Selection | Agent routing by task type |
| Part 11 - Implementation Patterns | Phased integration |
| Part 13 - Security Guardrails | Enhanced security hooks |
| Part 14 - Event Bus | Orchestrator events |

### Reference

See `docs/specs/phase-09-governance.md` for complete specification.

### Status: APPROVED

---

## ADR-009: Enterprise Features Selection

### Context

DEVAPEX v2.0 includes Projects, Secrets, Teams, OAuth. Determine which to include.

### Decision

**Selective adoption with prioritization:**

| Feature | Priority | Include | Rationale |
|---------|----------|---------|-----------|
| **Multi-Auth (OAuth)** | Critical | ✅ Yes | Core requirement |
| **LLM Providers (8)** | Critical | ✅ Yes | Core requirement |
| Projects Manager | High | ✅ Yes | Improves project lifecycle |
| Secrets Manager | High | ✅ Yes | Security requirement |
| Teams Collaboration | Medium | ⏳ Phase 7+ | After auth complete |
| Auto-Updates | Low | ✅ Enhance | Already implemented |

### Status: APPROVED

---

## ADR-010: Security Model Harmonization

### Context

Both systems have security concerns. Need unified approach.

### Decision

**Unified security with multi-provider credential management:**

1. **Multi-Provider Credential Vault** - Encrypted storage for all 8 LLM provider credentials
2. **Provider-Specific Secret Scanning** - Detect leaked API keys for each provider
3. **Per-Provider Rate Limiting** - Different limits per provider
4. **Per-Provider Quota Management** - Cost caps per provider
5. **Comprehensive Audit Logging** - Track all provider interactions

### Reference

See `docs/specs/phase-06-security.md` for complete specification.

### Status: APPROVED

---

## ADR-011: Merge Strategy and Testing

### Context

Merging DEVAPEX features requires comprehensive testing.

### Decision

**Test-first integration with 90%+ coverage:**

1. **Unit Tests**: Test each component in isolation
2. **Integration Tests**: Test all 8 LLM providers, all 4 auth providers
3. **E2E Tests**: Complete user journeys
4. **Acceptance Tests**: AT-X.1 through AT-X.10 per phase (100 total)

### Reference

See `docs/specs/phase-10-testing-docs.md` for complete specification.

### Status: APPROVED

---

## ADR-012: Multi-Provider Authentication

> ⚠️ **CRITICAL ADR** - Defines authentication architecture

### Context

Users need to authenticate via multiple providers to access the platform.

### Decision

**Support 4 equal authentication providers:**

| Provider | Method | Configuration |
|----------|--------|---------------|
| **GitHub** | OAuth 2.0 | Client ID/Secret |
| **Google** | OAuth 2.0 | Client ID/Secret |
| **Microsoft** | OAuth 2.0 (MSAL) | Client ID/Secret |
| **Manual** | Email + Password | Local database |

### Architecture

```python
class AuthProvider(Enum):
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    MANUAL = "manual"


class AuthService:
    """Multi-provider authentication service."""
    
    SUPPORTED_PROVIDERS = [
        AuthProvider.GITHUB,
        AuthProvider.GOOGLE,
        AuthProvider.MICROSOFT,
        AuthProvider.MANUAL,
    ]
    
    async def authenticate(self, provider: AuthProvider, credentials: dict) -> Session:
        """Authenticate via any of 4 supported providers."""
        pass
```

### Reference

See `docs/specs/phase-03-authentication.md` for complete specification.

### Status: APPROVED (Critical Priority)

---

## ADR-013: Per-Agent LLM Configuration

> ⚠️ **CRITICAL ADR** - Defines per-agent LLM assignment

### Context

Different agents may benefit from different LLM providers and models.

### Decision

**Each agent independently configures its LLM provider and model:**

```python
@dataclass
class AgentLLMConfig:
    """LLM configuration for a specific agent."""
    provider: str  # REQUIRED - one of 8 providers
    model: str  # REQUIRED - model name
    temperature: float = 0.7
    max_tokens: int = 4096
    fallback_providers: List[str] = field(default_factory=list)


@dataclass
class EnterpriseAgentConfig:
    """Configuration for an enterprise agent."""
    agent_id: str
    agent_type: str
    name: str
    llm_config: AgentLLMConfig  # REQUIRED - no default
```

### Example Usage

```python
# Each agent can use different providers
code_review_agent = EnterpriseAgentConfig(
    agent_id="code-review-1",
    agent_type="code_review",
    name="Code Review Agent",
    llm_config=AgentLLMConfig(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
    ),
)

security_agent = EnterpriseAgentConfig(
    agent_id="security-1",
    agent_type="security",
    name="Security Agent",
    llm_config=AgentLLMConfig(
        provider="ollama",  # Local for privacy
        model="llama3.2",
    ),
)

qa_agent = EnterpriseAgentConfig(
    agent_id="qa-1",
    agent_type="qa",
    name="QA Agent",
    llm_config=AgentLLMConfig(
        provider="openai",
        model="gpt-4o",
    ),
)
```

### Reference

See `docs/specs/phase-07-enterprise-agents.md` for complete specification.

### Status: APPROVED (Critical Priority)

---

## ADR-014: World-Class Quality Standards

> ⚠️ **NEW ADR** - Defines quality standards for all implementations

### Context

All implementations must meet world-class quality standards.

### Decision

**Every phase specification and implementation must meet these standards:**

| Standard | Description | Verification |
|----------|-------------|--------------|
| **World-Class** | Industry-leading patterns and practices | Expert review |
| **Enterprise-Grade** | SOC 2, GDPR compliance ready | Compliance audit |
| **Fully Production Ready** | Zero technical debt, battle-tested | Load testing |
| **Clean and Concise Code** | Every file earns its place | Code review |
| **Beyond PhD Level Expertise** | Advanced patterns, optimal solutions | Expert assessment |

### Quality Gates

Every file must pass:

| Gate | Requirement |
|------|-------------|
| **Necessity** | File serves unique, essential purpose |
| **Cohesion** | All contents relate to single responsibility |
| **Coupling** | Minimal external dependencies |
| **Testability** | Can be unit tested in isolation |
| **Documentation** | Clear docstrings with examples |
| **Type Safety** | Full type annotations |
| **Error Handling** | Explicit error paths |

### Phase Specification Requirements

Each phase specification includes:

1. **Quality Standards Table** - World-Class verification
2. **Business Objectives** - With World-Class Standard column
3. **Technical Outcomes** - Specific measurable targets
4. **Acceptance Tests** - AT-X.1 through AT-X.10 (10 per phase)
5. **Performance Metrics** - With alert thresholds
6. **Risk Mitigations** - With verification methods
7. **LLM-Agnostic Integration** - Provider-specific sections
8. **Validation Checklist** - 14 requirement verification

### Reference

All 10 phase specifications in `docs/specs/` follow these standards.

### Status: APPROVED (New)

---

## Summary: Critical ADRs

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-005 | LLM-Agnostic Architecture - 8 equal providers, no default | ✅ APPROVED |
| ADR-012 | Multi-Provider Authentication - 4 OAuth providers | ✅ APPROVED |
| ADR-013 | Per-Agent LLM Configuration - explicit provider required | ✅ APPROVED |
| ADR-014 | World-Class Quality Standards - all implementations | ✅ APPROVED |

---

## 14 User Requirements Verification

| # | Requirement | ADR Reference | Status |
|---|-------------|---------------|--------|
| 1 | LLM-Agnostic System | ADR-005 | ✅ |
| 2 | No Default Provider | ADR-005 | ✅ |
| 3 | 8 Equal LLM Providers | ADR-005 | ✅ |
| 4 | Per-Agent LLM Assignment | ADR-013 | ✅ |
| 5 | GitHub OAuth | ADR-012 | ✅ |
| 6 | Google OAuth | ADR-012 | ✅ |
| 7 | Microsoft OAuth | ADR-012 | ✅ |
| 8 | Manual Signup | ADR-012 | ✅ |
| 9 | Detailed Outcome Expectations | ADR-014 | ✅ |
| 10 | Phase-by-Phase Approach | ADR-002 | ✅ |
| 11 | Small Manageable Steps | ADR-002 | ✅ |
| 12 | ADDITIVE ONLY | ADR-001 | ✅ |
| 13 | No Implementation Yet | ADR-002 | ✅ |
| 14 | Absolute Project Alignment | ADR-001 | ✅ |

---

*Decision Log Version: 3.0.0*
*Last Updated: January 6, 2026*
