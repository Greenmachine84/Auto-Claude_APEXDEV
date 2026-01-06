# Phase 5: Testing, Security & Documentation Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 5 of 5 | File/Folder Architecture Specification
> Created: January 6, 2026

---

## Overview

Phase 5 establishes comprehensive testing infrastructure, security framework, and documentation system. This includes unit/integration/e2e tests, security scanning, audit logging, and automated documentation generation.

---

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                        # Pytest configuration
├── pytest.ini                         # Pytest settings
│
├── unit/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── test_base_agent.py         # Base agent tests
│   │   ├── test_coder_agent.py        # Coder agent tests
│   │   ├── test_reviewer_agent.py     # Reviewer tests
│   │   ├── test_fixer_agent.py        # Fixer tests
│   │   ├── test_agent_registry.py     # Registry tests
│   │   ├── test_agent_factory.py      # Factory tests
│   │   └── test_agent_lifecycle.py    # Lifecycle tests
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── test_episode_store.py      # Episode storage tests
│   │   ├── test_episode_query.py      # Query builder tests
│   │   ├── test_semantic_search.py    # Semantic search tests
│   │   ├── test_hmem_tiers.py         # H-MEM tier tests
│   │   └── test_context_builder.py    # Context builder tests
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── test_llm_client.py         # LLM client tests
│   │   ├── test_llm_router.py         # Router tests
│   │   ├── test_model_selector.py     # Model selection tests
│   │   ├── test_prompt_template.py    # Template tests
│   │   └── test_tool_executor.py      # Tool execution tests
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── test_skill_registry.py     # Skill registry tests
│   │   ├── test_skill_executor.py     # Executor tests
│   │   ├── test_coding_skills.py      # Coding skill tests
│   │   └── test_review_skills.py      # Review skill tests
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── test_tool_registry.py      # Tool registry tests
│   │   ├── test_tool_permissions.py   # Permission tests
│   │   ├── test_tool_sandbox.py       # Sandbox tests
│   │   ├── test_filesystem_tools.py   # FS tool tests
│   │   └── test_git_tools.py          # Git tool tests
│   │
│   └── orchestrator/
│       ├── __init__.py
│       ├── test_task_queue.py         # Queue tests
│       ├── test_agent_pool.py         # Pool tests
│       ├── test_workflow_engine.py    # Workflow tests
│       ├── test_dispatcher.py         # Dispatcher tests
│       └── test_result_collector.py   # Result tests
│
├── integration/
│   ├── __init__.py
│   │
│   ├── test_agent_memory.py           # Agent + Memory integration
│   ├── test_agent_llm.py              # Agent + LLM integration
│   ├── test_orchestrator_agents.py    # Orchestrator + Agents
│   ├── test_workflow_execution.py     # Full workflow execution
│   ├── test_skill_tool_chain.py       # Skill + Tool chain
│   ├── test_memory_persistence.py     # Memory persistence
│   └── test_ipc_communication.py      # IPC integration
│
├── e2e/
│   ├── __init__.py
│   │
│   ├── test_task_lifecycle.py         # Full task lifecycle
│   ├── test_code_generation_flow.py   # Code gen end-to-end
│   ├── test_review_fix_cycle.py       # Review-fix cycle
│   ├── test_multi_agent_workflow.py   # Multi-agent coordination
│   └── test_external_integrations.py  # GitHub/GitLab/etc.
│
├── fixtures/
│   ├── __init__.py
│   ├── agent_fixtures.py              # Agent test fixtures
│   ├── task_fixtures.py               # Task test fixtures
│   ├── memory_fixtures.py             # Memory test fixtures
│   ├── llm_fixtures.py                # LLM mock fixtures
│   └── sample_code_fixtures.py        # Sample code for tests
│
└── mocks/
    ├── __init__.py
    ├── mock_llm_client.py             # Mock LLM responses
    ├── mock_memory_store.py           # Mock memory
    ├── mock_tool_executor.py          # Mock tool execution
    └── mock_external_apis.py          # Mock GitHub/GitLab

