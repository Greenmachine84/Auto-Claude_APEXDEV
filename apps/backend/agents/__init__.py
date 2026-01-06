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
from .types import (
    AgentType,
    AgentCategory,
    AGENT_CATEGORY_MAP,
    Priority,
    AgentStatus,
    InvalidStatusTransitionError,
    AgentResult,
    SuccessResult,
    ErrorResult,
    PartialResult,
    ErrorCode,
)

# Base
from .base import (
    BaseAgent,
    AgentConfig,
    AgentCapabilities,
    ResourceLimits,
    AgentStateManager,
    ExecutionContext,
    ContextBuilder,
    AgentHooks,
    HookType,
    hook,
    pre_execute,
    post_execute,
    on_error,
    on_memory_store,
)

# Registry
from .registry import (
    AgentRegistry,
    get_registry,
    AgentFactory,
    create_agent,
    AgentCatalog,
    AgentMetadata,
)

# Lifecycle
from .lifecycle import (
    AgentPool,
    PoolConfig,
    LifecycleManager,
    LifecycleEvent,
    AgentSupervisor,
    SupervisorConfig,
)

# Core Agents
from .core import (
    CoderAgent,
    ReviewerAgent,
    FixerAgent,
    OrchestratorAgent,
)

# Enterprise Agents
from .enterprise import (
    ArchitectAgent,
    SystemDesignerAgent,
    MigrationAgent,
    SecurityScannerAgent,
    VulnerabilityAnalyzerAgent,
    ComplianceCheckerAgent,
    TestGeneratorAgent,
    PerformanceAnalyzerAgent,
    CoverageAgent,
    DocumentationAgent,
    APIDocumenterAgent,
    ChangelogGeneratorAgent,
    APIDesignerAgent,
    SchemaValidatorAgent,
    TaskCoordinatorAgent,
    WorkflowManagerAgent,
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
