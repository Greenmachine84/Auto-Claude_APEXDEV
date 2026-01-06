# Decision Log

> **Auto-Claude_APEXDEV Enhancement Plan** - Architectural Decision Records (ADR)
> 
> This document captures key decisions, rationales, and trade-offs for the DEVAPEX feature integration into Auto-Claude.

---

## Document Info

| Field | Value |
|-------|-------|
| **Version** | 2.0.0 |
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
5. [ADR-005: LLM-Agnostic Architecture](#adr-005-llm-agnostic-architecture) ⚠️ UPDATED
6. [ADR-006: Kanban UI Integration](#adr-006-kanban-ui-integration)
7. [ADR-007: Agent Pool Management](#adr-007-agent-pool-management)
8. [ADR-008: APEX Governance Compliance](#adr-008-apex-governance-compliance)
9. [ADR-009: Enterprise Features Selection](#adr-009-enterprise-features-selection)
10. [ADR-010: Security Model Harmonization](#adr-010-security-model-harmonization)
11. [ADR-011: Merge Strategy and Testing](#adr-011-merge-strategy-and-testing)
12. [ADR-012: Multi-Provider Authentication](#adr-012-multi-provider-authentication) ⚠️ NEW
13. [ADR-013: Per-Agent LLM Configuration](#adr-013-per-agent-llm-configuration) ⚠️ NEW

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

**Phased additive integration with feature toggles:**

```
Phase 1: Foundation (BaseEnterpriseAgent, AgentRegistry, EpisodeStore)
Phase 2: LLM Agnostic Layer (Providers, Router, Per-Agent Config) ← CRITICAL
Phase 3: Authentication (GitHub, Google, Microsoft, Manual) ← CRITICAL
Phase 4: Orchestration (TaskQueue, AgentPool, EventBus)
Phase 5: Memory Enhancement (H-MEM, Episodic, Bridge)
Phase 6: Security (Secrets Manager, Audit, RBAC)
Phase 7: Enterprise Agents (16 new agents)
Phase 8: Analytics &amp; Tools (Metrics, ToolRegistry)
Phase 9: Governance (Validators, Councils, HITL)
Phase 10: Testing &amp; Documentation
```

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

### Status: APPROVED (Updated for LLM-Agnostic priority)

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
  User → Kanban UI → TaskQueue → Orchestrator → AgentPool → agent.py → LLM Router
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

**Implement a fully LLM-agnostic architecture with no default provider.**

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **No Default Provider** | Users explicitly configure their preferred provider(s) |
| **Provider Abstraction** | All LLM calls through unified `LLMProvider` interface |
| **Per-Agent Config** | Each agent can use a different provider/model |
| **Equal Priority** | All providers are equal - no "primary" or "fallback" |
| **Hot-Swappable** | Providers can be changed at runtime |
| **Graceful Failover** | Automatic failover based on user-defined chain |

### Supported LLM Routers (All Equal Priority)

| Router/Provider | Models | Configuration |
|-----------------|--------|---------------|
| GitHub Copilot | Copilot models via VS Code LM API | GitHub login |
| OpenRouter | 100+ models (OpenAI, Claude, Llama, Mistral, etc.) | API key |
| Ollama | Llama, Mistral, CodeLlama, local models | Local endpoint |
| LM Studio | Local models via OpenAI-compatible API | Local endpoint |
| Google Gemini | Gemini Pro, Ultra, Flash | API key |
| OpenAI Direct | GPT-4, GPT-4o, GPT-4o-mini, o1 | API key |
| Anthropic Direct | Claude 3 Opus, Sonnet, Haiku | API key |
| Azure OpenAI | Azure-hosted OpenAI models | API key + endpoint |

### Architecture

```python
from abc import ABC, abstractmethod

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
    
    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider availability."""
        pass


class LLMRouter:
    """Route requests to user-configured providers."""
    
    def __init__(self, providers: Dict[str, LLMProvider]):
        self.providers = providers  # User-configured only
    
    async def route(self, task: Task, agent_config: AgentLLMConfig) -> Response:
        """Route to agent's configured provider."""
        provider_id = agent_config.provider
        provider = self.providers.get(provider_id)
        
        if not provider:
            raise ProviderNotConfigured(f"Provider '{provider_id}' not configured")
        
        try:
            return await provider.complete(task.messages)
        except ProviderError:
            # Try fallback chain defined by user
            for fallback_id in agent_config.fallback_providers:
                fallback = self.providers.get(fallback_id)
                if fallback:
                    return await fallback.complete(task.messages)
            raise
```

### Consequences

1. **User Responsibility**: Users must configure at least one provider
2. **Onboarding Change**: First-run wizard guides provider setup
3. **No Assumptions**: System never assumes a provider is available
4. **Documentation Required**: Clear guides for each provider setup

### Supersedes

This ADR supersedes the previous ADR-005 which designated Claude as "primary" provider.

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
6. **Add login/authentication screen**

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
  agentLLMConfig?: AgentLLMConfig;  // NEW: Per-agent LLM
  episodeHistory?: Episode[];
  specId?: string;
}
```

### Rationale

1. **Visual Clarity**: Priority colors improve task scanning
2. **Agent Visibility**: Users see which agents are active
3. **Memory Access**: Context/history available without leaving board
4. **LLM Control**: Users can see/change agent LLM assignments

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
    
    def __init__(self, config: AgentPoolConfig, llm_router: LLMRouter):
        self.config = config
        self.llm_router = llm_router  # LLM-agnostic router
        self.agents: dict[str, AgentInstance] = {}
        self.active_tasks: dict[str, str] = {}  # task_id → agent_id
    
    async def acquire(self, agent_type: str, llm_config: AgentLLMConfig) -> AgentInstance:
        """Get or create an agent instance with specified LLM config."""
        # Check for idle agent of this type with matching LLM
        idle = self._find_idle_agent(agent_type, llm_config)
        if idle:
            return idle
        
        # Create new if under limit
        if len(self.agents) < self.config.max_agents:
            return await self._create_agent(agent_type, llm_config)
        
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
| **Multi-Auth (OAuth)** | Critical | ✅ Yes | Core requirement |
| **LLM Providers** | Critical | ✅ Yes | Core requirement |
| Projects Manager | High | ✅ Yes | Improves project lifecycle |
| Secrets Manager | High | ✅ Yes | Security requirement |
| Teams Collaboration | Medium | ⏳ Phase 7+ | After auth complete |
| Auto-Updates | Low | ✅ Enhance | Already implemented |

### Secrets Management Design

From DEVAPEX `secrets/manager.py`:

```python
class SecretScope(Enum):
    USER = "user"           # Personal API keys / LLM credentials
    PROJECT = "project"     # Project-specific secrets
    GLOBAL = "global"       # Shared across projects

class SecretsManager:
    async def store(self, name: str, value: str, 
                   scope: SecretScope, owner_id: str):
        encrypted = self._encrypt(value, self.master_key)
        # Store with audit trail
        ...
```

### Status: APPROVED (Updated priorities)

---

## ADR-010: Security Model Harmonization

### Context

Both systems have security layers. Need unified approach including multi-provider authentication.

### Auto-Claude Security (Current)

1. OS Sandbox - Bash command isolation
2. Filesystem Permissions - Project directory only
3. Command Allowlist - Dynamic from project analysis

### DEVAPEX Security (To Add)

1. Secret Encryption - PBKDF2 + Fernet (AES-256)
2. Scoped Access Control - User/Team/Project/Enterprise
3. Audit Trails - Complete action logging
4. **Multi-Provider OAuth** - GitHub, Google, Microsoft
5. **LLM Credential Storage** - Per-user encrypted storage

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
        self.auth_manager = AuthManager()  # NEW: Multi-provider auth
    
    async def validate_operation(self, operation: Operation) -> bool:
        # Auto-Claude checks
        if not self.command_allowlist.is_allowed(operation.command):
            return False
        if not self.filesystem_guard.is_allowed(operation.path):
            return False
        
        # Authentication check
        if not await self.auth_manager.is_authenticated(operation.user_id):
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

### Status: APPROVED (Updated for Multi-Auth)

---

## ADR-011: Merge Strategy and Testing

### Context

Need a safe strategy to merge DEVAPEX features without breaking Auto-Claude stability.

### Decision

**Conservative merge with extensive testing:**

1. **Feature Branches**: Each major feature in separate branch
2. **Integration Tests**: Comprehensive tests before merge
3. **Canary Deployment**: Phase rollout to subset of users first
4. **Rollback Plan**: Every feature has disable flag

### Testing Requirements

| Category | Coverage | Priority |
|----------|----------|----------|
| Unit Tests | 80%+ | HIGH |
| Integration Tests | All boundaries | HIGH |
| E2E Tests | Critical paths | HIGH |
| **LLM Provider Tests** | All 8 providers | HIGH |
| **Auth Provider Tests** | All 4 OAuth flows | HIGH |
| Performance Tests | Baseline comparison | MEDIUM |
| Security Tests | OWASP Top 10 | HIGH |
| APEX Compliance | All articles | MEDIUM |

### LLM Provider Testing

```python
@pytest.mark.parametrize("provider", [
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
])
async def test_provider_completion(provider):
    """Test each provider can complete a basic task."""
    router = LLMRouter(providers={provider: create_provider(provider)})
    response = await router.route(test_task, test_config)
    assert response.success
    assert response.content
```

### Status: APPROVED

---

## ADR-012: Multi-Provider Authentication

> ⚠️ **NEW ADR** - Critical for user accounts

### Context

Users need to create accounts and login via multiple authentication providers rather than relying on environment-based configuration.

### Decision

**Implement multi-provider OAuth with manual signup fallback:**

### Supported Auth Providers

| Provider | OAuth Version | Priority | Implementation |
|----------|---------------|----------|----------------|
| **GitHub** | OAuth 2.0 | CRITICAL | github_auth.py |
| **Google** | OAuth 2.0 + OIDC | CRITICAL | google_auth.py |
| **Microsoft** | OAuth 2.0 + Azure AD | CRITICAL | microsoft_auth.py |
| **Manual** | Email/Password | CRITICAL | manual_auth.py |

### Architecture

```python
from abc import ABC, abstractmethod

class AuthProvider(ABC):
    """Abstract base for authentication providers."""
    
    @abstractmethod
    async def initiate_auth(self) -> AuthURL:
        """Start OAuth flow, return redirect URL."""
        pass
    
    @abstractmethod
    async def handle_callback(self, code: str) -> AuthResult:
        """Handle OAuth callback, return user info."""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh expired access token."""
        pass
    
    @abstractmethod
    async def get_user_info(self, token: str) -> UserInfo:
        """Get user profile from provider."""
        pass


class AuthManager:
    """Manages authentication across all providers."""
    
    providers = {
        "github": GitHubAuthProvider(),
        "google": GoogleAuthProvider(),
        "microsoft": MicrosoftAuthProvider(),
        "manual": ManualAuthProvider(),
    }
    
    async def login(self, provider: str, **kwargs) -> AuthResult:
        """Authenticate user via specified provider."""
        auth_provider = self.providers.get(provider)
        if not auth_provider:
            raise UnsupportedProvider(provider)
        
        return await auth_provider.authenticate(**kwargs)
    
    async def create_session(self, user: User) -> Session:
        """Create authenticated session for user."""
        session = Session(
            user_id=user.id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
        )
        await self.session_store.save(session)
        return session
```

### User Account Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Account Creation | Via OAuth or manual signup | CRITICAL |
| Profile Management | Name, avatar, preferences | HIGH |
| LLM Credentials | Per-user provider API keys | CRITICAL |
| Session Management | Multi-device, secure tokens | HIGH |
| Password Reset | For manual accounts | HIGH |

### Rationale

1. **User Control**: Users own their accounts and credentials
2. **Provider Flexibility**: Choose login method based on preference
3. **Enterprise Ready**: Microsoft OAuth for corporate environments
4. **Privacy Option**: Manual signup for users avoiding OAuth

### Consequences

1. **Database Required**: User data storage (SQLite/PostgreSQL)
2. **OAuth Setup**: App registration with each provider
3. **Security Responsibility**: Session management, token handling

### Status: APPROVED (Critical Priority)

---

## ADR-013: Per-Agent LLM Configuration

> ⚠️ **NEW ADR** - Enables per-agent model assignment

### Context

Users want to assign different LLM models to different agents based on task requirements, cost, or capability.

### Decision

**Implement per-agent LLM configuration with hierarchical defaults:**

### Configuration Hierarchy

```
Global Default → Agent Type Default → Individual Agent → Task Override
```

| Level | Scope | Example |
|-------|-------|---------|
| **Global Default** | All agents | `openrouter/claude-3-opus` |
| **Agent Type Default** | Category of agents | Security agents → `openai/gpt-4` |
| **Individual Agent** | Specific agent | `RedTeamAgent` → `ollama/llama-3` |
| **Task Override** | Single task | This task → `gemini/pro` |

### Configuration Schema

```python
@dataclass
class AgentLLMConfig:
    """Per-agent LLM configuration."""
    
    agent_id: str                        # Agent identifier
    provider: str                        # e.g., "openrouter", "ollama"
    model: str                           # e.g., "gpt-4", "llama-3"
    fallback_providers: List[str]        # Ordered fallback chain
    max_tokens: int = 4096               # Token limit
    temperature: float = 0.7             # Model temperature
    cost_budget_daily: Optional[float]   # Daily cost limit (USD)
    enabled: bool = True                 # Whether agent is active
    
    @classmethod
    def from_defaults(cls, agent_id: str, defaults: GlobalConfig):
        """Create config using global defaults."""
        return cls(
            agent_id=agent_id,
            provider=defaults.default_provider,
            model=defaults.default_model,
            fallback_providers=defaults.fallback_chain,
        )


class AgentConfigManager:
    """Manages per-agent LLM configurations."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.configs: Dict[str, AgentLLMConfig] = {}
    
    async def get_config(self, agent_id: str) -> AgentLLMConfig:
        """Get LLM config for agent, applying hierarchy."""
        # Check individual config
        if agent_id in self.configs:
            return self.configs[agent_id]
        
        # Check agent type default
        agent_type = self._get_agent_type(agent_id)
        type_config = await self._get_type_default(agent_type)
        if type_config:
            return type_config
        
        # Use global default
        return await self._get_global_default()
    
    async def set_config(self, agent_id: str, config: AgentLLMConfig):
        """Set or update agent LLM configuration."""
        self.configs[agent_id] = config
        await self._persist_config(agent_id, config)
```

### UI Requirements

| Feature | Description |
|---------|-------------|
| Provider Selector | Dropdown of configured providers |
| Model Browser | Browse/search available models per provider |
| Agent Assignment | Drag-drop or select to assign models |
| Cost Preview | Estimated cost based on configuration |
| Batch Update | Update multiple agents at once |
| Import/Export | Save/load configurations |

### Example Configurations

```yaml
# User's agent configurations
agents:
  # Global default
  _default:
    provider: openrouter
    model: anthropic/claude-3-sonnet
    fallback_providers: [ollama, openai]
  
  # Security agents use GPT-4 for analysis
  SecurityArchitectAgent:
    provider: openai
    model: gpt-4
    temperature: 0.3
    
  RedTeamAgent:
    provider: openai
    model: gpt-4
    temperature: 0.5
  
  # Coding agents use local Llama for speed
  CoderAgent:
    provider: ollama
    model: codellama:34b
    max_tokens: 8192
  
  # Documentation uses Gemini for long context
  DocumentationLeadAgent:
    provider: gemini
    model: gemini-pro
    max_tokens: 32000
```

### Rationale

1. **Cost Optimization**: Use cheaper models for simpler tasks
2. **Capability Matching**: Match model strengths to task requirements
3. **Privacy Control**: Use local models for sensitive code
4. **Experimentation**: Easy A/B testing of different models

### Consequences

1. **Configuration Complexity**: Users need to understand model differences
2. **UI Required**: Need intuitive configuration interface
3. **Validation Needed**: Ensure selected models support required features

### Status: APPROVED (Critical Priority)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-05 | Initial 11 ADRs |
| 2.0.0 | 2026-01-05 | Updated ADR-005 for LLM-agnostic, added ADR-012 (Multi-Auth), ADR-013 (Per-Agent LLM) |

---

*Document Version: 2.0.0*
*Last Updated: January 5, 2026*
