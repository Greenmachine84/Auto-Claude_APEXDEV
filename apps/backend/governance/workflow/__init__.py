"""
Workflow Module - Phase 9 Implementation.

Provides approval workflow management for governance.
"""

from .approval_request import (
    ApprovalDecision,
    ApprovalHistory,
    ApprovalRequestManager,
)
from .approval_workflow import ApprovalWorkflow
from .escalation import (
    EscalationEvent,
    EscalationManager,
    EscalationRule,
    EscalationTrigger,
)
from .workflow_definitions import (
    CHAIN_APPROVAL_WORKFLOW,
    CONSENSUS_WORKFLOW,
    DEFAULT_WORKFLOWS,
    MULTI_APPROVER_WORKFLOW,
    SINGLE_APPROVER_WORKFLOW,
    WorkflowRegistry,
    WorkflowType,
)

__all__ = [
    # Approval Workflow
    "ApprovalWorkflow",
    # Workflow Definitions
    "WorkflowType",
    "WorkflowRegistry",
    "DEFAULT_WORKFLOWS",
    "SINGLE_APPROVER_WORKFLOW",
    "MULTI_APPROVER_WORKFLOW",
    "CHAIN_APPROVAL_WORKFLOW",
    "CONSENSUS_WORKFLOW",
    # Approval Request
    "ApprovalDecision",
    "ApprovalHistory",
    "ApprovalRequestManager",
    # Escalation
    "EscalationTrigger",
    "EscalationRule",
    "EscalationEvent",
    "EscalationManager",
]
