"""Enterprise Agents Module.

Implements the 16 enterprise agents defined in PHASE1_AGENT_SYSTEM_ARCHITECTURE.md.
Organized by category for maintainability.

Categories:
- Architecture: Architect, SystemDesigner, MigrationAgent
- Security: SecurityScanner, VulnerabilityAnalyzer, ComplianceChecker
- Quality: TestGenerator, PerformanceAnalyzer, CoverageAgent
- Documentation: DocumentationAgent, APIDocumenter, ChangelogGenerator
- API: APIDesigner, SchemaValidator
- Orchestration: TaskCoordinator, WorkflowManager

Phase 7 Additions:
- Core: AgentLLMConfig, EnterpriseAgentConfig, LLM-agnostic base class
- Subdirectories: code_review, security, qa, documentation, project_analysis, 
                  orchestration, capabilities
"""

# Architecture Agents
from .architect_agent import ArchitectAgent
from .system_designer_agent import SystemDesignerAgent
from .migration_agent import MigrationAgent

# Security Agents
from .security_scanner_agent import SecurityScannerAgent
from .vulnerability_analyzer_agent import VulnerabilityAnalyzerAgent
from .compliance_checker_agent import ComplianceCheckerAgent

# Quality Agents
from .test_generator_agent import TestGeneratorAgent
from .performance_analyzer_agent import PerformanceAnalyzerAgent
from .coverage_agent import CoverageAgent

# Documentation Agents
from .documentation_agent import DocumentationAgent
from .api_documenter_agent import APIDocumenterAgent
from .changelog_generator_agent import ChangelogGeneratorAgent

# API Agents
from .api_designer_agent import APIDesignerAgent
from .schema_validator_agent import SchemaValidatorAgent

# Orchestration Agents
from .task_coordinator_agent import TaskCoordinatorAgent
from .workflow_manager_agent import WorkflowManagerAgent

# Phase 7: Core LLM-Agnostic Infrastructure
from .config import AgentLLMConfig, EnterpriseAgentConfig, LLMProvider
from .types import EnterpriseAgentType, Severity
from .config import AgentCapability
from .base_enterprise_agent import BaseEnterpriseAgent

# Phase 7: Code Review Module
from .code_review import (
    CodeReviewAgent,
    ReviewResult,
    ReviewFinding,
    ReviewPrompts,
    SeverityClassifier,
)

# Phase 7: Security Module
from .security import (
    SecurityAgent,
    ScanResult,
    VulnerabilityFinding,
    SecretFinding,
    VulnerabilityDB,
    OWASPChecker,
)

# Phase 7: QA Module
from .qa import (
    QAAgent,
    TestGenerator,
    GeneratedTest,
    CoverageAnalyzer,
    CoverageReport,
    TestTemplates,
    TestTemplate,
)

# Phase 7: Documentation Module
from .documentation import (
    DocumentationAgent as DocumentationAgentV2,
    DocstringGenerator,
    GeneratedDocstring,
    ReadmeGenerator,
    ReadmeSection,
    APIDocGenerator,
    APIEndpoint,
)

# Phase 7: Project Analysis Module
from .project_analysis import (
    ProjectAnalyzerAgent,
    DependencyMapper,
    DependencyGraph,
    ArchitectureExtractor,
    ArchitectureMap,
    TechDebtAnalyzer,
    TechDebtReport,
)

# Phase 7: Orchestration Module
from .orchestration import (
    OrchestratorAgent,
    AgentCoordinator,
    CoordinationResult,
    ResultAggregator,
    AggregatedResult,
    PipelineManager,
    Pipeline,
    PipelineStage,
)

# Phase 7: Capabilities Module
from .capabilities import (
    CodeAnalysisCapability,
    AnalysisResult as CapabilityAnalysisResult,
    TestGenerationCapability,
    TestSuite,
    DocumentationCapability,
    DocOutput,
    CollaborationCapability,
    Message,
)