apps/
└── backend/
    ├── security/
    │   ├── __init__.py                    # Security exports
    │   │
    │   ├── core/
    │   │   ├── __init__.py                # Core security exports
    │   │   ├── security_manager.py        # Central security coordinator
    │   │   ├── security_config.py         # Security configuration
    │   │   └── security_context.py        # Security context
    │   │
    │   ├── scanning/
    │   │   ├── __init__.py                # Scanning exports
    │   │   ├── secret_scanner.py          # Secret detection
    │   │   ├── vulnerability_scanner.py   # CVE/SAST scanning
    │   │   ├── dependency_scanner.py      # Dependency vulnerabilities
    │   │   ├── code_scanner.py            # Static analysis
    │   │   └── scan_report.py             # Scan report generation
    │   │
    │   ├── audit/
    │   │   ├── __init__.py                # Audit exports
    │   │   ├── audit_logger.py            # Audit event logging
    │   │   ├── audit_store.py             # Audit log storage
    │   │   ├── audit_query.py             # Audit log querying
    │   │   └── compliance_reporter.py     # Compliance reports
    │   │
    │   ├── auth/
    │   │   ├── __init__.py                # Auth exports
    │   │   ├── auth_manager.py            # Authentication manager
    │   │   ├── token_manager.py           # API token management
    │   │   ├── oauth_handler.py           # OAuth flows
    │   │   └── credential_store.py        # Secure credential storage
    │   │
    │   ├── encryption/
    │   │   ├── __init__.py                # Encryption exports
    │   │   ├── crypto_manager.py          # Encryption/decryption
    │   │   ├── key_manager.py             # Key management
    │   │   └── secure_storage.py          # Encrypted storage
    │   │
    │   ├── validation/
    │   │   ├── __init__.py                # Validation exports
    │   │   ├── input_validator.py         # Input sanitization
    │   │   ├── output_validator.py        # Output validation
    │   │   ├── prompt_injection_guard.py  # Prompt injection defense
    │   │   └── content_filter.py          # Content filtering
    │   │
    │   └── types/
    │       ├── __init__.py                # Type exports
    │       ├── security_types.py          # Security enums/types
    │       ├── audit_types.py             # Audit event types
    │       └── permission_types.py        # Permission types
    │
    └── documentation/
        ├── __init__.py                    # Doc exports
        │
        ├── generators/
        │   ├── __init__.py                # Generator exports
        │   ├── api_doc_generator.py       # API documentation
        │   ├── schema_doc_generator.py    # Schema documentation
        │   ├── agent_doc_generator.py     # Agent documentation
        │   ├── tool_doc_generator.py      # Tool documentation
        │   └── skill_doc_generator.py     # Skill documentation
        │
        ├── templates/
        │   ├── __init__.py                # Template exports
        │   ├── markdown_template.py       # Markdown generator
        │   ├── html_template.py           # HTML generator
        │   └── openapi_template.py        # OpenAPI spec generator
        │
        ├── builders/
        │   ├── __init__.py                # Builder exports
        │   ├── readme_builder.py          # README generation
        │   ├── changelog_builder.py       # Changelog generation
        │   ├── decision_builder.py        # ADR generation
        │   └── user_guide_builder.py      # User guide generation
        │
        └── types/
            ├── __init__.py                # Type exports
            ├── doc_types.py               # Documentation types
            └── template_types.py          # Template types

