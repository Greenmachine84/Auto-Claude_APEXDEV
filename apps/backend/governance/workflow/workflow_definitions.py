"""
Workflow Definitions - Phase 9 Implementation.

Predefined workflow templates for common approval scenarios.

World-Class Standards:
- Configurable workflows
- Multi-step support
- Provider-aware templates
"""

import logging
from enum import Enum

from ..models import WorkflowDefinition

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Types of approval workflows."""

    SINGLE_APPROVER = "single_approver"
    MULTI_APPROVER = "multi_approver"
    CHAIN_APPROVAL = "chain_approval"
    CONSENSUS = "consensus"


# =============================================================================
# PREDEFINED WORKFLOWS
# =============================================================================

SINGLE_APPROVER_WORKFLOW = WorkflowDefinition(
    id="single_approver",
    name="Single Approver",
    description="Requires approval from one authorized approver",
    steps=[{"order": 1, "role": "approver", "required": True}],
    require_all=False,  # Any one approver is sufficient
    timeout_hours=24,
    escalation_path=["manager", "admin"],
    enabled=True,
)


MULTI_APPROVER_WORKFLOW = WorkflowDefinition(
    id="multi_approver",
    name="Multi Approver",
    description="Requires approval from multiple approvers",
    steps=[
        {"order": 1, "role": "tech_lead", "required": True},
        {"order": 1, "role": "security", "required": True},
    ],
    require_all=True,  # All approvers required
    timeout_hours=48,
    escalation_path=["director"],
    enabled=True,
)


CHAIN_APPROVAL_WORKFLOW = WorkflowDefinition(
    id="chain_approval",
    name="Chain Approval",
    description="Sequential approval from multiple levels",
    steps=[
        {"order": 1, "role": "team_lead", "required": True},
        {"order": 2, "role": "manager", "required": True},
        {"order": 3, "role": "director", "required": False},  # Optional
    ],
    require_all=True,
    timeout_hours=72,
    escalation_path=["admin"],
    enabled=True,
)


CONSENSUS_WORKFLOW = WorkflowDefinition(
    id="consensus",
    name="Consensus",
    description="Requires majority approval from committee",
    steps=[
        {"order": 1, "role": "committee_member", "required": False},
    ],
    require_all=False,  # Majority is sufficient
    timeout_hours=168,  # 1 week
    escalation_path=["admin"],
    enabled=True,
)


# Provider-specific workflows
AZURE_APPROVAL_WORKFLOW = WorkflowDefinition(
    id="azure_provider_access",
    name="Azure Provider Access",
    description="Approval required for Azure OpenAI access",
    steps=[
        {"order": 1, "role": "tech_lead", "required": True},
        {"order": 2, "role": "cost_approver", "required": True},
    ],
    require_all=True,
    timeout_hours=24,
    escalation_path=["manager", "admin"],
    enabled=True,
)


HIGH_COST_APPROVAL_WORKFLOW = WorkflowDefinition(
    id="high_cost_approval",
    name="High Cost Approval",
    description="Approval for requests exceeding cost threshold",
    steps=[
        {"order": 1, "role": "manager", "required": True},
        {"order": 2, "role": "finance", "required": True},
    ],
    require_all=True,
    timeout_hours=48,
    escalation_path=["director", "cfo"],
    enabled=True,
)


# =============================================================================
# WORKFLOW REGISTRY
# =============================================================================

DEFAULT_WORKFLOWS: dict[str, WorkflowDefinition] = {
    "single_approver": SINGLE_APPROVER_WORKFLOW,
    "multi_approver": MULTI_APPROVER_WORKFLOW,
    "chain_approval": CHAIN_APPROVAL_WORKFLOW,
    "consensus": CONSENSUS_WORKFLOW,
    "azure_provider_access": AZURE_APPROVAL_WORKFLOW,
    "high_cost_approval": HIGH_COST_APPROVAL_WORKFLOW,
}


class WorkflowRegistry:
    """
    Registry of available workflow definitions.
    """

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default workflow definitions."""
        for workflow_id, workflow in DEFAULT_WORKFLOWS.items():
            self._workflows[workflow_id] = workflow
        logger.info(f"Loaded {len(self._workflows)} default workflows")

    def register(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self._workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.id}")

    def unregister(self, workflow_id: str) -> bool:
        """Unregister a workflow definition."""
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False

    def get(self, workflow_id: str) -> WorkflowDefinition | None:
        """Get a workflow by ID."""
        return self._workflows.get(workflow_id)

    def list_all(self) -> list[WorkflowDefinition]:
        """List all registered workflows."""
        return list(self._workflows.values())

    def list_enabled(self) -> list[WorkflowDefinition]:
        """List only enabled workflows."""
        return [w for w in self._workflows.values() if w.enabled]

    def get_for_provider(self, provider: str) -> WorkflowDefinition | None:
        """Get workflow specific to a provider."""
        # Check for provider-specific workflow
        workflow_id = f"{provider}_provider_access"
        if workflow_id in self._workflows:
            return self._workflows[workflow_id]

        # Default to single approver
        return self._workflows.get("single_approver")
