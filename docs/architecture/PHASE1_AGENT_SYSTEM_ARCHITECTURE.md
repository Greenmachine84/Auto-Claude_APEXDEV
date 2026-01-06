# Phase 1: Agent System & Core Infrastructure Architecture

> **Auto-Claude_APEXDEV Enhancement Project**
> Phase 1 of 10 | File/Folder Architecture Specification
> Created: January 6, 2026

---

## Overview

Phase 1 establishes the foundational agent system architecture, incorporating DEVAPEX's comprehensive agent framework including 4 core agents and 16 enterprise agents.

---

## Directory Structure

```
apps/
└── backend/
    └── agents/
        ├── __init__.py                    # Agent system exports
        ├── base/
        │   ├── __init__.py                # Base module exports
        │   ├── base_agent.py              # Abstract base class for all agents
        │   ├── agent_config.py            # Agent configuration dataclasses
        │   ├── agent_state.py             # Agent state management
        │   ├── agent_context.py           # Execution context for agents
        │   ├── agent_result.py            # Standardized result types
        │   └── agent_hooks.py             # APEX lifecycle hooks
        │
        ├── core/
        │   ├── __init__.py                # Core agents exports
        │   ├── coder_agent.py             # Primary autonomous coding agent
        │   ├── reviewer_agent.py          # Automated code review agent
        │   ├── fixer_agent.py             # Automated issue resolution agent
        │   └── orchestrator_agent.py      # Task orchestration agent
        │
        ├── enterprise/
        │   ├── __init__.py                # Enterprise agents exports
        │   ├── base_enterprise_agent.py   # Enhanced base for enterprise agents
        │   │
        │   ├── architecture/
        │   │   ├── __init__.py
        │   │   ├── system_architect_agent.py      # Architecture design
        │   │   ├── refactor_architect_agent.py    # Code refactoring
        │   │   ├── performance_architect_agent.py # Performance optimization
        │   │   ├── integration_architect_agent.py # API/service integration
        │   │   ├── data_architect_agent.py        # Data modeling
        │   │   ├── cloud_architect_agent.py       # Cloud design
        │   │   └── devops_architect_agent.py      # CI/CD & infrastructure
        │   │
        │   ├── security/
        │   │   ├── __init__.py
        │   │   ├── security_architect_agent.py    # Security analysis
        │   │   ├── red_team_agent.py              # Adversarial testing
        │   │   └── blue_team_agent.py             # Defensive security
        │   │
        │   ├── quality/
        │   │   ├── __init__.py
        │   │   ├── qa_verification_agent.py       # Test planning & quality
        │   │   └── compliance_auditor_agent.py    # Regulatory compliance
        │   │
        │   ├── documentation/
        │   │   ├── __init__.py
        │   │   └── documentation_lead_agent.py    # Doc generation
        │   │
        │   ├── api/
        │   │   ├── __init__.py
        │   │   └── api_design_agent.py            # API design specialist
        │   │
        │   └── orchestration/
        │       ├── __init__.py
        │       └── mda_orchestrator_agent.py      # Multi-agent coordination
        │
        ├── registry/
        │   ├── __init__.py                # Registry exports
        │   ├── agent_registry.py          # Global agent type registry
        │   ├── agent_factory.py           # Agent instantiation factory
        │   └── agent_capabilities.py      # Capability declarations
        │
        ├── lifecycle/
        │   ├── __init__.py                # Lifecycle exports
        │   ├── agent_lifecycle.py         # Startup/shutdown management
        │   ├── health_check.py            # Agent health monitoring
        │   └── graceful_shutdown.py       # Clean termination handling
        │
        └── types/
            ├── __init__.py                # Type exports
            ├── agent_types.py             # AgentType enum and types
            ├── priority_types.py          # Priority level definitions
            ├── status_types.py            # Agent status enums
            └── result_types.py            # Result type definitions
```

---

## File Specifications

### 1. Base Module (`agents/base/`)

#### `base_agent.py`
**Purpose**: Abstract base class providing foundation for all agents
**Key Components**:
- `BaseAgent` abstract class
- Episode tracking integration
- Session management
- APEX lifecycle hooks (pre_execute, post_execute, on_error)
- Configuration validation
- Logging infrastructure

**Dependencies**: agent_config, agent_state, agent_context, agent_hooks

#### `agent_config.py`
**Purpose**: Configuration dataclasses for agent initialization
**Key Components**:
- `AgentConfig` dataclass
- `AgentCapabilities` dataclass
- `ResourceLimits` dataclass
- Configuration validation logic