docs/
├── api/
│   ├── README.md                      # API docs index
│   ├── agents-api.md                  # Agent API reference
│   ├── memory-api.md                  # Memory API reference
│   ├── llm-api.md                     # LLM API reference
│   ├── tools-api.md                   # Tools API reference
│   ├── skills-api.md                  # Skills API reference
│   ├── orchestrator-api.md            # Orchestrator API reference
│   └── integrations-api.md            # Integrations API reference
│
├── guides/
│   ├── README.md                      # Guides index
│   ├── getting-started.md             # Quick start guide
│   ├── installation.md                # Installation guide
│   ├── configuration.md               # Configuration guide
│   ├── creating-tasks.md              # Task creation guide
│   ├── using-agents.md                # Agent usage guide
│   ├── custom-workflows.md            # Workflow customization
│   ├── integrations-setup.md          # Integration setup
│   └── troubleshooting.md             # Troubleshooting guide
│
├── architecture/
│   ├── README.md                      # Architecture overview
│   ├── PHASE1_*.md                    # (already created)
│   ├── PHASE2_*.md                    # (already created)
│   ├── PHASE3_*.md                    # (already created)
│   ├── PHASE4_*.md                    # (already created)
│   └── PHASE5_*.md                    # (this file)
│
├── security/
│   ├── README.md                      # Security overview
│   ├── security-model.md              # Security model
│   ├── authentication.md              # Auth documentation
│   ├── authorization.md               # Authorization model
│   ├── audit-logging.md               # Audit log documentation
│   └── prompt-injection-defense.md    # Prompt injection defense
│
└── development/
    ├── README.md                      # Development overview
    ├── contributing.md                # Contribution guide
    ├── coding-standards.md            # Coding standards
    ├── testing-guide.md               # Testing guide
    ├── release-process.md             # Release process
    └── architecture-decisions.md      # ADR guide
```

---

## File Specifications

### 1. Test Infrastructure

#### `conftest.py`
**Purpose**: Pytest configuration and shared fixtures
**Key Components**:
```python
# Shared fixtures available to all tests
@pytest.fixture
def mock_llm_client() -> MockLLMClient

@pytest.fixture
def memory_store() -> EpisodeStore

@pytest.fixture
def agent_factory() -> AgentFactory

@pytest.fixture
def task_queue() -> TaskQueue
```

#### Unit Tests Structure

| Domain | Test Files | Coverage Target |
|--------|------------|----------------|
| Agents | 7 | Base, Core (4), Registry, Factory, Lifecycle |
| Memory | 5 | Store, Query, Semantic, H-MEM, Context |
| LLM | 5 | Client, Router, Selector, Template, Tools |
| Skills | 4 | Registry, Executor, Coding, Review |
| Tools | 5 | Registry, Permissions, Sandbox, FS, Git |
| Orchestrator | 5 | Queue, Pool, Workflow, Dispatch, Results |

#### Integration Tests

| Test File | Integration Points | Purpose |
|-----------|-------------------|--------|
| `test_agent_memory.py` | Agent + Memory | Episode storage on agent run |
| `test_agent_llm.py` | Agent + LLM | LLM calls from agents |
| `test_orchestrator_agents.py` | Orchestrator + Pool | Task dispatch to agents |
| `test_workflow_execution.py` | All | Complete workflow flow |
| `test_skill_tool_chain.py` | Skills + Tools | Skill using tools |
| `test_memory_persistence.py` | Memory + SQLite | Data persistence |
| `test_ipc_communication.py` | Electron + Backend | IPC message flow |

#### E2E Tests

| Test File | Scenario | Duration |
|-----------|----------|----------|
| `test_task_lifecycle.py` | Create → Execute → Complete | ~30s |
| `test_code_generation_flow.py` | Spec → Generate → Review | ~60s |
| `test_review_fix_cycle.py` | Code → Review → Fix → Verify | ~120s |
| `test_multi_agent_workflow.py` | MDA orchestration | ~180s |
| `test_external_integrations.py` | GitHub PR flow | ~60s |

---

### 2. Security Module (`security/`)

#### Core Security (`security/core/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `security_manager.py` | Central coordinator | `check_permission()`, `validate_input()`, `audit_log()` |
| `security_config.py` | Security settings | `get_setting()`, `set_policy()` |
| `security_context.py` | Request context | `get_user()`, `get_permissions()` |

#### Security Scanning (`security/scanning/`)

| File | Scanner Type | Detection |
|------|--------------|----------|
| `secret_scanner.py` | Secrets | API keys, passwords, tokens |
| `vulnerability_scanner.py` | CVEs | Known vulnerabilities |
| `dependency_scanner.py` | Dependencies | Vulnerable packages |
| `code_scanner.py` | SAST | Code issues, patterns |
| `scan_report.py` | Reporting | Aggregate scan results |

**Secret Scanner Patterns**:
```python
PATTERNS = [
    r'AKIA[0-9A-Z]{16}',           # AWS Access Key
    r'ghp_[a-zA-Z0-9]{36}',         # GitHub Token
    r'sk-[a-zA-Z0-9]{48}',          # OpenAI Key
    r'xox[baprs]-[0-9a-zA-Z-]+',    # Slack Token
    # ... more patterns
]
```