__all__ = [
    # Architecture (Legacy)
    "ArchitectAgent",
    "SystemDesignerAgent",
    "MigrationAgent",
    # Security (Legacy)
    "SecurityScannerAgent",
    "VulnerabilityAnalyzerAgent",
    "ComplianceCheckerAgent",
    # Quality (Legacy)
    "TestGeneratorAgent",
    "PerformanceAnalyzerAgent",
    "CoverageAgent",
    # Documentation (Legacy)
    "DocumentationAgent",
    "APIDocumenterAgent",
    "ChangelogGeneratorAgent",
    # API (Legacy)
    "APIDesignerAgent",
    "SchemaValidatorAgent",
    # Orchestration (Legacy)
    "TaskCoordinatorAgent",
    "WorkflowManagerAgent",
    # Phase 7: Core
    "AgentLLMConfig",
    "EnterpriseAgentConfig",
    "LLMProvider",
    "EnterpriseAgentType",
    "Severity",
    "AgentCapability",
    "BaseEnterpriseAgent",
    # Phase 7: Code Review
    "CodeReviewAgent",
    "ReviewResult",
    "ReviewFinding",
    "ReviewPrompts",
    "SeverityClassifier",
    # Phase 7: Security
    "SecurityAgent",
    "ScanResult",
    "VulnerabilityFinding",
    "SecretFinding",
    "VulnerabilityDB",
    "OWASPChecker",
    # Phase 7: QA
    "QAAgent",
    "TestResult",
    "TestGenerator",
    "CoverageAnalyzer",
    "TestTemplates",
    # Phase 7: Documentation
    "DocumentationAgentV2",
    "DocResult",
    "DocstringGenerator",
    "ReadmeGenerator",
    "APIDocGenerator",
    # Phase 7: Project Analysis
    "ProjectAnalyzerAgent",
    "AnalysisResult",
    "DependencyMapper",
    "ArchitectureExtractor",
    "TechDebtAnalyzer",
    # Phase 7: Orchestration
    "OrchestratorAgent",
    "OrchestrationResult",
    "AgentCoordinator",
    "ResultAggregator",
    "PipelineManager",
    # Phase 7: Capabilities
    "CodeAnalysisCapability",
    "CapabilityAnalysisResult",
    "TestGenerationCapability",
    "TestSuite",
    "DocumentationCapability",
    "DocOutput",
    "CollaborationCapability",
    "Message",
]

# Enterprise Agent Registry
# Maps EnterpriseAgentType categories to their implementing agents
# Note: These use EnterpriseAgentType (simplified 6-category system)
# while the core registry uses AgentType (full 20-type system)

ENTERPRISE_AGENT_REGISTRY: dict[EnterpriseAgentType, list[type]] = {
    EnterpriseAgentType.PROJECT_ANALYSIS: [
        ArchitectAgent,
        SystemDesignerAgent,
        MigrationAgent,
    ],
    EnterpriseAgentType.SECURITY: [
        SecurityScannerAgent,
        VulnerabilityAnalyzerAgent,
        ComplianceCheckerAgent,
    ],
    EnterpriseAgentType.QA: [
        TestGeneratorAgent,
        PerformanceAnalyzerAgent,
        CoverageAgent,
    ],
    EnterpriseAgentType.DOCUMENTATION: [
        DocumentationAgent,
        APIDocumenterAgent,
        ChangelogGeneratorAgent,
    ],
    EnterpriseAgentType.CODE_REVIEW: [
        APIDesignerAgent,
        SchemaValidatorAgent,
    ],
    EnterpriseAgentType.ORCHESTRATOR: [
        TaskCoordinatorAgent,
        WorkflowManagerAgent,
    ],
}


def get_enterprise_agents_by_type(agent_type: EnterpriseAgentType) -> list[type]:
    """Get all enterprise agent classes for a given type.
    
    Args:
        agent_type: The enterprise agent type category
        
    Returns:
        List of agent classes in that category
    """
    return ENTERPRISE_AGENT_REGISTRY.get(agent_type, [])


def get_all_enterprise_agents() -> list[type]:
    """Get all enterprise agent classes.
    
    Returns:
        List of all enterprise agent classes
    """
    return [
        agent
        for agents in ENTERPRISE_AGENT_REGISTRY.values()
        for agent in agents
    ]
