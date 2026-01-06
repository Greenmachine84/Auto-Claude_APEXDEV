"""Agent Type Definitions.

Defines the canonical enumeration of all agent types in the system.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification:
- 4 Core Agents: Coder, Reviewer, Fixer, Orchestrator
- 16 Enterprise Agents across 6 categories

Naming follows NAMING_ALIGNMENT_STANDARDS.md conventions.
"""

from enum import Enum, auto
from typing import Final


class AgentCategory(Enum):
    """Categories for organizing agent types."""

    CORE = "core"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    QUALITY = "quality"
    DOCUMENTATION = "documentation"
    API = "api"
    ORCHESTRATION = "orchestration"


class AgentType(Enum):
    """Enumeration of all agent types in the system.

    The agent system consists of:
    - 4 Core Agents: Primary autonomous coding capabilities
    - 16 Enterprise Agents: Specialized domain expertise

    Total: 20 agent types

    Usage:
        >>> agent_type = AgentType.CODER
        >>> agent_type.value
        'coder'
        >>> AgentType.get_category(agent_type)
        AgentCategory.CORE
    """

    # ═══════════════════════════════════════════════════════════════════════
    # CORE AGENTS (4)
    # Primary autonomous coding capabilities
    # ═══════════════════════════════════════════════════════════════════════
    CODER = "coder"
    REVIEWER = "reviewer"
    FIXER = "fixer"
    ORCHESTRATOR = "orchestrator"

    # ═══════════════════════════════════════════════════════════════════════
    # ENTERPRISE AGENTS - ARCHITECTURE (7)
    # System design and optimization specialists
    # ═══════════════════════════════════════════════════════════════════════
    SYSTEM_ARCHITECT = "system_architect"
    REFACTOR_ARCHITECT = "refactor_architect"
    PERFORMANCE_ARCHITECT = "performance_architect"
    INTEGRATION_ARCHITECT = "integration_architect"
    DATA_ARCHITECT = "data_architect"
    CLOUD_ARCHITECT = "cloud_architect"
    DEVOPS_ARCHITECT = "devops_architect"

    # ═══════════════════════════════════════════════════════════════════════
    # ENTERPRISE AGENTS - SECURITY (3)
    # Security analysis and defense specialists
    # ═══════════════════════════════════════════════════════════════════════
    SECURITY_ARCHITECT = "security_architect"
    RED_TEAM = "red_team"
    BLUE_TEAM = "blue_team"

    # ═══════════════════════════════════════════════════════════════════════
    # ENTERPRISE AGENTS - QUALITY (2)
    # Testing and compliance specialists
    # ═══════════════════════════════════════════════════════════════════════
    QA_VERIFICATION = "qa_verification"
    COMPLIANCE_AUDITOR = "compliance_auditor"

    # ═══════════════════════════════════════════════════════════════════════
    # ENTERPRISE AGENTS - DOCUMENTATION (1)
    # Documentation generation specialist
    # ═══════════════════════════════════════════════════════════════════════
    DOCUMENTATION_LEAD = "documentation_lead"

    # ═══════════════════════════════════════════════════════════════════════
    # ENTERPRISE AGENTS - API (1)
    # API design specialist
    # ═══════════════════════════════════════════════════════════════════════
    API_DESIGN = "api_design"

    # ═══════════════════════════════════════════════════════════════════════
    # ENTERPRISE AGENTS - ORCHESTRATION (1)
    # Multi-agent coordination specialist
    # ═══════════════════════════════════════════════════════════════════════
    MDA_ORCHESTRATOR = "mda_orchestrator"

    @classmethod
    def get_category(cls, agent_type: "AgentType") -> AgentCategory:
        """Get the category for an agent type.

        Args:
            agent_type: The agent type to categorize

        Returns:
            The AgentCategory for the given agent type
        """
        return AGENT_CATEGORY_MAP.get(agent_type, AgentCategory.CORE)

    @classmethod
    def get_core_agents(cls) -> list["AgentType"]:
        """Get all core agent types."""
        return [cls.CODER, cls.REVIEWER, cls.FIXER, cls.ORCHESTRATOR]

    @classmethod
    def get_enterprise_agents(cls) -> list["AgentType"]:
        """Get all enterprise agent types."""
        return [
            agent for agent in cls if agent not in cls.get_core_agents()
        ]

    @classmethod
    def get_agents_by_category(cls, category: AgentCategory) -> list["AgentType"]:
        """Get all agent types in a specific category.

        Args:
            category: The category to filter by

        Returns:
            List of agent types in the category
        """
        return [
            agent for agent, cat in AGENT_CATEGORY_MAP.items() if cat == category
        ]

    def is_core(self) -> bool:
        """Check if this is a core agent type."""
        return self in self.get_core_agents()

    def is_enterprise(self) -> bool:
        """Check if this is an enterprise agent type."""
        return not self.is_core()


# ═══════════════════════════════════════════════════════════════════════════
# AGENT CATEGORY MAPPING
# Maps each agent type to its category for O(1) lookup
# ═══════════════════════════════════════════════════════════════════════════

AGENT_CATEGORY_MAP: Final[dict[AgentType, AgentCategory]] = {
    # Core Agents
    AgentType.CODER: AgentCategory.CORE,
    AgentType.REVIEWER: AgentCategory.CORE,
    AgentType.FIXER: AgentCategory.CORE,
    AgentType.ORCHESTRATOR: AgentCategory.CORE,
    # Architecture Agents
    AgentType.SYSTEM_ARCHITECT: AgentCategory.ARCHITECTURE,
    AgentType.REFACTOR_ARCHITECT: AgentCategory.ARCHITECTURE,
    AgentType.PERFORMANCE_ARCHITECT: AgentCategory.ARCHITECTURE,
    AgentType.INTEGRATION_ARCHITECT: AgentCategory.ARCHITECTURE,
    AgentType.DATA_ARCHITECT: AgentCategory.ARCHITECTURE,
    AgentType.CLOUD_ARCHITECT: AgentCategory.ARCHITECTURE,
    AgentType.DEVOPS_ARCHITECT: AgentCategory.ARCHITECTURE,
    # Security Agents
    AgentType.SECURITY_ARCHITECT: AgentCategory.SECURITY,
    AgentType.RED_TEAM: AgentCategory.SECURITY,
    AgentType.BLUE_TEAM: AgentCategory.SECURITY,
    # Quality Agents
    AgentType.QA_VERIFICATION: AgentCategory.QUALITY,
    AgentType.COMPLIANCE_AUDITOR: AgentCategory.QUALITY,
    # Documentation Agents
    AgentType.DOCUMENTATION_LEAD: AgentCategory.DOCUMENTATION,
    # API Agents
    AgentType.API_DESIGN: AgentCategory.API,
    # Orchestration Agents
    AgentType.MDA_ORCHESTRATOR: AgentCategory.ORCHESTRATION,
}

# Validate all agent types are mapped
assert len(AGENT_CATEGORY_MAP) == len(AgentType), (
    f"Category map incomplete: {len(AGENT_CATEGORY_MAP)} vs {len(AgentType)} agents"
)

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

CORE_AGENT_COUNT: Final[int] = 4
ENTERPRISE_AGENT_COUNT: Final[int] = 16
TOTAL_AGENT_COUNT: Final[int] = CORE_AGENT_COUNT + ENTERPRISE_AGENT_COUNT

# Validate counts
assert len(AgentType.get_core_agents()) == CORE_AGENT_COUNT
assert len(AgentType.get_enterprise_agents()) == ENTERPRISE_AGENT_COUNT
assert len(AgentType) == TOTAL_AGENT_COUNT