#### Audit System (`security/audit/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `audit_logger.py` | Event logging | `log_event()`, `log_action()` |
| `audit_store.py` | Log storage | `store()`, `query()`, `rotate()` |
| `audit_query.py` | Log querying | `find_by_user()`, `find_by_action()` |
| `compliance_reporter.py` | Reports | `generate_report()`, `export()` |

**Audit Event Schema**:
```python
@dataclass
class AuditEvent:
    id: str
    timestamp: datetime
    user: str
    action: str
    resource: str
    details: Dict[str, Any]
    outcome: str  # success, failure, error
    ip_address: Optional[str]
```

#### Authentication (`security/auth/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `auth_manager.py` | Auth coordinator | `authenticate()`, `authorize()` |
| `token_manager.py` | API tokens | `generate()`, `validate()`, `revoke()` |
| `oauth_handler.py` | OAuth flows | `start_flow()`, `handle_callback()` |
| `credential_store.py` | Credential storage | `store()`, `retrieve()`, `delete()` |

#### Encryption (`security/encryption/`)

| File | Purpose | Algorithms |
|------|---------|------------|
| `crypto_manager.py` | Encryption ops | AES-256-GCM, ChaCha20 |
| `key_manager.py` | Key management | Key derivation, rotation |
| `secure_storage.py` | Encrypted storage | File and DB encryption |

#### Input/Output Validation (`security/validation/`)

| File | Purpose | Key Features |
|------|---------|-------------|
| `input_validator.py` | Input sanitization | XSS prevention, size limits |
| `output_validator.py` | Output validation | PII redaction, format check |
| `prompt_injection_guard.py` | Prompt security | Injection detection, blocking |
| `content_filter.py` | Content filtering | Harmful content detection |

**Prompt Injection Guard**:
```python
class PromptInjectionGuard:
    def check(self, input_text: str) -> ValidationResult:
        """Detect and block prompt injection attempts"""
        
    def sanitize(self, input_text: str) -> str:
        """Sanitize input to remove injection patterns"""
        
    def wrap_user_input(self, input_text: str) -> str:
        """Wrap user input with delimiters for safety"""
```

---

### 3. Documentation Module (`documentation/`)

#### Documentation Generators (`documentation/generators/`)

| File | Generates | Output Format |
|------|-----------|---------------|
| `api_doc_generator.py` | API reference | Markdown, HTML |
| `schema_doc_generator.py` | Data models | Markdown |
| `agent_doc_generator.py` | Agent docs | Markdown |
| `tool_doc_generator.py` | Tool reference | Markdown |
| `skill_doc_generator.py` | Skill reference | Markdown |

**API Doc Generator**:
```python
class APIDocGenerator:
    def generate_from_module(self, module: ModuleType) -> str
    def generate_from_class(self, cls: Type) -> str
    def generate_from_function(self, func: Callable) -> str
    def generate_openapi_spec(self) -> dict
```

#### Templates (`documentation/templates/`)

| File | Template Type | Features |
|------|---------------|----------|
| `markdown_template.py` | Markdown | TOC, code blocks, tables |
| `html_template.py` | HTML | Styled, searchable |
| `openapi_template.py` | OpenAPI 3.0 | Full spec generation |

#### Documentation Builders (`documentation/builders/`)

| File | Builds | Content |
|------|--------|--------|
| `readme_builder.py` | README.md | Project overview |
| `changelog_builder.py` | CHANGELOG.md | Version history |
| `decision_builder.py` | ADRs | Architecture decisions |
| `user_guide_builder.py` | User guides | How-to documentation |

---

### 4. Documentation Files (`docs/`)

#### API Documentation (`docs/api/`)

| File | Content |
|------|--------|
| `agents-api.md` | Agent classes, methods, examples |
| `memory-api.md` | Memory store, search, context APIs |
| `llm-api.md` | LLM client, providers, prompts |
| `tools-api.md` | Tool definitions, execution |
| `skills-api.md` | Skill registry, execution |
| `orchestrator-api.md` | Queue, pool, workflow APIs |
| `integrations-api.md` | GitHub, GitLab, Linear APIs |