#### `agent_state.py`
**Purpose**: Agent state management and transitions
**Key Components**:
- `AgentState` enum (IDLE, RUNNING, PAUSED, ERROR, TERMINATED)
- State transition validation
- State persistence interface

#### `agent_context.py`
**Purpose**: Execution context passed to agent operations
**Key Components**:
- `ExecutionContext` dataclass
- Task reference
- Memory access
- Tool permissions
- Parent agent reference (for MDA)

#### `agent_result.py`
**Purpose**: Standardized result types for agent operations
**Key Components**:
- `AgentResult` base class
- `SuccessResult`, `ErrorResult`, `PartialResult` types
- Result serialization

#### `agent_hooks.py`
**Purpose**: APEX Constitution lifecycle hooks
**Key Components**:
- `pre_execute()` hook
- `post_execute()` hook
- `on_error()` hook
- `on_memory_store()` hook
- Hook registration system

---

### 2. Core Agents Module (`agents/core/`)

#### `coder_agent.py`
**Purpose**: Primary autonomous coding agent
**Key Components**:
- LLM integration for code generation
- Tool calling capability
- File operations (read, write, modify)
- Git operations (commit, branch, diff)
- Episode tracking for learning
- APEX compliance validation

**Capabilities**:
- `CAN_READ_FILES`
- `CAN_WRITE_FILES`
- `CAN_EXECUTE_COMMANDS`
- `CAN_USE_GIT`
- `CAN_CALL_LLM`

