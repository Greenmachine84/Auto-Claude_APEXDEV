# Product Requirements Document: DEVAPEX Integration

> **Auto-Claude_APEXDEV Enhancement Plan**
>
> Enterprise-Grade, Production-Ready, World-Class **LLM-Agnostic** Autonomous Coding Platform
>
> Version: 3.1.0 | Last Updated: January 5, 2026

---

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 3.1.0 |
| **Created** | 2026-01-05 |
| **Updated** | 2026-01-05 |
| **Status** | Draft - Pending Approval |
| **Author** | Auto-Claude Enhancement Team |
| **Source** | DEVAPEX Features and Functions Overview v2.0.0 |

---

## CRITICAL CONSTRAINTS

> ⚠️ **MANDATORY REQUIREMENTS**

1. **ADDITIVE ONLY**: All enhancements MUST be additive - NO removal of existing functionality
2. **UI/UX PRESERVATION**: Original styling and flow MUST be preserved - enhance only when necessary
3. **APEX COMPLIANCE**: All features MUST comply with APEX Constitution Articles I-V
4. **ENTERPRISE-GRADE**: All implementations MUST be production-ready and world-class
5. **BACKWARD COMPATIBILITY**: Existing CLI workflows and APIs MUST remain functional
6. **LLM-AGNOSTIC**: System MUST NOT be dependent on any single LLM provider

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent System Enhancement](#2-agent-system-enhancement)
3. [Memory System Enhancement](#3-memory-system-enhancement)
4. [LLM Integration - Agnostic Architecture](#4-llm-integration---agnostic-architecture)
5. [Skills Framework](#5-skills-framework)
6. [Tools System](#6-tools-system)
7. [Orchestration System](#7-orchestration-system)
8. [Governance &amp; Compliance](#8-governance--compliance)
9. [Security &amp; Authentication](#9-security--authentication)
10. [V2.0 Modules](#10-v20-modules)
11. [Integrations Framework](#11-integrations-framework)
12. [Analytics System](#12-analytics-system)
13. [Configuration Management](#13-configuration-management)
14. [Testing Framework](#14-testing-framework)
15. [Documentation Deliverables](#15-documentation-deliverables)
16. [Desktop UI Enhancements](#16-desktop-ui-enhancements)
17. [Implementation Milestones](#17-implementation-milestones)

---

## 1. Executive Summary

### 1.1 Vision

Transform Auto-Claude_APEXDEV into a **world-class, enterprise-grade, LLM-agnostic autonomous coding platform** that empowers users with complete control over their AI providers, authentication methods, and model assignments.

### 1.2 Key Architectural Principles

> ⚠️ **CRITICAL**: The system is designed to be **PROVIDER-AGNOSTIC**

| Principle | Description |
|-----------|-------------|
| **LLM Agnostic** | No hard dependency on Anthropic/Claude - users choose their providers |
| **Multi-Auth** | Support for GitHub, Google, Microsoft, and manual account login |
| **Multi-Router** | Support for Copilot, OpenRouter, Ollama, LLMStudio, Gemini routers |
| **Per-Agent LLM** | Each agent can be assigned different LLM models/providers |
| **User Control** | Users have full control over provider selection and configuration |

### 1.3 Core Enhancements

| Category | Current State | Enhanced State | Reference |
|----------|--------------|----------------|-----------|
| Agents | 4 core agents | 4 core + 16 enterprise agents (each configurable LLM) | [Section 2](#2-agent-system-enhancement) |
| Memory | Graphiti only | Graphiti + H-MEM tiers + Episodic | [Section 3](#3-memory-system-enhancement) |
| LLM | Anthropic-dependent | **LLM-Agnostic** with 7+ routers | [Section 4](#4-llm-integration---agnostic-architecture) |
| Auth | None | Multi-provider (GitHub, Google, Microsoft, Manual) | [Section 9](#9-security--authentication) |
| Skills | Implicit | 25+ categorized skills with registry | [Section 5](#5-skills-framework) |
| Tools | Basic tools_pkg | Enhanced ToolRegistry + MCP | [Section 6](#6-tools-system) |
| Governance | Basic | 5 councils + HITL gates | [Section 8](#8-governance--compliance) |
| Security | .env based | AES-256 encrypted secrets + RBAC | [Section 9](#9-security--authentication) |
| Integrations | Linear + Graphiti | Extensible framework | [Section 11](#11-integrations-framework) |
| Analytics | None | Full metrics suite | [Section 12](#12-analytics-system) |

### 1.4 Success Criteria

- ✅ Zero breaking changes to existing functionality
- ✅ 80%+ test coverage on new code
- ✅ &lt;5% performance overhead
- ✅ APEX Constitution compliance verified
- ✅ User sign-off on each milestone
- ✅ **Full LLM provider independence achieved**
- ✅ **Per-agent LLM assignment functional**
- ✅ **Multi-auth login operational**

---

## 2. Agent System Enhancement

### 2.1 Existing Core Agents (PRESERVE)

> **Reference**: `apps/backend/agents/` - These agents MUST remain unchanged

| Agent | Location | Status |
|-------|----------|--------|
| Planner Agent | Existing | ✅ PRESERVE |
| Coder Agent | Existing | ✅ PRESERVE - Extend with APEX hooks |
| QA Reviewer | Existing | ✅ PRESERVE - Add severity categorization |
| QA Fixer | Existing | ✅ PRESERVE - Add reflexion pattern |

### 2.2 Per-Agent LLM Configuration (NEW - CRITICAL)

> ⚠️ **CORE REQUIREMENT**: Each agent MUST be able to use a different LLM provider/model

| Feature | Description | Priority |
|---------|-------------|----------|
| AgentLLMConfig | Per-agent LLM provider and model assignment | **CRITICAL** |
| ProviderOverride | Agent-level override of default provider | **CRITICAL** |
| ModelSelection | Agent-specific model selection from available models | **CRITICAL** |
| FallbackChain | Per-agent fallback provider chain | HIGH |
| CostBudget | Per-agent token/cost budget limits | MEDIUM |

#### Agent LLM Configuration Schema

```python
class AgentLLMConfig:
    """Per-agent LLM configuration"""
    agent_id: str                    # Agent identifier
    provider: str                    # e.g., "openrouter", "ollama", "copilot"
    model: str                       # e.g., "gpt-4", "claude-3-opus", "llama-3"
    fallback_providers: List[str]    # Ordered fallback list
    max_tokens: int                  # Token limit for this agent
    temperature: float               # Model temperature
    cost_budget_daily: float         # Daily cost limit (optional)
    enabled: bool                    # Whether agent is active
```

### 2.3 Enterprise Agents (16 New)

> **Reference**: DEVAPEX Features § 1 Agent System
> 
> **Note**: Each enterprise agent can be configured with its own LLM provider

#### Architecture Agents (4)

| Agent | Purpose | Default LLM | Configurable | Priority |
|-------|---------|-------------|--------------|----------|
| SystemArchitectAgent | Architecture design, pattern recommendations | User Choice | ✅ Yes | HIGH |
| SecurityArchitectAgent | Security analysis, vulnerability assessment | User Choice | ✅ Yes | HIGH |
| RefactorArchitectAgent | Code refactoring, technical debt reduction | User Choice | ✅ Yes | MEDIUM |
| PerformanceArchitectAgent | Performance optimization, profiling | User Choice | ✅ Yes | MEDIUM |

#### Security Agents (2)

| Agent | Purpose | Default LLM | Configurable | Priority |
|-------|---------|-------------|--------------|----------|
| RedTeamAgent | Adversarial testing, penetration simulation | User Choice | ✅ Yes | HIGH |
| BlueTeamAgent | Defensive security, incident response | User Choice | ✅ Yes | HIGH |

#### Quality Agents (3)

| Agent | Purpose | Default LLM | Configurable | Priority |
|-------|---------|-------------|--------------|----------|
| DocumentationLeadAgent | Documentation generation, API docs | User Choice | ✅ Yes | MEDIUM |
| QAVerificationAgent | Test planning, coverage analysis | User Choice | ✅ Yes | MEDIUM |
| ComplianceAuditorAgent | Regulatory compliance, audit trails | User Choice | ✅ Yes | MEDIUM |

#### Infrastructure Agents (4)

| Agent | Purpose | Default LLM | Configurable | Priority |
|-------|---------|-------------|--------------|----------|
| IntegrationArchitectAgent | API design, service integration | User Choice | ✅ Yes | MEDIUM |
| DataArchitectAgent | Data modeling, schema design | User Choice | ✅ Yes | MEDIUM |
| DevOpsArchitectAgent | CI/CD, infrastructure automation | User Choice | ✅ Yes | LOW |
| CloudArchitectAgent | Cloud design, multi-cloud strategy | User Choice | ✅ Yes | LOW |

#### Orchestration Agents (3)

| Agent | Purpose | Default LLM | Configurable | Priority |
|-------|---------|-------------|--------------|----------|
| MDAOrchestratorAgent | Multi-agent coordination | User Choice | ✅ Yes | HIGH |
| APIDesignAgent | RESTful/GraphQL API design | User Choice | ✅ Yes | MEDIUM |
| BaseEnterpriseAgent | Base class for enterprise agents | User Choice | ✅ Yes | HIGH |

### 2.4 File Structure

```
apps/backend/agents/
├── core/                         # EXISTING - PRESERVE
├── tools_pkg/                    # EXISTING - PRESERVE
│   ├── registry.py               # EXISTING - ENHANCE
│   ├── models.py                 # EXISTING - PRESERVE
│   └── tools/                    # EXISTING - PRESERVE
├── enterprise/                   # NEW
│   ├── __init__.py
│   ├── base_enterprise.py        # LLM-agnostic base class
│   ├── llm_config.py             # Per-agent LLM configuration
│   ├── architects/
│   ├── security/
│   ├── quality/
│   ├── infrastructure/
│   └── orchestration/
└── registry.py                   # NEW - Agent discovery with LLM config
```

---

## 3. Memory System Enhancement

### 3.1 Existing Memory (PRESERVE)

> **Reference**: `apps/backend/integrations/graphiti/` - MUST remain unchanged

| Component | Location | Status |
|-----------|----------|--------|
| Graphiti Integration | `integrations/graphiti/` | ✅ PRESERVE |
| Semantic Search | `integrations/graphiti/` | ✅ PRESERVE - Extend |
| Context Management | `apps/backend/context/` | ✅ PRESERVE |

### 3.2 H-MEM Tiered System (NEW)

> **Reference**: DEVAPEX Features § 2 Memory System

| Tier | Purpose | Storage | Access Speed | ADR Ref |
|------|---------|---------|--------------|---------|
| L1 | Active context | In-memory | &lt;1ms | ADR-003 |
| L2 | Recent sessions | SQLite | &lt;10ms | ADR-003 |
| L3 | Historical | Compressed | &lt;100ms | ADR-003 |

### 3.3 Episodic Memory Features

| Feature | Description | Value | ADR Ref |
|---------|-------------|-------|---------|
| EpisodeStore | SQLite-based action/decision storage | Learning from experience | ADR-003 |
| ReflexionPattern | Store lessons learned from past tasks | Continuous improvement | ADR-003 |
| RetentionPolicy | Configurable cleanup (30/60/90 days) | Storage optimization | ADR-003 |
| MemoryQuery | Flexible query interface | Precise memory access | ADR-003 |

### 3.4 File Structure

```
apps/backend/memory/
├── graphiti/                     # EXISTING via integrations - PRESERVE
├── episodes/                     # NEW
│   ├── __init__.py
│   ├── store.py
│   ├── reflexion.py
│   └── retention.py
├── hmem/                         # NEW
│   ├── __init__.py
│   ├── l1_cache.py
│   ├── l2_sqlite.py
│   ├── l3_archive.py
│   └── tier_manager.py
├── bridge/                       # NEW
│   ├── __init__.py
│   ├── unified_query.py
│   └── sync.py
└── embeddings/                   # NEW
    ├── __init__.py
    └── providers/
```

---

## 4. LLM Integration - Agnostic Architecture

> ⚠️ **CRITICAL SECTION**: This section defines the LLM-agnostic architecture

### 4.1 Design Philosophy

> **The system MUST NOT be dependent on any single LLM provider**

| Principle | Implementation |
|-----------|----------------|
| **No Default Provider** | Users explicitly choose their preferred provider(s) |
| **Provider Abstraction** | All LLM calls go through a unified abstraction layer |
| **Per-Agent Config** | Each agent can use a different provider/model |
| **Hot-Swappable** | Providers can be changed at runtime without restart |
| **Graceful Fallback** | Automatic failover to backup providers |

### 4.2 Supported LLM Routers

> **Reference**: DEVAPEX Features § 3 LLM Integration

| Router/Provider | Models | Configuration | Priority |
|-----------------|--------|---------------|----------|
| **GitHub Copilot** | Copilot models via VS Code LM API | API key via GitHub login | **EQUAL** |
| **OpenRouter** | 100+ models (OpenAI, Claude, Llama, Mistral, etc.) | API key | **EQUAL** |
| **Ollama** | Llama, Mistral, CodeLlama, local models | Local endpoint | **EQUAL** |
| **LM Studio** | Local models via OpenAI-compatible API | Local endpoint | **EQUAL** |
| **Google Gemini** | Gemini Pro, Gemini Ultra, Gemini Flash | API key | **EQUAL** |
| **OpenAI Direct** | GPT-4, GPT-4o, GPT-4o-mini, o1 | API key | **EQUAL** |
| **Anthropic Direct** | Claude 3 Opus, Sonnet, Haiku | API key | **EQUAL** |
| **Azure OpenAI** | Azure-hosted OpenAI models | API key + endpoint | **EQUAL** |

### 4.3 LLM Abstraction Layer

```python
class LLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    @abstractmethod
    async def complete(self, messages: List[Message], **kwargs) -> Response:
        """Generate completion - provider agnostic"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models for this provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider availability"""
        pass
```

### 4.4 LLM Router Features

| Feature | Description | Value |
|---------|-------------|-------|
| **ProviderRegistry** | Central registry of all configured providers | Discovery |
| **IntelligentRouting** | Route based on cost, capability, latency, availability | Optimization |
| **ProviderHealth** | Real-time health monitoring + automatic failover | Reliability |
| **ModelDiscovery** | Dynamic model listing from each provider | Up-to-date access |
| **CostTracking** | Per-provider token usage and cost estimation | Budget management |
| **RateLimiting** | Per-provider rate limit handling | Stability |
| **LoadBalancing** | Distribute requests across multiple providers | Scalability |

### 4.5 Per-Agent LLM Assignment

> **Each agent can be configured to use any available LLM provider/model**

| Configuration Level | Scope | Example |
|---------------------|-------|---------|
| **Global Default** | Fallback for all agents | `openrouter/claude-3-opus` |
| **Agent Type Default** | Default for agent category | Security agents → `openai/gpt-4` |
| **Individual Agent** | Specific agent override | `RedTeamAgent` → `ollama/llama-3` |
| **Task Override** | Per-task temporary override | Current task → `gemini/pro` |

### 4.6 User LLM Configuration UI

| Feature | Description |
|---------|-------------|
| Provider Setup | Add/configure providers with credentials |
| Model Browser | Browse available models per provider |
| Agent Assignment | Drag-drop model assignment to agents |
| Cost Calculator | Estimate costs based on configuration |
| Test Connection | Verify provider connectivity |

### 4.7 File Structure

```
apps/backend/llm/
├── __init__.py
├── abstraction/                  # Provider abstraction layer
│   ├── __init__.py
│   ├── base_provider.py          # Abstract LLMProvider
│   ├── message.py                # Provider-agnostic message format
│   └── response.py               # Provider-agnostic response format
├── providers/                    # Concrete provider implementations
│   ├── __init__.py
│   ├── copilot_provider.py       # GitHub Copilot via VS Code LM API
│   ├── openrouter_provider.py    # OpenRouter multi-model
│   ├── ollama_provider.py        # Ollama local models
│   ├── lmstudio_provider.py      # LM Studio local models
│   ├── gemini_provider.py        # Google Gemini
│   ├── openai_provider.py        # OpenAI direct
│   ├── anthropic_provider.py     # Anthropic direct
│   └── azure_provider.py         # Azure OpenAI
├── router/                       # Intelligent routing
│   ├── __init__.py
│   ├── router.py                 # Main router logic
│   ├── strategies.py             # Routing strategies
│   ├── health.py                 # Provider health monitoring
│   └── failover.py               # Automatic failover
├── registry/                     # Provider registration
│   ├── __init__.py
│   ├── provider_registry.py
│   └── model_catalog.py
├── config/                       # Configuration
│   ├── __init__.py
│   ├── agent_llm_config.py       # Per-agent LLM config
│   ├── provider_config.py        # Provider credentials
│   └── defaults.py               # System defaults
└── metrics/                      # Usage tracking
    ├── __init__.py
    ├── cost_tracker.py
    └── usage_analytics.py
```

---

## 5. Skills Framework

### 5.1 Skills System (NEW)

> **Reference**: DEVAPEX Features § 4 Skills Framework
>
> **Note**: Skills are LLM-agnostic and work with any configured provider

| Component | Description | Value |
|-----------|-------------|-------|
| SkillRegistry | Central registry for all skills | Skill discovery |
| SkillMetadata | Rich metadata (category, complexity, priority) | Skill classification |
| SkillExecutor | **LLM-agnostic** skill execution engine | Universal execution |
| SkillValidator | Pre/post execution validation | Quality assurance |
| SkillLoader | Dynamic skill loading from multiple sources | Extensibility |
| ContextCompression | Token-efficient context management | Cost optimization |
| ReflexionEngine | Learn from skill execution outcomes | Continuous improvement |

### 5.2 Skill Categories (25+)

| Category | Examples | Priority |
|----------|----------|----------|
| Coding | Write, refactor, optimize | HIGH |
| Review | Security, performance, style | HIGH |
| Testing | Unit, integration, e2e | HIGH |
| Documentation | API, user, developer | MEDIUM |
| Architecture | Design, patterns, decisions | MEDIUM |
| Security | Scan, audit, remediate | HIGH |
| DevOps | CI/CD, deploy, monitor | MEDIUM |

### 5.3 File Structure

```
apps/backend/skills/
├── __init__.py
├── registry.py
├── executor.py                   # LLM-agnostic executor
├── validator.py
├── loader.py
├── rubric.py
├── categories/
│   ├── coding/
│   ├── review/
│   ├── testing/
│   ├── documentation/
│   ├── architecture/
│   ├── security/
│   └── devops/
└── templates/
    └── prompt_template_skill.py
```

---

## 6. Tools System

### 6.1 Existing Tools (PRESERVE &amp; ENHANCE)

> **Reference**: `apps/backend/agents/tools_pkg/` - Enhance, do not replace

| Component | Location | Status |
|-----------|----------|--------|
| ToolRegistry | `tools_pkg/registry.py` | ✅ PRESERVE - Enhance |
| Tool Models | `tools_pkg/models.py` | ✅ PRESERVE |
| Permissions | `tools_pkg/permissions.py` | ✅ PRESERVE |
| Tools Directory | `tools_pkg/tools/` | ✅ PRESERVE - Extend |

### 6.2 Tool Enhancements (Additive)

> **Reference**: DEVAPEX Features § 5 Tools

| Feature | Description | Enhancement Type |
|---------|-------------|------------------|
| FileOperations | Read, write, create, delete, move files | EXTEND existing |
| GitOperations | Clone, commit, push, pull, branch, merge | EXTEND existing |
| CommandExecution | Safe shell command execution with sandboxing | EXTEND existing |
| MCPClient | Model Context Protocol integration | ADD NEW |
| DockerIntegration | Container management and execution | ADD NEW |
| SearchTools | Code search, grep, semantic search | EXTEND existing |
| DiffTools | File comparison and patch generation | EXTEND existing |

### 6.3 File Structure

```
apps/backend/agents/tools_pkg/
├── __init__.py                   # EXISTING - PRESERVE
├── registry.py                   # EXISTING - ENHANCE
├── models.py                     # EXISTING - PRESERVE
├── permissions.py                # EXISTING - PRESERVE
├── tools/                        # EXISTING - EXTEND
│   └── ... existing tools ...
├── mcp/                          # NEW
│   ├── __init__.py
│   ├── client.py
│   └── server.py
└── docker/                       # NEW
    ├── __init__.py
    └── integration.py
```

---

## 7. Orchestration System

### 7.1 Existing Workflows (PRESERVE)

| Component | Status | Action |
|-----------|--------|--------|
| spec_runner | ✅ PRESERVE | No changes |
| QA Loop | ✅ PRESERVE | Extend with events |
| Git Worktree | ✅ PRESERVE | No changes |

### 7.2 Orchestration Layer (NEW)

> **Reference**: DEVAPEX Features § 6 Orchestration

| Feature | Description | Value | ADR Ref |
|---------|-------------|-------|---------|
| TaskQueue | Priority-based task scheduling | Ordered execution | ADR-004 |
| AgentPool | Concurrent agent management (12 max, 6 concurrent) | Parallel processing | ADR-007 |
| EventBus | Real-time event emission for UI updates | Live feedback | ADR-004 |
| SessionManager | User session tracking and isolation | Multi-user support | ADR-004 |
| WorkflowEngine | Multi-step workflow execution | Complex automation | ADR-004 |
| DependencyResolver | Task dependency management | Correct ordering | ADR-004 |
| ConcurrencyControl | Rate limiting and resource management | System stability | ADR-004 |
| StateTransitions | Atomic task state management | Data integrity | ADR-004 |

### 7.3 File Structure

```
apps/backend/orchestrator/
├── __init__.py
├── task_queue.py
├── agent_pool.py
├── manager.py
├── events.py
├── session.py
├── state.py
└── workflow.py
```

---

## 8. Governance &amp; Compliance

### 8.1 APEX Constitution Implementation

> **Reference**: DEVAPEX Features § 7 Governance &amp; Compliance

| Article | Implementation | ADR Ref |
|---------|----------------|---------|
| Article I: Core Principles | Agent autonomy, traceable decisions, task integrity | ADR-008 |
| Article II: Agent Classes | Primary, Advisory, Quality agent separation | ADR-008 |
| Article III: Task Workflow | TODO → IN_PROGRESS → IN_REVIEW → DONE | ADR-008 |
| Article V: Safety Protocols | Operation limits, forbidden operations, rollback | ADR-008 |

### 8.2 Validators (NEW)

| Validator | Purpose | Priority |
|-----------|---------|----------|
| ConstitutionValidator | APEX Constitution compliance checking | MEDIUM |
| ArchitectValidator | Architecture specification validation | MEDIUM |
| AlignmentGate | Pre-execution alignment verification | MEDIUM |

### 8.3 Governance Councils (5)

| Council | Purpose | Quorum | Priority |
|---------|---------|--------|----------|
| ArchitectureCouncil | Design quality review | 2/3 | LOW |
| SecurityCouncil | Security review and approval | 2/3 | LOW |
| QualityCouncil | Quality standards enforcement | 2/3 | LOW |
| OpsCouncil | Operational readiness review | 2/3 | LOW |
| ProductCouncil | Business alignment verification | 2/3 | LOW |

### 8.4 HITL Gates (NEW)

| Feature | Description | Priority |
|---------|-------------|----------|
| HITLGate | Human-in-the-loop approval workflows | LOW |
| EvidenceBinder | Audit trail and evidence collection | MEDIUM |
| SpecDrivenGate | Specification-based validation | MEDIUM |

---

## 9. Security &amp; Authentication

### 9.1 Existing Security (PRESERVE)

> **Reference**: `apps/backend/security/` - Maintain backward compatibility

| Component | Location | Status |
|-----------|----------|--------|
| .env Configuration | Various | ✅ PRESERVE as fallback |
| API Key Storage | .env files | ✅ PRESERVE as fallback |
| Security Scanner | `security/` | ✅ PRESERVE |

### 9.2 Multi-Provider Authentication (NEW - CRITICAL)

> ⚠️ **CORE REQUIREMENT**: Users can login via multiple OAuth providers or manually

| Auth Provider | Implementation | Priority |
|---------------|----------------|----------|
| **GitHub OAuth** | OAuth 2.0 flow with GitHub | **CRITICAL** |
| **Google OAuth** | OAuth 2.0 flow with Google | **CRITICAL** |
| **Microsoft OAuth** | OAuth 2.0 flow with Microsoft/Azure AD | **CRITICAL** |
| **Manual Signup** | Email/password with verification | **CRITICAL** |

### 9.3 Authentication Architecture

```python
class AuthProvider(ABC):
    """Abstract base for authentication providers"""
    
    @abstractmethod
    async def authenticate(self, credentials: Credentials) -> AuthResult:
        pass
    
    @abstractmethod
    async def get_user_info(self, token: str) -> UserInfo:
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        pass
```

### 9.4 User Account Features

| Feature | Description | Priority |
|---------|-------------|----------|
| AccountCreation | Create accounts via OAuth or manual signup | **CRITICAL** |
| ProfileManagement | User profile with preferences | HIGH |
| LLMCredentials | Per-user LLM provider credentials storage | **CRITICAL** |
| TeamMembership | Optional team/organization support | MEDIUM |
| SessionManagement | Multi-device session handling | HIGH |

### 9.5 Secrets Manager (NEW)

> **Reference**: DEVAPEX Features § 8 Security &amp; Authentication

| Feature | Description | ADR Ref |
|---------|-------------|---------|
| AES-256-GCM | Encryption standard | ADR-010 |
| PBKDF2 | Key derivation | ADR-010 |
| SecretScopes | USER, TEAM, PROJECT, ENTERPRISE | ADR-010 |
| SecretTypes | API_KEY, PASSWORD, TOKEN, CERTIFICATE | ADR-010 |
| VersionHistory | 10 versions retained | ADR-010 |
| AuditTrail | Complete access logging | ADR-010 |
| SecretRotation | Expiry tracking and rotation reminders | ADR-010 |

### 9.6 File Structure

```
apps/backend/auth/
├── __init__.py
├── providers/                    # OAuth providers
│   ├── __init__.py
│   ├── base_auth.py              # Abstract AuthProvider
│   ├── github_auth.py            # GitHub OAuth
│   ├── google_auth.py            # Google OAuth
│   ├── microsoft_auth.py         # Microsoft OAuth
│   └── manual_auth.py            # Email/password
├── session/                      # Session management
│   ├── __init__.py
│   ├── session_manager.py
│   └── token_manager.py
├── user/                         # User management
│   ├── __init__.py
│   ├── user_service.py
│   ├── profile.py
│   └── credentials.py            # User LLM credentials
└── rbac/                         # Role-based access control
    ├── __init__.py
    ├── roles.py
    └── permissions.py
```

---

## 10. V2.0 Modules

### 10.1 Projects Module

> **Reference**: DEVAPEX Features § 9 V2.0 Modules

| Feature | Description | Priority | ADR Ref |
|---------|-------------|----------|---------|
| ProjectLifecycle | DRAFT → ACTIVE → ARCHIVED | HIGH | ADR-009 |
| ProjectTypes | Application, Library, Service, Monorepo | HIGH | ADR-009 |
| SemanticVersioning | Auto major/minor/patch bumping | MEDIUM | ADR-009 |
| RepositoryIntegration | Git repo association | HIGH | ADR-009 |
| ProjectMetadata | Rich settings storage | MEDIUM | ADR-009 |
| **ProjectLLMConfig** | Per-project LLM provider settings | HIGH | ADR-009 |

### 10.2 Teams Module (Optional)

| Feature | Description | Priority |
|---------|-------------|----------|
| TeamRoles | OWNER, ADMIN, MEMBER, VIEWER, GUEST | LOW |
| MemberManagement | Add, remove, update members | LOW |
| ProjectSharing | Cross-team project access | LOW |
| TeamChannels | Team communication | LOW |
| PresenceTracking | Real-time member presence | LOW |
| **TeamLLMConfig** | Team-level LLM provider settings | LOW |

### 10.3 Engines Module

| Feature | Description | Priority |
|---------|-------------|----------|
| EngineBase | Abstract with lifecycle | MEDIUM |
| SelectionEngine | APEX Part 7 scoring-based selection | MEDIUM |
| Strategies | BEST_MATCH, TOP_N, THRESHOLD, ENSEMBLE | MEDIUM |
| EngineMetrics | Performance monitoring | MEDIUM |

### 10.4 Updates Module

> **EXISTING**: `apps/frontend/src/main/app-updater.ts` (16KB)

| Component | Status | Enhancement |
|-----------|--------|-------------|
| AppUpdater | ✅ EXISTS | Enhance with DEVAPEX patterns |
| UpdateModes | Verify | AUTOMATIC, MANUAL, DISABLED |
| GitSync | Verify | Git-based version sync |
| RollbackSupport | Verify | Automatic backup |
| UpdateNotifications | ✅ EXISTS | Enhance with events |

**Action**: Review existing `app-updater.ts` and enhance only if needed per ADR-009.

---

## 11. Integrations Framework

### 11.1 Existing Integrations (PRESERVE)

> **Reference**: `apps/backend/integrations/`

| Integration | Location | Status |
|-------------|----------|--------|
| Graphiti | `integrations/graphiti/` | ✅ PRESERVE |
| Linear | `integrations/linear/` | ✅ PRESERVE |

### 11.2 Extensible Integration Architecture (NEW)

> **Design Goal**: Enable future integrations (GitLab, Jira, Slack) without code changes

| Component | Description | Purpose |
|-----------|-------------|---------|
| IntegrationRegistry | Central registry for all integrations | Discovery |
| IntegrationBase | Abstract base class | Consistency |
| IntegrationConfig | Unified configuration model | Easy setup |
| IntegrationHooks | Lifecycle hooks (connect, sync, disconnect) | Management |

### 11.3 File Structure

```
apps/backend/integrations/
├── __init__.py                   # EXISTING - ENHANCE
├── base.py                       # NEW - Abstract base class
├── registry.py                   # NEW - Integration registry
├── config.py                     # NEW - Unified config
├── graphiti/                     # EXISTING - PRESERVE
├── linear/                       # EXISTING - PRESERVE
└── plugins/                      # NEW - Future integrations
    ├── __init__.py
    └── README.md                 # Integration development guide
```

### 11.4 Future Integration Template

```python
# apps/backend/integrations/plugins/README.md
"""
Integration Development Guide

To add a new integration (e.g., GitLab, Jira, Slack):

1. Create folder: integrations/plugins/gitlab/
2. Implement IntegrationBase:
   - __init__.py
   - client.py (API client)
   - sync.py (data synchronization)
   - config.py (integration-specific config)
3. Register in IntegrationRegistry
4. Add configuration to .env.example
5. Document in USER_GUIDE.md

See existing Linear integration for reference.
"""
```

---

## 12. Analytics System

### 12.1 Analytics Architecture (NEW)

> **Reference**: DEVAPEX Features § 12 Analytics

| Component | Description | Purpose |
|-----------|-------------|---------|
| MetricsCollector | Centralized metric collection | Data gathering |
| MetricsStore | Time-series storage (SQLite) | Persistence |
| MetricsAPI | REST API for metrics access | Integration |
| MetricsDashboard | UI component (optional) | Visualization |

### 12.2 Metrics Categories

| Category | Metrics | Priority |
|----------|---------|----------|
| TaskMetrics | Completion rates, durations, throughput | HIGH |
| AgentMetrics | Utilization, success rates, error rates | HIGH |
| MemoryMetrics | Usage, query performance, cache hit ratio | MEDIUM |
| CostMetrics | LLM token usage, cost estimation **per provider** | HIGH |
| QualityMetrics | Code quality scores, issue rates, test coverage | MEDIUM |
| **ProviderMetrics** | Per-provider latency, reliability, cost | HIGH |

### 12.3 Implementation Specifications

| Metric | Calculation | Storage |
|--------|-------------|---------|
| task_completion_rate | completed / total * 100 | Daily aggregate |
| agent_utilization | active_time / total_time * 100 | Per-agent |
| avg_task_duration | sum(duration) / count | Hourly aggregate |
| token_usage | sum(prompt_tokens + completion_tokens) | Per-request |
| cost_estimate | token_usage * model_rate | Daily aggregate |
| **provider_latency** | avg(response_time) per provider | Hourly |
| **provider_reliability** | success_rate per provider | Daily |

### 12.4 File Structure

```
apps/backend/analytics/
├── __init__.py
├── collector.py
├── store.py
├── api.py
├── metrics/
│   ├── __init__.py
│   ├── task_metrics.py
│   ├── agent_metrics.py
│   ├── memory_metrics.py
│   ├── cost_metrics.py
│   ├── quality_metrics.py
│   └── provider_metrics.py       # NEW - Per-provider metrics
└── exporters/
    ├── __init__.py
    ├── json_exporter.py
    └── prometheus_exporter.py
```

---

## 13. Configuration Management

### 13.1 Existing Configuration (PRESERVE)

| Component | Location | Status |
|-----------|----------|--------|
| .env files | Various | ✅ PRESERVE |
| Backend config | `apps/backend/` | ✅ PRESERVE |
| Frontend config | `apps/frontend/` | ✅ PRESERVE |

### 13.2 Unified Configuration (NEW)

> **Reference**: DEVAPEX Features § 13 Configuration

| Feature | Description | Purpose |
|---------|-------------|---------|
| UnifiedConfig | Single configuration source | Consistency |
| EnvironmentConfig | Development, staging, production modes | Environment support |
| ConfigValidation | Schema-based validation | Error prevention |
| ConfigHotReload | Runtime configuration updates | Flexibility |
| **LLMProviderConfig** | Per-provider credential management | LLM agnosticism |
| **UserPreferences** | Per-user configuration storage | Personalization |

### 13.3 Configuration Schema

```python
# apps/backend/config/schema.py
"""
Configuration Schema (Enterprise-Grade)

Sections:
1. LLMConfig - Provider configurations (multiple providers)
   - Per-provider credentials
   - Default provider selection
   - Per-agent overrides
2. AuthConfig - Authentication provider settings
   - OAuth provider configs (GitHub, Google, Microsoft)
   - Manual auth settings
3. MemoryConfig - Retention, embedding, search settings
4. OrchestratorConfig - Pool size, queue limits, timeouts
5. SecurityConfig - Encryption, access settings
6. GovernanceConfig - HITL, compliance, approval settings
7. AnalyticsConfig - Metrics collection, retention, export
8. IntegrationConfig - Per-integration settings
"""
```

### 13.4 File Structure

```
apps/backend/config/
├── __init__.py
├── unified.py                    # NEW - Unified config manager
├── schema.py                     # NEW - Config schema definitions
├── validators.py                 # NEW - Schema validation
├── loaders/
│   ├── __init__.py
│   ├── env_loader.py             # Load from .env
│   ├── file_loader.py            # Load from JSON/YAML
│   └── secrets_loader.py         # Load from secrets manager
├── providers/                    # NEW - LLM provider configs
│   ├── __init__.py
│   └── llm_provider_config.py
└── environments/
    ├── development.py
    ├── staging.py
    └── production.py
```

---

## 14. Testing Framework

### 14.1 Testing Strategy

> **Reference**: DEVAPEX Features § 14 Testing

| Test Type | Coverage Target | Priority |
|-----------|----------------|----------|
| Unit Tests | 80%+ new code | HIGH |
| Integration Tests | All module boundaries | HIGH |
| E2E Tests | Critical workflows | HIGH |
| Performance Tests | Baseline + regression | MEDIUM |
| Compliance Tests | APEX Constitution | MEDIUM |
| Security Tests | OWASP Top 10 | HIGH |
| **LLM Provider Tests** | All supported providers | HIGH |
| **Auth Provider Tests** | All OAuth flows | HIGH |

### 14.2 Test Specifications

| Module | Unit Tests | Integration Tests | E2E Tests |
|--------|------------|-------------------|-----------|
| Orchestrator | task_queue, agent_pool | full workflow | Kanban → Agent |
| Memory | episodes, hmem tiers | Graphiti sync | Search accuracy |
| Secrets | encryption, scoping | IPC handlers | UI → Store → Retrieve |
| Analytics | collectors, metrics | store + API | Dashboard display |
| Agents | each enterprise agent | multi-agent coordination | Spec → Code |
| **LLM Providers** | each provider client | routing, failover | Multi-provider task |
| **Auth** | each OAuth provider | login flow | Full signup/login |

### 14.3 Validation Requirements

| Validation | Method | Acceptance Criteria |
|------------|--------|---------------------|
| Functionality | Automated tests | All tests pass |
| Performance | Benchmark suite | &lt;5% overhead |
| Security | Security scan | No critical vulnerabilities |
| APEX Compliance | Compliance tests | All articles satisfied |
| User Acceptance | Manual verification | Sign-off received |
| **LLM Agnosticism** | Provider swap tests | Works with all providers |

### 14.4 File Structure

```
tests/
├── conftest.py                   # EXISTING - EXTEND
├── pytest.ini                    # EXISTING - PRESERVE
├── unit/                         # NEW - Organized unit tests
│   ├── test_orchestrator/
│   ├── test_memory/
│   ├── test_secrets/
│   ├── test_analytics/
│   ├── test_enterprise_agents/
│   ├── test_llm_providers/       # NEW - Provider tests
│   └── test_auth_providers/      # NEW - Auth tests
├── integration/                  # NEW - Integration tests
│   ├── test_memory_integration.py
│   ├── test_orchestrator_integration.py
│   ├── test_ipc_integration.py
│   ├── test_llm_routing.py       # NEW - LLM routing tests
│   └── test_auth_flow.py         # NEW - Auth flow tests
├── e2e/                          # NEW - End-to-end tests
│   ├── test_kanban_workflow.py
│   ├── test_secrets_workflow.py
│   ├── test_spec_execution.py
│   └── test_multi_provider.py    # NEW - Multi-provider tests
├── performance/                  # NEW - Performance tests
│   ├── test_memory_perf.py
│   └── test_orchestrator_perf.py
└── compliance/                   # NEW - APEX compliance
    └── test_apex_compliance.py
```

---

## 15. Documentation Deliverables

### 15.1 Required Documentation

> **Reference**: DEVAPEX Features § 15 Documentation

| Document | Purpose | Priority | Status |
|----------|---------|----------|--------|
| ARCHITECTURE.md | System architecture overview | HIGH | NEW |
| API.md | API reference documentation | HIGH | NEW |
| USER_GUIDE.md | End-user documentation | MEDIUM | NEW |
| DEVELOPMENT.md | Developer setup and contribution guide | MEDIUM | ENHANCE |
| CONFIGURATION.md | Configuration reference | MEDIUM | NEW |
| **LLM_PROVIDERS.md** | LLM provider setup guide | HIGH | NEW |
| **AUTH_SETUP.md** | Authentication configuration guide | HIGH | NEW |
| decisions.md | Architecture Decision Records | HIGH | ✅ EXISTS |
| CHANGELOG.md | Version history and changes | HIGH | ✅ EXISTS |
| FEATURES.md | Feature catalog | MEDIUM | NEW |

### 15.2 Documentation Standards

| Standard | Requirement |
|----------|-------------|
| Format | Markdown with GitHub Flavored Markdown |
| Code Examples | Working, tested code snippets |
| Cross-References | Links between related documents |
| Version Tracking | Document version in header |
| API Documentation | OpenAPI/Swagger for REST APIs |

### 15.3 File Structure

```
docs/
├── Decision.md                   # EXISTS - ADRs
├── DEVAPEX_CHANGELOG.md          # EXISTS - Integration changelog
├── PRD_DEVAPEX_INTEGRATION.md    # EXISTS - This document
├── ARCHITECTURE.md               # NEW
├── API.md                        # NEW
├── USER_GUIDE.md                 # NEW
├── CONFIGURATION.md              # NEW
├── LLM_PROVIDERS.md              # NEW - Provider setup
├── AUTH_SETUP.md                 # NEW - Auth configuration
├── FEATURES.md                   # NEW
└── api/                          # NEW - API specs
    ├── openapi.yaml
    └── schemas/
```

---

## 16. Desktop UI Enhancements

### 16.1 Existing UI (PRESERVE)

> ⚠️ **CRITICAL**: Original styling and flow MUST be preserved

| Component | Status | Action |
|-----------|--------|--------|
| 12-Terminal Grid | ✅ PRESERVE | No changes |
| Existing Theme | ✅ PRESERVE | No changes |
| Navigation Flow | ✅ PRESERVE | No changes |
| Settings Panel | ✅ PRESERVE | Extend only |
| Kanban Board | ✅ PRESERVE | Enhance only |

### 16.2 UI Enhancements (When Necessary)

| Enhancement | Description | Impact | Priority |
|-------------|-------------|--------|----------|
| Priority Colors | Visual priority indicators on Kanban cards | Low | MEDIUM |
| Agent Linking | Show assigned agent on tasks | Low | MEDIUM |
| Status Events | Real-time status updates | Low | MEDIUM |
| Memory Panel | Episode history viewer (optional) | Low | LOW |
| Analytics View | Metrics dashboard (optional) | Low | LOW |
| **LLM Provider Panel** | Provider configuration UI | LOW | HIGH |
| **Login Screen** | OAuth provider selection | LOW | **CRITICAL** |
| **Agent LLM Config** | Per-agent model assignment UI | LOW | HIGH |

---

## 17. Implementation Milestones

### Phase 1: Foundation (Week 1-2)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 1A | Base Enterprise Agent class (LLM-agnostic) | HIGH | ADR-001 |
| 1B | Agent Registry with LLM config | HIGH | ADR-001 |
| 1C | Episode Store | HIGH | ADR-003 |

### Phase 2: LLM Agnostic Layer (Week 3-4) - **NEW PRIORITY**

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 2A | LLM Abstraction Layer | **CRITICAL** | ADR-005 |
| 2B | Provider Implementations (7+) | **CRITICAL** | ADR-005 |
| 2C | Intelligent Router | HIGH | ADR-005 |
| 2D | Per-Agent LLM Config | **CRITICAL** | ADR-005 |

### Phase 3: Authentication (Week 5-6) - **NEW PRIORITY**

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 3A | GitHub OAuth | **CRITICAL** | ADR-010 |
| 3B | Google OAuth | **CRITICAL** | ADR-010 |
| 3C | Microsoft OAuth | **CRITICAL** | ADR-010 |
| 3D | Manual Signup | **CRITICAL** | ADR-010 |
| 3E | User Credential Storage | HIGH | ADR-010 |

### Phase 4: Orchestration (Week 7-8)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 4A | Task Queue | HIGH | ADR-004 |
| 4B | Agent Pool | HIGH | ADR-007 |
| 4C | Event Bus | HIGH | ADR-004 |

### Phase 5: Memory (Week 9-10)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 5A | H-MEM L1/L2/L3 tiers | MEDIUM | ADR-003 |
| 5B | Memory Bridge | MEDIUM | ADR-003 |
| 5C | Unified Query | MEDIUM | ADR-003 |

### Phase 6: Security (Week 11-12)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 6A | Secrets Manager | HIGH | ADR-010 |
| 6B | Audit Trail | MEDIUM | ADR-010 |
| 6C | RBAC | LOW | ADR-010 |

### Phase 7: Enterprise Agents (Week 13-16)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 7A | Architecture Agents (4) | MEDIUM | ADR-002 |
| 7B | Security Agents (2) | HIGH | ADR-010 |
| 7C | Quality Agents (3) | MEDIUM | ADR-002 |
| 7D | Infrastructure Agents (4) | LOW | ADR-002 |
| 7E | Orchestration Agents (3) | MEDIUM | ADR-004 |

### Phase 8: Analytics &amp; Tools (Week 17-18)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 8A | Metrics Collector (with provider metrics) | HIGH | ADR-009 |
| 8B | Tool Registry Enhancement | MEDIUM | ADR-002 |
| 8C | Integration Framework | MEDIUM | ADR-009 |

### Phase 9: Governance (Week 19-20)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 9A | APEX Validators | MEDIUM | ADR-008 |
| 9B | Governance Councils | LOW | ADR-008 |
| 9C | HITL Gates | LOW | ADR-008 |

### Phase 10: Testing &amp; Documentation (Week 21-22)

| Milestone | Tasks | Priority | ADR Ref |
|-----------|-------|----------|---------|
| 10A | Unit Tests (80%+) | HIGH | ADR-011 |
| 10B | Integration Tests | HIGH | ADR-011 |
| 10C | E2E Tests | MEDIUM | ADR-011 |
| 10D | LLM Provider Tests | HIGH | ADR-011 |
| 10E | Auth Provider Tests | HIGH | ADR-011 |
| 10F | Documentation | HIGH | ADR-011 |
| 10G | User Sign-off | HIGH | ADR-011 |

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Lead | | | |
| Technical Lead | | | |
| QA Lead | | | |
| User Representative | | | |

---

## References

| Document | Location | Description |
|----------|----------|-------------|
| Decision.md | `docs/Decision.md` | Architecture Decision Records |
| DEVAPEX_CHANGELOG.md | `docs/DEVAPEX_CHANGELOG.md` | Integration changelog |
| DEVAPEX Features | User-provided | Features and Functions Overview v2.0.0 |
| APEX Constitution | DEVAPEX repo | Governance framework |
| Auto-Claude CLAUDE.md | Repository root | Original project documentation |

---

*Document Version: 3.1.0*
*Last Updated: January 5, 2026*
*Based on: DEVAPEX Features and Functions Overview v2.0.0*
*Key Update: LLM-Agnostic Architecture with Multi-Provider Authentication*
