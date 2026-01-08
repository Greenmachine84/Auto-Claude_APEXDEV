# Changelog

## 3.7.3 - APEXDEV Branding Completion

### Branding Update
- Updated all EN/FR locale files with APEXDEV branding
- Onboarding wizard now shows Welcome to APEXDEV

### Dashboard Improvements
- Removed Phase 2-7 labels from Platform Features cards
- Updated subtitle to AI-powered autonomous development platform

### Documentation
- ADR-059: APEXDEV Branding Completion

## 3.7.3 - APEXDEV Branding Completion & UI Polish

### Branding Update

- **Locale Files Rebranded**
  - Updated all EN/FR locale files (dialogs, navigation, onboarding, settings, welcome)
  - Replaced all Auto Claude references with APEXDEV
  - Onboarding wizard now shows Welcome to APEXDEV

### Dashboard Improvements

- **Removed Phase Badges**
  - Removed Phase 2-7 labels from Platform Features cards
  - Updated subtitle to AI-powered autonomous development platform
  - Cleaner, more professional dashboard appearance

### Documentation
- ADR-059: APEXDEV Branding Completion

## 3.7.3 - APEXDEV Branding Completion & UI Polish

### 🎨 Complete Branding Update

- **Locale Files Rebranded**
  - Updated all EN/FR locale files (dialogs, navigation, onboarding, settings, welcome)
  - Replaced all "Auto Claude" references with "APEXDEV"
  - Onboarding wizard now shows "Welcome to APEXDEV"

### 🖥️ Dashboard Improvements

- **Removed Phase Badges**
  - Removed Phase 2-7 labels from Platform Features cards
  - Updated subtitle to "AI-powered autonomous development platform"
  - Cleaner, more professional dashboard appearance

### 📄 Documentation
- ADR-059: APEXDEV Branding Completion

## 3.7.2 - API Provider Updates

### 🔧 API Configuration

