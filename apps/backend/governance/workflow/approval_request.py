"""
Approval Request Management - Phase 9 Implementation.

Handles approval request lifecycle and operations.

World-Class Standards:
- Full request lifecycle
- Status tracking
- History preservation
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..models import (
    SUPPORTED_PROVIDERS,
    ApprovalRequest,
    ApprovalStatus,
    ApprovalStep,
    WorkflowDefinition,
)

logger = logging.getLogger(__name__)


class ApprovalDecision(Enum):
    """Approval decisions."""

    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ABSTAINED = "abstained"


@dataclass
class ApprovalHistory:
    """Record of approval actions."""

    request_id: str
    step_id: str
    approver: str
    decision: ApprovalDecision
    timestamp: datetime
    comment: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ApprovalRequestManager:
    """
    Manages approval request lifecycle.
    """

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._history: dict[str, list[ApprovalHistory]] = {}

    def create_request(
        self,
        provider: str,
        action: str,
        requestor: str,
        workflow: WorkflowDefinition,
        context: dict[str, Any] | None = None,
    ) -> ApprovalRequest:
        """Create a new approval request."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        request_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=workflow.timeout_hours)

        # Initialize steps from workflow
        steps = []
        for step_def in workflow.steps:
            step = ApprovalStep(
                id=str(uuid.uuid4()),
                order=step_def["order"],
                approver_role=step_def["role"],
                required=step_def["required"],
                status=ApprovalStatus.PENDING,
            )
            steps.append(step)

        request = ApprovalRequest(
            id=request_id,
            provider=provider,
            action=action,
            requestor=requestor,
            status=ApprovalStatus.PENDING,
            workflow_id=workflow.id,
            steps=steps,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            context=context or {},
        )

        self._requests[request_id] = request
        self._history[request_id] = []

        logger.info(f"Created approval request: {request_id} for provider: {provider}")
        return request

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        """Get a request by ID."""
        return self._requests.get(request_id)

    def update_step(
        self,
        request_id: str,
        step_id: str,
        approver: str,
        decision: ApprovalDecision,
        comment: str | None = None,
    ) -> bool:
        """Update approval step with decision."""
        request = self._requests.get(request_id)
        if not request:
            logger.warning(f"Request not found: {request_id}")
            return False

        # Find and update step
        for step in request.steps:
            if step.id == step_id:
                step.approver = approver
                step.approved_at = datetime.utcnow()
                step.comment = comment

                if decision == ApprovalDecision.APPROVED:
                    step.status = ApprovalStatus.APPROVED
                elif decision == ApprovalDecision.REJECTED:
                    step.status = ApprovalStatus.REJECTED

                # Record history
                history = ApprovalHistory(
                    request_id=request_id,
                    step_id=step_id,
                    approver=approver,
                    decision=decision,
                    timestamp=datetime.utcnow(),
                    comment=comment,
                )
                self._history[request_id].append(history)

                # Update request status
                self._update_request_status(request)
                return True

        return False

    def _update_request_status(self, request: ApprovalRequest) -> None:
        """Update overall request status based on steps."""
        required_steps = [s for s in request.steps if s.required]

        # Check for any rejections
        rejected = any(s.status == ApprovalStatus.REJECTED for s in request.steps)
        if rejected:
            request.status = ApprovalStatus.REJECTED
            return

        # Check if all required steps approved
        all_required_approved = all(
            s.status == ApprovalStatus.APPROVED for s in required_steps
        )
        if all_required_approved:
            request.status = ApprovalStatus.APPROVED
            return

        # Check expiration
        if datetime.utcnow() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED

    def list_pending(
        self,
        provider: str | None = None,
        requestor: str | None = None,
    ) -> list[ApprovalRequest]:
        """List pending approval requests with optional filters."""
        pending = [
            r for r in self._requests.values() if r.status == ApprovalStatus.PENDING
        ]

        if provider:
            pending = [r for r in pending if r.provider == provider]

        if requestor:
            pending = [r for r in pending if r.requestor == requestor]

        return pending

    def list_by_approver(self, approver_role: str) -> list[ApprovalRequest]:
        """List requests needing approval from specific role."""
        result = []
        for request in self._requests.values():
            if request.status != ApprovalStatus.PENDING:
                continue

            for step in request.steps:
                if (
                    step.approver_role == approver_role
                    and step.status == ApprovalStatus.PENDING
                ):
                    result.append(request)
                    break

        return result

    def get_history(self, request_id: str) -> list[ApprovalHistory]:
        """Get approval history for a request."""
        return self._history.get(request_id, [])

    def cancel_request(self, request_id: str, reason: str) -> bool:
        """Cancel an approval request."""
        request = self._requests.get(request_id)
        if not request:
            return False

        if request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.CANCELLED

        # Record cancellation in history
        history = ApprovalHistory(
            request_id=request_id,
            step_id="cancelled",
            approver="system",
            decision=ApprovalDecision.REJECTED,
            timestamp=datetime.utcnow(),
            comment=reason,
        )
        self._history[request_id].append(history)

        logger.info(f"Cancelled request: {request_id}")
        return True

    def cleanup_expired(self) -> int:
        """Clean up expired requests."""
        count = 0
        for request in self._requests.values():
            if request.status == ApprovalStatus.PENDING:
                if datetime.utcnow() > request.expires_at:
                    request.status = ApprovalStatus.EXPIRED
                    count += 1

        if count > 0:
            logger.info(f"Expired {count} requests")
        return count
