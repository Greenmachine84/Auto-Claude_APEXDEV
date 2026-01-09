"""DEVAPEX Agent System.

Comprehensive agent architecture implementing PHASE1_AGENT_SYSTEM_ARCHITECTURE.md.

Modules:
- types: Foundation types (AgentType, Priority, AgentStatus, AgentResult)
- base: Base agent infrastructure (BaseAgent, AgentConfig, ExecutionContext)
- registry: Agent registration and factory patterns
- lifecycle: Agent pool, lifecycle management, supervision
- core: 4 core agents (Coder, Reviewer, Fixer, Orchestrator)
- enterprise: 16 enterprise agents across 6 categories

Usage:
    >>> from agents import AgentType, AgentFactory, CoderAgent
    >>> factory = AgentFactory()
    >>> coder = factory.create(AgentType.CODER)
    >>> coder.initialize()
    >>> result = coder.run(context)

20 Agents Total:
- Core (4): Coder, Reviewer, Fixer, Orchestrator
- Enterprise (16):
  - Architecture: Architect, SystemDesigner, Migration
  - Security: SecurityScanner, VulnerabilityAnalyzer, ComplianceChecker
  - Quality: TestGenerator, PerformanceAnalyzer, Coverage
  - Documentation: Documentation, APIDocumenter, ChangelogGenerator
  - API: APIDesigner, SchemaValidator
  - Orchestration: TaskCoordinator, WorkflowManager

APEX Constitution Compliant.
"""

# Types
# Base
from .base import (
    AUTO_CONTINUE_DELAY_SECONDS,
    HUMAN_INTERVENTION_FILE,
    AgentCapabilities,
    AgentConfig,
    AgentHooks,
    AgentStateManager,
    BaseAgent,
    ContextBuilder,
    ExecutionContext,
    HookType,
    ResourceLimits,
    hook,
    on_error,
    on_memory_store,
    post_execute,
    pre_execute,
)

# Coder
from .coder import run_autonomous_agent

# Core Agents
from .core import (
    CoderAgent,
    FixerAgent,
    OrchestratorAgent,
    ReviewerAgent,
)

# Enterprise Agents
from .enterprise import (
    APIDesignerAgent,
    APIDocumenterAgent,
    ArchitectAgent,
    ChangelogGeneratorAgent,
    ComplianceCheckerAgent,
    CoverageAgent,
    DocumentationAgent,
    MigrationAgent,
    PerformanceAnalyzerAgent,
    SchemaValidatorAgent,
    SecurityScannerAgent,
    SystemDesignerAgent,
    TaskCoordinatorAgent,
    TestGeneratorAgent,
    VulnerabilityAnalyzerAgent,
    WorkflowManagerAgent,
)

# Lifecycle
from .lifecycle import (
    AgentPool,
    AgentSupervisor,
    LifecycleEvent,
    LifecycleManager,
    PoolConfig,
    SupervisorConfig,
)

# Memory Management
from .memory_manager import (
    debug_memory_system_status,
    get_graphiti_context,
    save_session_memory,
    save_session_to_graphiti,
)

# Planner
from .planner import run_followup_planner

# Registry
from .registry import (
    AgentCatalog,
    AgentFactory,
    AgentMetadata,
    AgentRegistry,
    create_agent,
    get_registry,
)

# Session Management
from .session import (
    post_session_processing,
    run_agent_session,
)
from .types import (
    AGENT_CATEGORY_MAP,
    AgentCategory,
    AgentResult,
    AgentStatus,
    AgentType,
    ErrorCode,
    ErrorResult,
    InvalidStatusTransitionError,
    PartialResult,
    Priority,
    SuccessResult,
)

# Utilities
from .utils import (
    find_phase_for_subtask,
    find_subtask_in_plan,
    get_commit_count,
    get_latest_commit,
    load_implementation_plan,
    sync_spec_to_source,
)

__version__ = "1.0.0"

__all__ = [
    # Version
    "__version__",
    # Types
    "AgentType",
    "AgentCategory",
    "AGENT_CATEGORY_MAP",
    "Priority",
    "AgentStatus",
    "InvalidStatusTransitionError",
    "AgentResult",
    "SuccessResult",
    "ErrorResult",
    "PartialResult",
    "ErrorCode",
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentCapabilities",
    "ResourceLimits",
    "AgentStateManager",
    "ExecutionContext",
    "ContextBuilder",
    "AgentHooks",
    "HookType",
    "hook",
    "pre_execute",
    "post_execute",
    "on_error",
    "on_memory_store",
    # Registry
    "AgentRegistry",
    "get_registry",
    "AgentFactory",
    "create_agent",
    "AgentCatalog",
    "AgentMetadata",
    # Lifecycle
    "AgentPool",
    "PoolConfig",
    "LifecycleManager",
    "LifecycleEvent",
    "AgentSupervisor",
    "SupervisorConfig",
    # Core Agents
    "CoderAgent",
    "ReviewerAgent",
    "FixerAgent",
    "OrchestratorAgent",
    # Enterprise Agents
    "ArchitectAgent",
    "SystemDesignerAgent",
    "MigrationAgent",
    "SecurityScannerAgent",
    "VulnerabilityAnalyzerAgent",
    "ComplianceCheckerAgent",
    "TestGeneratorAgent",
    "PerformanceAnalyzerAgent",
    "CoverageAgent",
    "DocumentationAgent",
    "APIDocumenterAgent",
    "ChangelogGeneratorAgent",
    "APIDesignerAgent",
    "SchemaValidatorAgent",
    "TaskCoordinatorAgent",
    "WorkflowManagerAgent",
]