#### User Guides (`docs/guides/`)

| File | Content |
|------|--------|
| `getting-started.md` | Quick start (15 min) |
| `installation.md` | Detailed installation |
| `configuration.md` | Config options, env vars |
| `creating-tasks.md` | Task creation, priority |
| `using-agents.md` | Agent selection, monitoring |
| `custom-workflows.md` | Workflow DSL, templates |
| `integrations-setup.md` | External integrations |
| `troubleshooting.md` | Common issues, solutions |

#### Security Documentation (`docs/security/`)

| File | Content |
|------|--------|
| `security-model.md` | Security architecture |
| `authentication.md` | Auth methods, tokens |
| `authorization.md` | Permissions, roles |
| `audit-logging.md` | Audit trail, compliance |
| `prompt-injection-defense.md` | Injection prevention |

#### Development Documentation (`docs/development/`)

| File | Content |
|------|--------|
| `contributing.md` | How to contribute |
| `coding-standards.md` | Style guide, linting |
| `testing-guide.md` | Test writing guide |
| `release-process.md` | Release workflow |
| `architecture-decisions.md` | ADR process |

---

## Test Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|----------------|
| Agents (core) | 85% | 95% |
| Memory | 80% | 90% |
| LLM | 75% | 85% |
| Skills | 80% | 90% |
| Tools | 85% | 95% |
| Orchestrator | 80% | 90% |
| Security | 90% | 98% |
| **Overall** | **80%** | **90%** |

---

## CI/CD Integration

### Test Pipeline
```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    - pytest tests/unit/ --cov
  
  integration-tests:
    - pytest tests/integration/
  
  e2e-tests:
    - pytest tests/e2e/ --slow
  
  security-scan:
    - python -m security.scanning.runner
  
  docs-build:
    - python -m documentation.build
```

---

## Integration Points

### With All Previous Phases
- Tests cover all Phase 1-4 components
- Security wraps all sensitive operations
- Documentation generated from source

### APEX Compliance
- Audit logging mandatory
- Security scanning on all code
- Documentation auto-generated

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `tests/` | 3 | Config files |
| `tests/unit/agents/` | 8 | Agent unit tests |
| `tests/unit/memory/` | 6 | Memory unit tests |
| `tests/unit/llm/` | 6 | LLM unit tests |
| `tests/unit/skills/` | 5 | Skill unit tests |
| `tests/unit/tools/` | 6 | Tool unit tests |
| `tests/unit/orchestrator/` | 6 | Orchestrator tests |
| `tests/integration/` | 8 | Integration tests |
| `tests/e2e/` | 6 | E2E tests |
| `tests/fixtures/` | 6 | Test fixtures |
| `tests/mocks/` | 5 | Mock objects |
| `security/core/` | 4 | Security core |
| `security/scanning/` | 6 | Scanners |
| `security/audit/` | 5 | Audit system |
| `security/auth/` | 5 | Authentication |
| `security/encryption/` | 4 | Encryption |
| `security/validation/` | 5 | Validation |
| `security/types/` | 4 | Security types |
| `documentation/generators/` | 6 | Doc generators |
| `documentation/templates/` | 4 | Templates |
| `documentation/builders/` | 5 | Builders |
| `documentation/types/` | 3 | Doc types |
| `docs/api/` | 8 | API docs |
| `docs/guides/` | 9 | User guides |
| `docs/security/` | 6 | Security docs |
| `docs/development/` | 6 | Dev docs |
| **Total** | **145** | Phase 5 files |

---

## Project Completion Summary

### All Phases Complete

| Phase | Files | Focus |
|-------|-------|-------|
| Phase 1 | 37 | Agent System |
| Phase 2 | 58 | Memory & LLM |
| Phase 3 | 79 | Skills, Tools, Orchestration |
| Phase 4 | 132 | UI, Integrations, Analytics |
| Phase 5 | 145 | Testing, Security, Documentation |
| **TOTAL** | **451** | Complete System |

---

*Architecture specification complete. Ready for implementation.*