#### `reviewer_agent.py`
**Purpose**: Automated code review with quality checks
**Key Components**:
- Severity categorization (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- APEX compliance checking
- Security vulnerability detection
- Code style analysis
- Review report generation

**Capabilities**:
- `CAN_READ_FILES`
- `CAN_ANALYZE_CODE`
- `CAN_CALL_LLM`

#### `fixer_agent.py`
**Purpose**: Automated issue resolution
**Key Components**:
- Review feedback parsing
- Automated fix generation
- Fix verification
- Rollback capability

**Capabilities**:
- `CAN_READ_FILES`
- `CAN_WRITE_FILES`
- `CAN_CALL_LLM`

#### `orchestrator_agent.py`
**Purpose**: Task distribution and workflow coordination
**Key Components**:
- Task queue management
- Agent selection logic
- Workflow state machine
- Result aggregation

**Capabilities**:
- `CAN_SPAWN_AGENTS`
- `CAN_MANAGE_TASKS`

---

### 3. Enterprise Agents Module (`agents/enterprise/`)

#### `base_enterprise_agent.py`
**Purpose**: Enhanced base class for enterprise-grade agents
**Key Components**:
- Extended logging and audit trail
- Enhanced error handling
- Compliance integration
- Cost tracking
- SLA monitoring

#### Architecture Submodule (`enterprise/architecture/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `system_architect_agent.py` | System design & patterns | `analyze_architecture()`, `recommend_patterns()`, `review_design()` |
| `refactor_architect_agent.py` | Technical debt reduction | `identify_debt()`, `plan_refactor()`, `execute_refactor()` |
| `performance_architect_agent.py` | Performance optimization | `profile_code()`, `benchmark()`, `optimize()` |
| `integration_architect_agent.py` | API/service integration | `design_api()`, `validate_protocol()`, `test_integration()` |
| `data_architect_agent.py` | Data modeling & migrations | `design_schema()`, `plan_migration()`, `validate_data()` |
| `cloud_architect_agent.py` | Cloud-native design | `design_infrastructure()`, `optimize_cost()`, `multi_cloud_strategy()` |
| `devops_architect_agent.py` | CI/CD & infrastructure | `design_pipeline()`, `configure_deployment()`, `setup_monitoring()` |

#### Security Submodule (`enterprise/security/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `security_architect_agent.py` | Security analysis | `analyze_vulnerabilities()`, `check_compliance()`, `security_review()` |
| `red_team_agent.py` | Adversarial testing | `penetration_test()`, `attack_simulation()`, `find_weaknesses()` |
| `blue_team_agent.py` | Defensive security | `detect_threats()`, `incident_response()`, `setup_monitoring()` |

#### Quality Submodule (`enterprise/quality/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `qa_verification_agent.py` | Test planning & QA | `plan_tests()`, `analyze_coverage()`, `verify_quality()` |
| `compliance_auditor_agent.py` | Regulatory compliance | `audit_code()`, `check_policy()`, `generate_report()` |

#### Documentation Submodule (`enterprise/documentation/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `documentation_lead_agent.py` | Documentation generation | `generate_api_docs()`, `create_user_guide()`, `update_readme()` |

#### API Submodule (`enterprise/api/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `api_design_agent.py` | API design specialist | `design_rest_api()`, `design_graphql()`, `version_api()` |

#### Orchestration Submodule (`enterprise/orchestration/`)

| File | Purpose | Key Methods |
|------|---------|-------------|
| `mda_orchestrator_agent.py` | Multi-agent coordination | `coordinate_agents()`, `manage_workflow()`, `aggregate_results()` |

---

### 4. Registry Module (`agents/registry/`)

#### `agent_registry.py`
**Purpose**: Global registry of all agent types
**Key Components**:
- Agent type registration
- Agent lookup by type/capability
- Dynamic agent discovery
- Singleton pattern implementation

#### `agent_factory.py`
**Purpose**: Factory for creating agent instances
**Key Components**:
- `create_agent(agent_type, config)` method
- Configuration injection
- Dependency resolution
- Instance caching (optional)

#### `agent_capabilities.py`
**Purpose**: Capability declarations and validation
**Key Components**:
- `Capability` enum
- Capability requirements per agent type
- Capability validation logic

---

### 5. Lifecycle Module (`agents/lifecycle/`)

#### `agent_lifecycle.py`
**Purpose**: Manage agent startup and shutdown
**Key Components**:
- `start_agent()` method
- `stop_agent()` method
- Lifecycle event emission
- Resource allocation/deallocation

#### `health_check.py`
**Purpose**: Monitor agent health
**Key Components**:
- Health check interface
- Heartbeat mechanism
- Failure detection
- Recovery triggering

#### `graceful_shutdown.py`
**Purpose**: Clean termination handling
**Key Components**:
- Shutdown signal handling
- In-flight task completion
- State persistence on shutdown
- Resource cleanup

---

### 6. Types Module (`agents/types/`)

#### `agent_types.py`
```python
class AgentType(Enum):
    # Core Agents
    CODER = "coder"
    REVIEWER = "reviewer"
    FIXER = "fixer"
    ORCHESTRATOR = "orchestrator"
    
    # Enterprise - Architecture
    SYSTEM_ARCHITECT = "system_architect"
    REFACTOR_ARCHITECT = "refactor_architect"
    PERFORMANCE_ARCHITECT = "performance_architect"
    INTEGRATION_ARCHITECT = "integration_architect"
    DATA_ARCHITECT = "data_architect"
    CLOUD_ARCHITECT = "cloud_architect"
    DEVOPS_ARCHITECT = "devops_architect"
    
    # Enterprise - Security
    SECURITY_ARCHITECT = "security_architect"
    RED_TEAM = "red_team"
    BLUE_TEAM = "blue_team"
    
    # Enterprise - Quality
    QA_VERIFICATION = "qa_verification"
    COMPLIANCE_AUDITOR = "compliance_auditor"
    
    # Enterprise - Documentation
    DOCUMENTATION_LEAD = "documentation_lead"
    
    # Enterprise - API
    API_DESIGN = "api_design"
    
    # Enterprise - Orchestration
    MDA_ORCHESTRATOR = "mda_orchestrator"
```

#### `priority_types.py`
```python
class Priority(Enum):
    CRITICAL = 0  # Immediate execution
    HIGH = 1      # Next in queue
    MEDIUM = 2    # Standard priority
    LOW = 3       # Background tasks
```

#### `status_types.py`
```python
class AgentStatus(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"
```

---

## Integration Points

### With Memory System (Phase 2)
- `BaseAgent` stores episodes via `MemoryBridge`
- Enterprise agents use `SemanticSearch` for context

### With LLM Integration (Phase 2)
- All agents receive `LLMClient` via dependency injection
- Model selection based on agent type and task complexity

### With Orchestration (Phase 3)
- `AgentRegistry` provides agent discovery for `TaskQueue`
- `AgentFactory` creates instances for `AgentPool`

### With UI (Phase 4)
- Agent status exposed via IPC for terminal grid
- Real-time updates via event emission

---

## APEX Compliance

### Constitution Adherence
- All agents implement APEX hooks
- Episode tracking is mandatory
- Memory-First principle enforced

### Governance
- Agent capabilities are declared and validated
- Enterprise agents include audit trails
- HITL (Human-In-The-Loop) hooks available

---

## File Count Summary

| Directory | File Count | Description |
|-----------|------------|-------------|
| `agents/base/` | 6 | Base infrastructure |
| `agents/core/` | 4 | Core agents |
| `agents/enterprise/` | 17 | Enterprise agents |
| `agents/registry/` | 3 | Agent registry |
| `agents/lifecycle/` | 3 | Lifecycle management |
| `agents/types/` | 4 | Type definitions |
| **Total** | **37** | Phase 1 files |

---

## Next Steps

→ Phase 2: Memory System & LLM Integration Architecture
