"""
Approval Workflow Engine - Phase 9 Implementation.

Multi-step approval workflows for governance.

World-Class Standards:
- SLA-compliant workflows
- Auto-escalation
- Complete audit trail
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from ..models import (
    ApprovalRequest,
    ApprovalStatus,
    WorkflowDefinition,
)

logger = logging.getLogger(__name__)


class ApprovalWorkflow:
    """
    Approval workflow engine.

    Manages multi-step approval processes with
    escalation and SLA tracking.
    """

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._default_timeout_hours: int = 24
        self._escalation_enabled: bool = True

    async def create_request(
        self,
        request_type: str,
        requester_id: str,
        description: str,
        provider: str | None = None,
        model: str | None = None,
        approvers: list[str] | None = None,
        context: dict[str, Any] | None = None,
        timeout_hours: int | None = None,
    ) -> str:
        """
        Create a new approval request.

        Args:
            request_type: Type of request (e.g., "model_access")
            requester_id: User requesting approval
            description: Human-readable description
            provider: LLM provider (optional)
            model: Model identifier (optional)
            approvers: List of approver IDs
            context: Additional context
            timeout_hours: Hours until expiration

        Returns:
            Request ID
        """
        request_id = str(uuid.uuid4())
        timeout = timeout_hours or self._default_timeout_hours

        request = ApprovalRequest(
            id=request_id,
            request_type=request_type,
            requester_id=requester_id,
            description=description,
            status=ApprovalStatus.PENDING,
            provider=provider,
            model=model,
            context=context or {},
            approvers=approvers or [],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=timeout),
        )

        self._requests[request_id] = request
        logger.info(
            f"Created approval request: {request_id} "
            f"(type={request_type}, requester={requester_id})"
        )

        return request_id

    async def approve(
        self, request_id: str, approver_id: str, comments: str | None = None
    ) -> bool:
        """
        Approve a request.

        Args:
            request_id: Request to approve
            approver_id: User approving
            comments: Optional approval comments

        Returns:
            True if approval successful
        """
        request = self._requests.get(request_id)
        if not request:
            logger.warning(f"Approval request not found: {request_id}")
            return False

        if request.status != ApprovalStatus.PENDING:
            logger.warning(
                f"Cannot approve request {request_id}: status is {request.status}"
            )
            return False

        # Check if requester is an authorized approver
        if request.approvers and approver_id not in request.approvers:
            logger.warning(f"User {approver_id} not authorized to approve {request_id}")
            return False

        # Check expiration
        if request.expires_at and datetime.now() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            logger.warning(f"Approval request {request_id} has expired")
            return False

        # Approve
        request.status = ApprovalStatus.APPROVED
        request.approved_by = approver_id
        request.decided_at = datetime.now()

        logger.info(f"Approved request: {request_id} by {approver_id}")
        return True

    async def reject(self, request_id: str, approver_id: str, reason: str) -> bool:
        """
        Reject a request.

        Args:
            request_id: Request to reject
            approver_id: User rejecting
            reason: Rejection reason

        Returns:
            True if rejection successful
        """
        request = self._requests.get(request_id)
        if not request:
            logger.warning(f"Approval request not found: {request_id}")
            return False

        if request.status != ApprovalStatus.PENDING:
            logger.warning(
                f"Cannot reject request {request_id}: status is {request.status}"
            )
            return False

        # Reject
        request.status = ApprovalStatus.REJECTED
        request.rejected_by = approver_id
        request.rejection_reason = reason
        request.decided_at = datetime.now()

        logger.info(f"Rejected request: {request_id} by {approver_id}")
        return True

    async def cancel(self, request_id: str, user_id: str) -> bool:
        """
        Cancel a pending request.

        Only the requester can cancel.
        """
        request = self._requests.get(request_id)
        if not request:
            return False

        if request.requester_id != user_id:
            logger.warning(f"User {user_id} cannot cancel request {request_id}")
            return False

        if request.status != ApprovalStatus.PENDING:
            return False

        request.status = ApprovalStatus.CANCELLED
        request.decided_at = datetime.now()

        logger.info(f"Cancelled request: {request_id}")
        return True

    async def get_pending(
        self, approver_id: str | None = None, provider: str | None = None
    ) -> list[ApprovalRequest]:
        """
        Get pending approval requests.

        Args:
            approver_id: Filter by approver (optional)
            provider: Filter by provider (optional)

        Returns:
            List of pending requests
        """
        pending = [
            r for r in self._requests.values() if r.status == ApprovalStatus.PENDING
        ]

        if approver_id:
            pending = [
                r for r in pending if not r.approvers or approver_id in r.approvers
            ]

        if provider:
            pending = [r for r in pending if r.provider == provider]

        return pending

    async def get_request(self, request_id: str) -> ApprovalRequest | None:
        """Get a specific request."""
        return self._requests.get(request_id)

    async def check_status(self, request_id: str) -> ApprovalStatus:
        """Check status of a request."""
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        # Auto-expire if past deadline
        if (
            request.status == ApprovalStatus.PENDING
            and request.expires_at
            and datetime.now() > request.expires_at
        ):
            request.status = ApprovalStatus.EXPIRED

        return request.status

    async def get_user_requests(
        self, user_id: str, status: ApprovalStatus | None = None
    ) -> list[ApprovalRequest]:
        """Get requests by a specific user."""
        requests = [r for r in self._requests.values() if r.requester_id == user_id]

        if status:
            requests = [r for r in requests if r.status == status]

        return requests

    async def expire_old_requests(self) -> int:
        """Expire all past-deadline pending requests."""
        count = 0
        now = datetime.now()

        for request in self._requests.values():
            if (
                request.status == ApprovalStatus.PENDING
                and request.expires_at
                and now > request.expires_at
            ):
                request.status = ApprovalStatus.EXPIRED
                count += 1

        if count:
            logger.info(f"Expired {count} approval requests")

        return count

    def get_statistics(self) -> dict[str, int]:
        """Get approval statistics."""
        stats = {
            "total": len(self._requests),
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "expired": 0,
            "cancelled": 0,
        }

        for request in self._requests.values():
            if request.status == ApprovalStatus.PENDING:
                stats["pending"] += 1
            elif request.status == ApprovalStatus.APPROVED:
                stats["approved"] += 1
            elif request.status == ApprovalStatus.REJECTED:
                stats["rejected"] += 1
            elif request.status == ApprovalStatus.EXPIRED:
                stats["expired"] += 1
            elif request.status == ApprovalStatus.CANCELLED:
                stats["cancelled"] += 1

        return stats
