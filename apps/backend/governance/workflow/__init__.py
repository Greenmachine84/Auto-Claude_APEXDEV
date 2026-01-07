"""
Workflow Module - Phase 9 Implementation.

Provides approval workflow management for governance.
"""

from .approval_workflow import ApprovalWorkflow
from .workflow_definitions import (
    WorkflowType,
    WorkflowRegistry,
    DEFAULT_WORKFLOWS,
    SINGLE_APPROVER_WORKFLOW,
    MULTI_APPROVER_WORKFLOW,
    CHAIN_APPROVAL_WORKFLOW,
    CONSENSUS_WORKFLOW,
)
from .approval_request import (
    ApprovalDecision,
    ApprovalHistory,
    ApprovalRequestManager,
)
from .escalation import (
    EscalationTrigger,
    EscalationRule,
    EscalationEvent,
    EscalationManager,
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