- **Updated API Provider Presets**
  - Added Google Gemini (https://generativelanguage.googleapis.com/v1beta)
  - Added GitHub Copilot (https://api.githubcopilot.com)
  - Removed GLM Global and GLM China providers
  - Retained Anthropic, OpenRouter, and Groq presets

- **Locale Updates**
  - Updated English and French locale files with new preset labels
  - Test coverage updated for new presets

### 📄 Documentation
- ADR-058: API Provider Updates



All notable changes to this project will be documented in this file.

## 3.7.1 - Complete APEXDEV Rebranding (Production Release)

### 🎨 Comprehensive Branding Update

Complete rebrand from "Auto-Claude" to "APEXDEV" across **160+ files**

- **Application Identity**
  - Window title: "APEXDEV - Autonomous Coding Platform"
  - App name: "APEXDEV" (Electron)
  - Package name: `APEXDEV-ui`
  - New sidebar logo with "D" icon and APEXDEV text

- **Color Theme Update (Indigo/Purple)**
  - Primary: Yellow (#D6D876) → Indigo (#6366F1)
  - Accent: Olive → Dark Indigo (#1E1B4B)
  - Updated dark mode, light mode, and dusk theme variants
  - Professional enterprise-grade color scheme

- **User Interface Components**
  - Sidebar branding and logo
  - Onboarding wizard (16 files)
  - GitHub/GitLab setup modals
  - Agent tools and configuration
  - OAuth flow components
  - All 55 test files updated

- **Service & API Branding**
  - GitHub PR review comments: "APEXDEV Review"
  - GitLab MR review comments: "APEXDEV MR Review"
  - User-Agent header: "APEXDEV-UI"
  - All error messages and logging

- **Documentation**
  - README.md - Main project documentation
  - CLAUDE.md - AI assistant guidelines
  - CONTRIBUTING.md - Contribution guidelines
  - RELEASE.md - Release process
  - CLI-USAGE.md - Command line guide
  - Linux installation guide

### 📂 Files Modified (160+)

| Category | Count | Description |
|----------|-------|-------------|
| UI Components | 30+ | React components, modals, wizards |
| Main Process | 20+ | Electron main, IPC handlers |
| Test Files | 55 | Unit and integration tests |
| Documentation | 10+ | README, guides, shared docs |
| Styles | 1 | globals.css theme variables |
| Configuration | 2 | package.json, index.html |

### 🏗️ Architecture Decision

See [ADR-049: APEXDEV Rebranding](shared_docs/decisions/ADR-049-APEXDEV-rebranding.md)

---
## 3.6.0 - Phase 10: Testing & Documentation Infrastructure

### ✨ New Features

- **Comprehensive Test Suite** (100+ test files)
  - Unit tests for all modules with 90%+ coverage target
  - Integration tests for cross-module functionality
  - End-to-end tests for complete workflows
  - LLM-agnostic test fixtures for all 8 providers

- **Test Infrastructure** (5 directories)
  - `tests/unit/`: Component-level unit tests
  - `tests/integration/`: Module integration tests
  - `tests/e2e/`: End-to-end workflow tests
  - `tests/fixtures/`: Shared test fixtures
  - `tests/mocks/`: Provider mocks for all 8 LLM providers

- **Quality Standards**
  - Parametrized tests for all 8 LLM providers
  - Zero flaky tests requirement (10 consecutive passes)
  - CI/CD pipeline integration
  - Financial-grade accuracy for cost tests

### 🏗️ Architecture

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures (all providers)
├── pytest.ini           # Pytest configuration
├── unit/                # Unit tests
├── integration/         # Integration tests
├── e2e/                 # End-to-end tests
├── fixtures/            # Test data
└── mocks/               # Provider mocks
```

### 📂 Files Added

| Directory | Files | Description |
|-----------|-------|-------------|
| tests/ | 100+ | Complete test infrastructure |
| tests/unit/ | 40+ | Unit test suites |
| tests/integration/ | 30+ | Integration tests |
| tests/e2e/ | 20+ | E2E workflow tests |
| tests/fixtures/ | 10+ | Shared test data |

### 📖 Documentation

- ADR-054: Phase 10 Testing & Documentation Complete
- Reference: `docs/architecture/PHASE10_TESTING_DOCUMENTATION_ARCHITECTURE.md`

---
## 3.5.0 - Phase 9: Governance Architecture Implementation

### ✨ New Features

- **Policy Engine** (5 files)
  - `policy_engine.py`: Rule-based access control with provider-specific policies
  - `policy_loader.py`: Policy configuration loading and validation
  - `provider_policies.py`: Per-provider governance policies for all 8 LLM providers
  - `rules.py`: Governance rule definitions and conditions
  - `conditions.py`: Rule condition evaluation engine

- **Approval Workflows** (4 files)
  - `approval_workflow.py`: Multi-step approval processes
  - `approval_request.py`: Approval request management
  - `escalation.py`: Escalation handling and notifications
  - `workflow_definitions.py`: Pre-defined workflow templates

- **Rate Limiting & Quotas** (4 files)
  - `rate_limiter.py`: Provider-aware rate limiting
  - `quota_manager.py`: Cost tracking and quota management
  - `throttle.py`: Request throttling strategies
  - `limit_storage.py`: Persistent limit tracking

- **Compliance & Audit** (4 files)
  - `compliance_logger.py`: SOC 2/GDPR ready audit trail
  - `audit_trail.py`: Complete audit logging
  - `data_retention.py`: Data retention policy enforcement
  - `reporting.py`: Compliance reporting generation

### 🏗️ Architecture

```
apps/backend/governance/
├── __init__.py          # Governance module exports
├── config.py            # Governance configuration
├── models.py            # Data models
├── policy/              # Policy engine (5 files)
├── workflow/            # Approval workflows (4 files)
├── limits/              # Rate limiting (4 files)
└── compliance/          # Audit & compliance (4 files)
```

### 📂 Files Added

| Module | Files | Description |
|--------|-------|-------------|
| governance/ | 3 | Core config, models |
| governance/policy/ | 5 | Policy engine |
| governance/workflow/ | 4 | Approval workflows |
| governance/limits/ | 4 | Rate limiting & quotas |
| governance/compliance/ | 4 | Audit & compliance |
| **Total** | **24** | **Complete governance infrastructure** |

### 📖 Documentation

- ADR-053: Phase 9 Governance Implementation Complete
- Reference: `docs/architecture/PHASE9_GOVERNANCE_ARCHITECTURE.md`

---
## 3.4.0 - Phase 8: Analytics & Tools Architecture Implementation

### ✨ New Features

- **Analytics Core** (3 files)
  - `__init__.py`: Analytics module exports
  - `config.py`: Analytics configuration with retention policies
  - `models.py`: Analytics data models for all 8 LLM providers

- **Metrics Collection** (4 files)
  - `collector.py`: Real-time event collection
  - `aggregator.py`: Metric aggregation with time windows
  - `time_series.py`: Time series data storage
  - `storage.py`: Metrics persistence layer

- **Cost Tracking** (4 files)
  - `cost_tracker.py`: Multi-provider cost tracking for all 8 providers
  - `pricing.py`: Provider-specific pricing models
  - `budget_manager.py`: Budget limits and alerts
  - `cost_report.py`: Cost reporting and export

- **Dashboard API** (4 files)
  - `api.py`: Dashboard REST endpoints
  - `data_builder.py`: Dashboard data construction
  - `chart_data.py`: Chart-ready data formats
  - `export.py`: CSV/JSON/PDF export

- **Provider Analytics** (3 files)
  - `provider_comparison.py`: Cross-provider performance comparison
  - `provider_metrics.py`: Per-provider usage metrics
  - `usage_optimizer.py`: Cost optimization recommendations

- **Tools System** (57 files across 11 modules)
  - `core/`: Base tool infrastructure
  - `builtin/`: Standard tools
  - `executor/`: Sandboxed execution
  - `filesystem/`: File operations
  - `git/`: Git operations
  - `terminal/`: Command execution
  - `web/`: HTTP requests
  - `search/`: Search capabilities
  - `registry/`: Tool registration
  - `types/`: Type definitions

### 🏗️ Architecture

```
apps/backend/
├── analytics/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── metrics/         # Metrics collection (4 files)
│   ├── cost/            # Cost tracking (4 files)
│   ├── dashboard/       # Dashboard API (4 files)
│   └── provider_analytics/  # Provider analytics (3 files)
│
└── tools/
    ├── __init__.py
    ├── config.py
    ├── models.py
    ├── core/            # Base infrastructure
    ├── builtin/         # Standard tools
    ├── executor/        # Sandboxed execution
    ├── filesystem/      # File operations
    ├── git/             # Git operations
    ├── terminal/        # Command execution
    ├── web/             # HTTP requests
    ├── search/          # Search capabilities
    ├── registry/        # Tool registration
    └── types/           # Type definitions
```

### 📂 Files Added

| Module | Files | Description |
|--------|-------|-------------|
| analytics/ | 3 | Core config, models |
| analytics/metrics/ | 4 | Metrics collection |
| analytics/cost/ | 4 | Cost tracking |
| analytics/dashboard/ | 4 | Dashboard API |
| analytics/provider_analytics/ | 3 | Provider analytics |
| tools/ | 57 | Complete tools system |
| **Total** | **79** | **Complete analytics & tools infrastructure** |

### 📖 Documentation

- ADR-052: Phase 8 Analytics & Tools Implementation Complete
- Reference: `docs/architecture/PHASE8_ANALYTICS_TOOLS_ARCHITECTURE.md`

---
# Changelog

## 3.7.2 - API Provider Updates

### 🔧 API Configuration

- **Updated API Provider Presets**
  - Added Google Gemini (https://generativelanguage.googleapis.com/v1beta)
  - Added GitHub Copilot (https://api.githubcopilot.com)
  - Removed GLM Global and GLM China providers
  - Retained Anthropic, OpenRouter, and Groq presets

- **Locale Updates**
  - Updated English and French locale files with new preset labels
  - Test coverage updated for new presets

### 📄 Documentation
- ADR-058: API Provider Updates



All notable changes to this project will be documented in this file.

## 3.3.0 - Phase 7: Enterprise Agents Architecture Implementation

### ✨ New Features

- **Core LLM-Agnostic Infrastructure** (3 files)
  - `config.py`: Per-agent LLM configuration with `AgentLLMConfig`, `EnterpriseAgentConfig`
  - `types.py`: Enterprise agent type definitions with `EnterpriseAgentType`, `Severity`, `AgentCapability`
  - `base_enterprise_agent.py`: LLM-agnostic base class with `complete()`, `complete_with_fallback()`
  - Full support for 8 LLM providers: copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
  - NO default provider - explicit configuration required (provider equality principle)

- **Code Review Module** (5 files)
  - `code_review_agent.py`: LLM-agnostic code review with PR/file review, style/security/performance checks
  - `review_result.py`: Structured review findings with severity, line references, suggestions
  - `review_prompts.py`: Language-specific code review prompts (Python, JavaScript, TypeScript, Go, Rust)
  - `severity_classifier.py`: Pattern-based severity classification with 20+ patterns
  - SOLID principle violation detection, dead code identification, complexity analysis

- **Security Module** (5 files)
  - `security_agent.py`: Security scanning with OWASP Top 10 compliance checking
  - `scan_result.py`: Structured security findings with CVE references, remediation guidance
  - `vulnerability_db.py`: 13 vulnerability patterns (SQL injection, XSS, path traversal, command injection, etc.)
  - `owasp_checker.py`: Complete OWASP 2021 Top 10 coverage with severity mapping
  - Provider-agnostic security analysis across all 8 LLM backends

- **QA Module** (5 files)
  - `qa_agent.py`: Test generation with 80%+ coverage target, test execution, coverage analysis
  - `test_generator.py`: Code-aware test skeleton generation with mocking support
  - `coverage_analyzer.py`: Coverage data parsing with improvement recommendations
  - `test_templates.py`: Framework templates for pytest, Jest, Vitest, Mocha, Go testing
  - Edge case generation, assertion suggestion, mock generation capabilities

- **Documentation Module** (5 files)
  - `documentation_agent.py`: Multi-style docstring generation (Google, NumPy, Sphinx)
  - `docstring_generator.py`: AST-aware docstring generation with type inference
  - `readme_generator.py`: Project README generation with badges, installation, usage sections
  - `api_doc_generator.py`: API documentation in Markdown and OpenAPI formats
  - Support for comprehensive documentation strategies

- **Project Analysis Module** (5 files)
  - `project_analyzer_agent.py`: Project structure analysis, tech debt assessment, refactoring recommendations
  - `dependency_mapper.py`: Dependency graph extraction with circular dependency detection
  - `architecture_extractor.py`: Architecture pattern detection (MVC, Clean, Hexagonal, Microservices)
  - `tech_debt_analyzer.py`: Technical debt scoring with prioritized recommendations
  - Code metrics, coupling analysis, pattern violation detection

- **Orchestration Module** (5 files)
  - `orchestrator_agent.py`: Multi-agent task coordination with result aggregation
  - `agent_coordinator.py`: Parallel, sequential, and dependency-based execution modes
  - `result_aggregator.py`: Result merging strategies (merge, vote, first, latest)
  - `pipeline_manager.py`: Pre-built pipelines for code review and documentation workflows
  - Standard pipelines: `code_review` (security→review→qa) and `documentation` (analysis→doc→readme)

- **Capabilities Module** (5 files)
  - `code_analysis.py`: Language-agnostic code analysis with metrics (complexity, functions, classes)
  - `test_generation.py`: Framework-aware test suite generation (pytest, Jest, Vitest, unittest)
  - `documentation.py`: Multi-format documentation output (Markdown, HTML, RST)
  - `collaboration.py`: Inter-agent messaging with task delegation, handoffs, conversations
  - Reusable capabilities shared across all enterprise agents

### 🏗️ Architecture

```
apps/backend/agents/enterprise/
├── __init__.py              # Main exports (60+ Phase 7 symbols)
├── config.py                # Per-agent LLM configuration
├── types.py                 # Enterprise agent type definitions
├── base_enterprise_agent.py # LLM-agnostic base class
├── code_review/             # Code review agents (5 files)
│   ├── __init__.py
│   ├── code_review_agent.py # Main review agent
│   ├── review_result.py     # Structured findings
│   ├── review_prompts.py    # Language-specific prompts
│   └── severity_classifier.py
├── security/                # Security agents (5 files)
│   ├── __init__.py
│   ├── security_agent.py    # Security scanner
│   ├── scan_result.py       # Security findings
│   ├── vulnerability_db.py  # Vulnerability patterns
│   └── owasp_checker.py     # OWASP compliance
├── qa/                      # QA agents (5 files)
│   ├── __init__.py
│   ├── qa_agent.py          # QA coordination
│   ├── test_generator.py    # Test skeleton generation
│   ├── coverage_analyzer.py # Coverage analysis
│   └── test_templates.py    # Framework templates
├── documentation/           # Documentation agents (5 files)
│   ├── __init__.py
│   ├── documentation_agent.py
│   ├── docstring_generator.py
│   ├── readme_generator.py
│   └── api_doc_generator.py
├── project_analysis/        # Project analysis (5 files)
│   ├── __init__.py
│   ├── project_analyzer_agent.py
│   ├── dependency_mapper.py
│   ├── architecture_extractor.py
│   └── tech_debt_analyzer.py
├── orchestration/           # Multi-agent coordination (5 files)
│   ├── __init__.py
│   ├── orchestrator_agent.py
│   ├── agent_coordinator.py
│   ├── result_aggregator.py
│   └── pipeline_manager.py
└── capabilities/            # Shared capabilities (5 files)
    ├── __init__.py
    ├── code_analysis.py
    ├── test_generation.py
    ├── documentation.py
    └── collaboration.py
```

### 🔒 LLM Provider Equality

- **8 Providers with Equal Support**: copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure
- **No Default Provider**: All agents require explicit provider configuration
- **Per-Agent Configuration**: Each agent can use different providers independently
- **Automatic Fallback**: Configurable fallback chain for resilience
- **Provider Validation**: Configuration validated at initialization, not runtime

### 📂 Files Added

| Module | Files | Description |
|--------|-------|-------------|
| enterprise/ | 3 | Core config, types, base class |
| enterprise/code_review/ | 5 | Code review agents |
| enterprise/security/ | 5 | Security scanning agents |
| enterprise/qa/ | 5 | QA and testing agents |
| enterprise/documentation/ | 5 | Documentation agents |
| enterprise/project_analysis/ | 5 | Project analysis agents |
| enterprise/orchestration/ | 5 | Multi-agent orchestration |
| enterprise/capabilities/ | 5 | Shared agent capabilities |
| **Total** | **38** | **Complete enterprise agents infrastructure** |

### 📖 Documentation

- ADR-051: Phase 7 Enterprise Agents Implementation Complete
- References: ADR-036 (Specialization), ADR-037 (Task Decomposition), ADR-044 (Provider Equality)

---

## 3.2.0 - Phase 6: Security Infrastructure Implementation

### ✨ New Features

- **Core Security Module** (3 files)
  - `models.py`: Domain models for threats, severity, audit actions, roles, credentials
  - `config.py`: Enterprise security configuration with environment-aware defaults
  - Full support for 8 LLM providers: copilot, openrouter, ollama, lmstudio, gemini, openai, anthropic, azure

- **Secrets Scanner** (6 files)
  - `secrets_scanner.py`: Multi-provider secrets detection with regex patterns
  - `prompt_injection.py`: Multi-layer defense with spotlighting technique
  - `code_scanner.py`: OWASP vulnerability detection (SQL injection, XSS, path traversal)
  - `pattern_registry.py`: Centralized pattern management for all providers
  - `sanitizer.py`: HTML, SQL, shell, and unicode sanitization
  - Provider-specific patterns for all 8 LLM API key formats

- **Encryption Module** (4 files)
  - `credential_vault.py`: Secure vault for all 8 LLM provider credentials
  - `key_manager.py`: PBKDF2-SHA256 with 600,000 iterations (OWASP 2023)
  - `crypto_utils.py`: AES-256-GCM encryption with FIPS 197 compliance
  - Support for credential rotation and audit logging

- **Audit Logging** (5 files)
  - `audit_logger.py`: Enterprise audit logging with immutable checksums
  - `event_types.py`: 50+ event types across security, access, data categories
  - `integrity_checker.py`: Cryptographic chain validation for tamper detection
  - `audit_storage.py`: Multi-backend storage with file-based implementation
  - SHA-256 event signing with optional chain linking

- **RBAC System** (5 files)
  - `role_manager.py`: Hierarchical role management with provider awareness
  - `permission_checker.py`: Fast permission evaluation with LRU caching
  - `policy_enforcer.py`: Declarative policy rules with condition handlers
  - `role_definitions.py`: 24+ permissions, 5 default roles
  - Provider-specific permissions (use_copilot, use_openai, etc.)

- **Validation Module** (5 files)
  - `input_validator.py`: LLM input validation with injection pre-screening
  - `output_validator.py`: PII detection/redaction (email, phone, SSN, CC, IP)
  - `schema_validator.py`: JSON Schema validation for structured data
  - `threat_detector.py`: Real-time signature-based threat detection with alerts
  - Rule-based validation with configurable thresholds

### 🔒 Security Compliance

- **OWASP LLM Top 10**: Full coverage including prompt injection defense
- **OWASP ASVS Level 2**: Cryptographic standards compliance
- **FIPS 197**: AES-256-GCM encryption algorithm
- **OWASP 2023**: PBKDF2-SHA256 with 600,000 iterations for key derivation

### 📂 Files Added

| Module | Files | Description |
|--------|-------|-------------|
| security/ | 3 | Core models, config, exports |
| security/scanner/ | 6 | Secrets, prompt injection, code scanning |
| security/encryption/ | 4 | Credential vault, key management |
| security/audit/ | 5 | Audit logging, integrity checking |
| security/rbac/ | 5 | Role-based access control |
| security/validation/ | 5 | Input/output validation |
| **Total** | **28** | **Complete security infrastructure** |

### 📖 Documentation

- ADR-050: Phase 6 Security Implementation Complete
- References: ADR-032 (Deduplication), ADR-033 (LLM-Agnostic), ADR-034 (Vault), ADR-035 (RBAC)

---

## 3.1.0 - Phase 5: Testing & Documentation Infrastructure

### ✨ New Features

- **Comprehensive Test Infrastructure** (65 files)
  - Unit tests for all core modules (42 files)
  - Integration tests for system interactions (8 files)
  - End-to-end tests for complete workflows (5 files)
  - Shared fixtures for consistent test setup (5 files)
  - Mock implementations for external dependencies (5 files)

- **Documentation Module** (18 files)
  - AST-based source code parsing for accurate extraction
  - Support for Google, NumPy, and reST docstring formats
  - Markdown and HTML output generation
  - Template-based rendering with Jinja2
  - Modular generator/exporter architecture

- **API Documentation** (8 files)
  - Complete API reference for agents, memory, tools, LLM providers
  - Configuration options documentation
  - Code examples for all public interfaces

- **User Guides** (6 files)
  - Getting started guide with quickstart examples
  - Agent development guide with best practices
  - Memory system guide with search patterns
  - LLM provider guide with configuration examples
  - Workflow orchestration guide

- **Security Documentation** (3 files)
  - Security architecture overview
  - Threat model with risk matrix and mitigations
  - Security best practices for deployment

- **Development Documentation** (3 files)
  - Contributing guide with workflow and standards
  - Testing guide with patterns and examples
  - ADR-049: Phase 5 Architecture Decision Record

### 🧪 Test Coverage

- Core agents: 90% coverage target
- Memory system: 85% coverage target
- Tool execution: 85% coverage target
- LLM providers: 75% coverage target
- All 166 integration/e2e tests passing

### 📖 Documentation

- ADR-049: Phase 5 Testing & Documentation System
- Complete API documentation for all modules
- Security threat model and best practices
- Developer onboarding documentation

---

## 3.0.0 - Phase 4: UI, Integrations & Analytics Architecture

### ✨ New Features

- **Complete Electron Frontend Rewrite**
  - Type-safe IPC layer with channels, handlers, and error handling
  - React 18+ with TypeScript strict mode
  - Zustand state management with devtools and persist middleware
  - CSS Variables theming (light/dark/system)

- **Enterprise Integrations**
  - GitHub integration with REST API, webhooks, and review support
  - GitLab integration with MR management and pipeline webhooks
  - Linear integration with GraphQL API and issue tracking
  - Slack integration with Block Kit messaging and notifications
  - JIRA integration with ADF document support and sprint tracking

- **Agent System**
  - 5 agent types: coder, reviewer, fixer, planner, analyst
  - Agent pool management with lifecycle controls
  - Performance metrics and success rate tracking

- **LLM Provider Support** (8 providers with equal support)
  - GitHub Copilot, OpenRouter, Ollama, LM Studio
  - Google Gemini, OpenAI, Anthropic, Azure OpenAI

- **UI Components**
  - Kanban board with drag-and-drop task management
  - Terminal emulator with XTerm.js integration
  - Visual workflow designer with node-based editing
  - Episodic memory viewer with semantic search
  - Analytics dashboard with usage charts and cost tracking
  - Comprehensive settings panels for all configurations

- **Developer Experience**
  - 132 new files with 12,000+ lines of TypeScript/Python
  - Full type safety across IPC boundaries
  - Production-ready webhook security for all integrations

### 📖 Documentation

- ADR-048: Phase 4 Architecture Decision Record
- Updated README with integration setup guides
- API documentation for all integration services

---

## 2.7.2 - Stability & Performance Enhancements

### ✨ New Features

- Added refresh button to Kanban board for manually reloading tasks
- Terminal dropdown with built-in and external options in task review
- Centralized CLI tool path management with customizable settings
- Files tab in task details panel for better file organization
- Enhanced PR review page with filtering capabilities
- GitLab integration support
- Automated PR review with follow-up support and structured outputs
- UI scale feature with 75-200% range for accessibility
- Python 3.12 bundled with packaged Electron app
- OpenRouter support as LLM/embedding provider
- Internationalization (i18n) system for multi-language support
- Flatpak packaging support for Linux
- Path-aware AI merge resolution with device code streaming

### 🛠️ Improvements

- Improved terminal experience with persistent state when switching projects
- Enhanced PR review with structured outputs and fork support
- Better UX for display and scaling changes
- Convert synchronous I/O to async operations in worktree handlers
- Enhanced logs for commit linting stage
- Remove top navigation bars for cleaner UI
- Enhanced PR detail area visual design
- Improved CLI tool detection with more language support
- Added iOS/Swift project detection
- Optimize performance by removing projectTabs from useEffect dependencies
- Improved Python detection and version validation for compatibility

### 🐛 Bug Fixes

- Fixed CI Python setup and PR status gate checks
- Fixed cross-platform CLI path detection and clearing in settings
- Preserve original task description after spec creation
- Fixed learning loop to retrieve patterns and gotchas from memory
- Resolved frontend lag and updated dependencies
- Fixed Content-Security-Policy to allow external HTTPS images
- Fixed PR review isolation by using temporary worktree
- Fixed Homebrew Python detection to prefer versioned Python over system python3
- Added support for Bun 1.2.0+ lock file format detection
- Fixed infinite re-render loop in task selection
- Fixed infinite loop in task detail merge preview loading
- Resolved Windows EINVAL error when opening worktree in VS Code
- Fixed fallback to prevent tasks stuck in ai_review status
- Fixed SDK permissions to include spec_dir
- Added --base-branch argument support to spec_runner
- Allow Windows to run CC PR Reviewer
- Fixed model selection to respect task_metadata.json
- Improved GitHub PR review by passing repo parameter explicitly
- Fixed electron-log imports with .js extension
- Fixed Swift detection order in project analyzer
- Prevent TaskEditDialog from unmounting when opened
- Fixed subprocess handling for Python paths with spaces
- Fixed file system race conditions and unused variables in security scanning
- Resolved Python detection and backend packaging issues
- Fixed version-specific links in README and pre-commit hooks
- Fixed task status persistence reverting on refresh
- Proper semver comparison for pre-release versions
- Use virtual environment Python for all services to fix dotenv errors
- Fixed explicit Windows System32 tar path for builds
- Added augmented PATH environment to all GitHub CLI calls
- Use PowerShell for tar extraction on Windows
- Added --force-local flag to tar on Windows
- Stop tracking spec files in git
- Fixed GitHub API calls with explicit GET method for comment fetches
- Support archiving tasks across all worktree locations
- Validated backend source path before using it
- Resolved spawn Python ENOENT error on Linux
- Fixed CodeQL alerts for uncontrolled command line
- Resolved GitHub follow-up review API issues
- Fixed relative path normalization to POSIX format
- Accepted bug_fix workflow_type alias during planning
- Added global spec numbering lock to prevent collisions
- Fixed ideation status sync
- Stopped running process when task status changes away from in_progress
- Removed legacy path from auto-claude source detection
- Resolved Python environment race condition

---

## 2.7.1 - Build Pipeline Enhancements

### 🛠️ Improvements

- Enhanced VirusTotal scan error handling in release workflow with graceful failure recovery and improved reporting visibility
- Refactored macOS build workflow to support both Intel and ARM64 architectures with notarization for Intel builds and improved artifact handling
- Streamlined CI/CD processes with updated caching strategies and enhanced error handling for external API interactions

### 📚 Documentation

- Clarified README documentation

---

## 2.7.0 - Tab Persistence & Memory System Modernization

### ✨ New Features

- Project tab bar with persistent tab management and GitHub organization initialization on project creation
- Task creation enhanced with @ autocomplete for agent profiles and improved drag-and-drop support
- Keyboard shortcuts and tooltips added to project tabs for better navigation
- Agent task restart functionality with new profile support for flexible task recovery
- Ollama embedding model support with automatic dimension detection for self-hosted deployments

### 🛠️ Improvements

- Memory system completely redesigned with embedded LadybugDB, eliminating Docker/FalkorDB dependency and improving performance
- Tab persistence implemented via IPC-based mechanism for reliable session state management
- Terminal environment improved by using virtual environment Python for proper terminal name generation
- AI merge operations timeout increased from 2 to 10 minutes for reliability with larger changes
- Merge operations now use stored baseBranch metadata for consistent branch targeting
- Memory configuration UI simplified and rebranded with improved Ollama integration and detection
- CI/CD workflows enhanced with code signing support and automated release process
- Cross-platform compatibility improved by replacing Unix shell syntax with portable git commands
- Python venv created in userData for packaged applications to ensure proper environment isolation

### 🐛 Bug Fixes

- Task title no longer blocks edit/close buttons in UI
- Tab persistence and terminal shortcuts properly scoped to prevent conflicts
- Agent profile fallback corrected from 'Balanced' to 'Auto (Optimized)'
- macOS notarization made optional and improved with private artifact storage
- Embedding provider changes now properly detected during migration
- Memory query CLI respects user's memory enabled flag
- CodeRabbit review issues and linting errors resolved across codebase
- F-string prefixes removed from strings without placeholders
- Import ordering fixed for ruff compliance
- Preview panel now receives projectPath prop correctly for image component functionality
- Default database path unified to ~/.apexdev/memories for consistency
- @lydell/node-pty build scripts compatibility improved for pnpm v10

---

## 2.6.0 - Multi-Provider Graphiti Support & Platform Fixes

### ✨ New Features

- **Google AI Provider for Graphiti**: Full Google AI (Gemini) support for both LLM and embeddings in the Memory Layer
- **Ollama LLM Provider in UI**: Add Ollama as an LLM provider option in Graphiti onboarding wizard
- **LLM Provider Selection UI**: Add provider selection dropdown to Graphiti setup wizard for flexible backend configuration
- **Per-Project GitHub Configuration**: UI clarity improvements for per-project GitHub org/repo settings

### 🛠️ Improvements

- Enhanced Graphiti provider factory to support Google AI alongside existing providers
- Updated env-handlers to properly populate graphitiProviderConfig from .env files
- Improved type definitions with proper Graphiti provider config properties in AppSettings
- Better API key loading when switching between providers in settings

### 🐛 Bug Fixes

- **node-pty Migration**: Replaced node-pty with @lydell/node-pty for prebuilt Windows binaries
- **GitHub Organization Support**: Fixed repository support for GitHub organization accounts
- **Asyncio Deprecation**: Fixed asyncio deprecation warning by using get_running_loop() instead of get_event_loop()
- Applied ruff formatting and fixed import sorting (I001) in Google provider files

---

## 2.5.5 - Enhanced Agent Reliability & Build Workflow

### ✨ New Features

- Required GitHub setup flow after Auto Claude initialization to ensure proper configuration
- Atomic log saving mechanism to prevent log file corruption during concurrent operations
- Per-session model and thinking level selection in insights management
- Multi-auth token support and ANTHROPIC_BASE_URL passthrough for flexible authentication
- Comprehensive DEBUG logging at Claude SDK invocation points for improved troubleshooting
- Auto-download of prebuilt node-pty binaries for Windows environments
- Enhanced merge workflow with current branch detection for accurate change previews
- Phase configuration module and enhanced agent profiles for improved flexibility
- Stage-only merge handling with comprehensive verification checks
- Authentication failure detection system with patterns and validation checks across agent pipeline

### 🛠️ Improvements

- Changed default agent profile from 'balanced' to 'auto' for more adaptive behavior
- Better GitHub issue tracking and improved user experience in issue management
- Improved merge preview accuracy using git diff counts for file statistics
- Preserved roadmap generation state when switching between projects
- Enhanced agent profiles with phase configuration support

### 🐛 Bug Fixes

- Resolved CI test failures and improved merge preview reliability
- Fixed CI failures related to linting, formatting, and tests
- Prevented dialog skip during project initialization flow
- Updated model IDs for Sonnet and Haiku to match current Claude versions
- Fixed branch namespace conflict detection to prevent worktree creation failures
- Removed duplicate LINEAR_API_KEY checks and consolidated imports
- Python 3.10+ version requirement enforced with proper version checking
- Prevented command injection vulnerabilities in GitHub API calls

---

## 2.5.0 - Roadmap Intelligence & Workflow Refinements

### ✨ New Features

- Interactive competitor analysis viewer for roadmap planning with real-time data visualization
- GitHub issue label mapping to task categories for improved organization and tracking
- GitHub issue comment selection in task creation workflow for better context integration
- TaskCreationWizard enhanced with drag-and-drop support for file references and inline @mentions
- Roadmap generation now includes stop functionality and comprehensive debug logging

### 🛠️ Improvements

- Refined visual drop zone feedback in file reference system for more subtle user guidance
- Remove auto-expand behavior for referenced files on draft restore to improve UX
- Always-visible referenced files section in TaskCreationWizard for better discoverability
- Drop zone wrapper added around main modal content area for improved drag-and-drop ergonomics
- Stuck task detection now enabled for ai_review status to better track blocked work
- Enhanced React component stability with proper key usage in RoadmapHeader and PhaseProgressIndicator

### 🐛 Bug Fixes

- Corrected CompetitorAnalysisViewer type definitions for proper TypeScript compliance
- Fixed multiple CodeRabbit review feedback items for improved code quality
- Resolved React key warnings in PhaseProgressIndicator component
- Fixed git status parsing in merge preview for accurate worktree state detection
- Corrected path resolution in runners for proper module imports and .env loading
- Resolved CI lint and TypeScript errors across codebase
- Fixed HTTP error handling and path resolution issues in core modules
- Corrected worktree test to match intended branch detection behavior
- Refined TaskReview component conditional rendering for proper staged task display

---

## 2.4.0 - Enhanced Cross-Platform Experience with OAuth & Auto-Updates

### ✨ New Features

- Claude account OAuth implementation on onboarding for seamless token setup
- Integrated release workflow with AI-powered version suggestion capabilities
- Auto-upgrading functionality supporting Windows, Linux, and macOS with automatic app updates
- Git repository initialization on app startup with project addition checks
- Debug logging for app updater to track update processes
- Auto-open settings to updates section when app update is ready

### 🛠️ Improvements

- Major Windows and Linux compatibility enhancements for cross-platform reliability
- Enhanced task status handling to support 'done' status in limbo state with worktree existence checks
- Better handling of lock files from worktrees upon merging
- Improved README documentation and build process
- Worktree manual deletion enforcement for early access safety

### 🐛 Bug Fixes

- Corrected git status parsing in merge preview functionality
- Fixed ESLint warnings and failing tests
- Fixed Windows/Linux Python handling for cross-platform compatibility
- Fixed Windows/Linux source path detection
- Refined TaskReview component conditional rendering for proper staged task display

---

## 2.3.2 - UI Polish & Build Improvements

### 🛠️ Improvements

- Restructured SortableFeatureCard badge layout for improved visual presentation
- Fixed spec runner path configuration for more reliable task execution

---

## 2.3.1 - Linux Compatibility Fix

### 🐛 Bug Fixes

- Resolved path handling issues on Linux systems for improved cross-platform compatibility

---

## 2.2.0 - Usage Monitoring & Merge Improvements

### ✨ New Features

- Add usage monitoring with profile swap detection to prevent cascading resource issues
- Option to stash changes before merge operations for safer branch integration
- Add hideCloseButton prop to DialogContent component for improved UI flexibility

### 🛠️ Improvements

- Enhance AgentManager to manage task context cleanup and preserve swapCount on restarts
- Improve changelog feature with version tracking, markdown/preview, and persistent styling options
- Refactor merge conflict handling to use branch names instead of commit hashes for better clarity
- Better handling of lock files during merge conflicts

### 🐛 Bug Fixes

- Fix worktree merge logic to correctly handle branch operations
- Fix spec_runner.py path resolution after move to runners/ directory
- Fix Discord release webhook failing on large changelogs
- Fix branch logic for merge AI operations

---

## 2.0.1 - Update & Terminal Improvements

### 🚀 New Features

- Update Check with Release URLs for easy access to release information
- Markdown Renderer for Release Notes in advanced settings
- Terminal Name Generator for improved terminal management

### 🔧 Improvements

- LLM Provider Naming updates in project settings
- IPC Handlers improved for external link management
- UI Simplification in App component
- Docker Infrastructure updates for FalkorDB service

---

## 2.0.0 - Major Platform Release

### New Features

- Task Integration with "Go to Task" functionality across UI
- File Explorer Panel with directory listing capabilities
- Terminal Task Selection with auto-context loading
- Task Archiving functionality
- Graphiti MCP Server Integration
- Roadmap Functionality for visualization and management

### Improvements

- File Tree Virtualization for improved performance
- Agent Parallelization for better task execution
- Enhanced Terminal Experience with task features
- Python Environment Detection before task execution
- Cleaner Version System
- Simpler Project Initialization

### Bug Fixes

- Fixed project settings bug
- Fixed insight UI sidebar
- Resolved Kanban and terminal integration issues

---

## 1.1.0 - Task Enhancements

### New Features

- Follow-up Tasks for continuing work on completed specs
- Screenshot Support for Feedback with visual context
- Unified Task Editing with full options

### Improvements

- Enhanced Kanban Board visual design
- Screenshot Handling with Ctrl+V paste
- Draft Auto-Save to prevent work loss

### Bug Fixes

- Fixed task editing to support comprehensive options


## 2.3.0 - Phase 3: Skills & Orchestration Architecture

### ✨ New Features

- **Skills System** (20 files)
  - Modular skill interface with dynamic loading
  - 10 built-in skills: code generation, review, testing, research
  - Skill composition: pipelines, parallel, conditional

- **Orchestration Layer** (20 files)
  - Multi-agent coordination and task delegation
  - Workflow engine with checkpointing and recovery
  - Consensus protocols and conflict resolution

### 📖 Documentation

- ADR-047: Phase 3 Skills & Orchestration Complete
- Reference: `docs/architecture/PHASE3_SKILLS_TOOLS_ORCHESTRATION_ARCHITECTURE.md`

---
## 2.2.0 - Phase 2: Memory & LLM Architecture

### ✨ New Features

- **LLM Provider System** (24 files)
  - 8 provider implementations: Copilot, OpenRouter, Ollama, LM Studio, Gemini, OpenAI, Anthropic, Azure
  - Streaming, function calling, embeddings, vision support
  - Provider fallback chain and response normalization

- **Memory System** (14 files)
  - Short-term, long-term, semantic, and episodic memory
  - Multiple storage backends: file, SQLite, vector
  - Efficient semantic search with embeddings

### 📖 Documentation

- ADR-046: Phase 2 Memory & LLM Complete
- Reference: `docs/architecture/PHASE2_MEMORY_LLM_ARCHITECTURE.md`

---
## 2.1.0 - Phase 1: Agent System Architecture

### ✨ New Features

- **Agent Core** (28 files)
  - Base agent class with state machine lifecycle
  - Agent types: conversational, autonomous, reactive, planning, coding, review
  - Inter-agent communication with message bus
  - Agent lifecycle management: spawning, supervision, recovery

- **Provider Agnostic Design**
  - All agents work with any of the 8 LLM providers
  - Seamless provider switching without code changes

### 📖 Documentation

- ADR-045: Phase 1 Agent System Complete
- Reference: `docs/architecture/PHASE1_AGENT_SYSTEM_ARCHITECTURE.md`




