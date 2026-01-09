"""Enterprise-grade audit logging system.

World-Class Standards:
- Immutable audit trails
- Cryptographic checksums for integrity
- Structured event logging
- Multi-backend storage support
"""

import hashlib
import json
import uuid
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime
from typing import Any

from ..models import AuditAction, AuditEvent, Severity
from .audit_storage import AuditStorage, FileAuditStorage
from .event_types import AuditEventType
from .integrity_checker import IntegrityChecker


class AuditLogger:
    """Centralized audit logging with integrity verification.

    Features:
    - Automatic checksum generation
    - Chain validation for tamper detection
    - Async-ready storage backends
    - Event filtering and querying

    Example:
        logger = AuditLogger()
        await logger.initialize()

        await logger.log_event(
            action=AuditAction.LOGIN_SUCCESS,
            actor="user@example.com",
            resource="auth_service",
            details={"ip": "192.168.1.1"},
        )
    """

    def __init__(
        self,
        storage: AuditStorage | None = None,
        integrity_checker: IntegrityChecker | None = None,
    ):
        """Initialize audit logger.

        Args:
            storage: Audit event storage backend
            integrity_checker: Integrity verification component
        """
        self._storage = storage or FileAuditStorage()
        self._integrity = integrity_checker or IntegrityChecker()
        self._last_checksum: str | None = None
        self._event_handlers: list[Callable[[AuditEvent], None]] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize logger and storage backend."""
        if self._initialized:
            return

        await self._storage.initialize()

        # Get last event checksum for chain validation
        last_event = await self._storage.get_last_event()
        if last_event:
            self._last_checksum = last_event.checksum

        self._initialized = True

    def _compute_checksum(
        self,
        action: AuditAction,
        actor: str,
        resource: str,
        timestamp: str,
        details: dict[str, Any] | None = None,
    ) -> str:
        """Compute SHA-256 checksum for event integrity.

        Includes previous checksum for chain validation.
        """
        data = {
            "action": action.value,
            "actor": actor,
            "resource": resource,
            "timestamp": timestamp,
            "details": details or {},
            "previous_checksum": self._last_checksum or "",
        }

        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    async def log_event(
        self,
        action: AuditAction,
        actor: str,
        resource: str,
        details: dict[str, Any] | None = None,
        severity: Severity = Severity.LOW,
        success: bool = True,
        ip_address: str | None = None,
        session_id: str | None = None,
    ) -> AuditEvent:
        """Log an audit event.

        Args:
            action: Type of action performed
            actor: Who performed the action
            resource: What was acted upon
            details: Additional event details
            severity: Event severity level
            success: Whether action succeeded
            ip_address: Client IP address
            session_id: Session identifier

        Returns:
            Created audit event
        """
        if not self._initialized:
            await self.initialize()

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Compute checksum including chain link
        checksum = self._compute_checksum(action, actor, resource, timestamp, details)

        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            action=action,
            actor=actor,
            resource=resource,
            details=details or {},
            severity=severity,
            success=success,
            ip_address=ip_address,
            session_id=session_id,
            checksum=checksum,
        )

        # Store event
        await self._storage.store_event(event)

        # Update chain
        self._last_checksum = checksum

        # Notify handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass  # Don't let handler errors break audit logging

        return event

    async def log_security_event(
        self,
        event_type: AuditEventType,
        actor: str,
        resource: str,
        details: dict[str, Any] | None = None,
        success: bool = True,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log a security-specific event.

        Convenience method that maps event types to actions.

        Args:
            event_type: Security event type
            actor: Who performed the action
            resource: What was acted upon
            details: Additional details
            success: Whether action succeeded
            ip_address: Client IP address

        Returns:
            Created audit event
        """
        action = event_type.to_audit_action()
        severity = event_type.default_severity()

        return await self.log_event(
            action=action,
            actor=actor,
            resource=resource,
            details=details,
            severity=severity,
            success=success,
            ip_address=ip_address,
        )

    async def log_credential_access(
        self,
        provider: str,
        actor: str,
        operation: str,
        success: bool = True,
        ip_address: str | None = None,
    ) -> AuditEvent:
        """Log credential vault access.

        Args:
            provider: LLM provider name
            actor: Who accessed credentials
            operation: What operation was performed
            success: Whether operation succeeded
            ip_address: Client IP

        Returns:
            Created audit event
        """
        action_map = {
            "read": AuditAction.CREDENTIAL_RETRIEVED,
            "write": AuditAction.CREDENTIAL_UPDATED,
            "delete": AuditAction.CREDENTIAL_DELETED,
            "rotate": AuditAction.KEY_ROTATED,
        }

        action = action_map.get(operation, AuditAction.CREDENTIAL_RETRIEVED)

        return await self.log_event(
            action=action,
            actor=actor,
            resource=f"credential:{provider}",
            details={"provider": provider, "operation": operation},
            severity=Severity.HIGH if not success else Severity.MEDIUM,
            success=success,
            ip_address=ip_address,
        )

    async def query_events(
        self,
        action: AuditAction | None = None,
        actor: str | None = None,
        resource: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events with filters.

        Args:
            action: Filter by action type
            actor: Filter by actor
            resource: Filter by resource
            start_time: Start of time range (ISO format)
            end_time: End of time range (ISO format)
            limit: Maximum events to return

        Returns:
            List of matching events
        """
        if not self._initialized:
            await self.initialize()

        return await self._storage.query_events(
            action=action,
            actor=actor,
            resource=resource,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    async def verify_integrity(
        self,
        start_id: str | None = None,
        end_id: str | None = None,
    ) -> bool:
        """Verify integrity of audit log chain.

        Checks that event checksums form valid chain.

        Args:
            start_id: Start from this event ID
            end_id: End at this event ID

        Returns:
            True if integrity verified
        """
        if not self._initialized:
            await self.initialize()

        events = await self._storage.get_event_range(start_id, end_id)

        return self._integrity.verify_chain(events)

    def add_event_handler(self, handler: Callable[[AuditEvent], None]) -> None:
        """Add a handler to be called for each event.

        Args:
            handler: Function to call with event
        """
        self._event_handlers.append(handler)

    def remove_event_handler(self, handler: Callable[[AuditEvent], None]) -> None:
        """Remove an event handler."""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    async def get_event_count(
        self,
        action: AuditAction | None = None,
        since: str | None = None,
    ) -> int:
        """Get count of events matching criteria.

        Args:
            action: Filter by action type
            since: Count events since this time

        Returns:
            Event count
        """
        if not self._initialized:
            await self.initialize()

        return await self._storage.count_events(action=action, since=since)

    async def export_events(
        self,
        format: str = "json",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> str:
        """Export audit events.

        Args:
            format: Export format (json, csv)
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Exported data as string
        """
        events = await self.query_events(
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        if format == "json":
            return json.dumps(
                [asdict(e) for e in events],
                indent=2,
                default=str,
            )
        elif format == "csv":
            lines = ["id,timestamp,action,actor,resource,success,severity"]
            for e in events:
                lines.append(
                    f"{e.id},{e.timestamp},{e.action.value},"
                    f"{e.actor},{e.resource},{e.success},{e.severity.value}"
                )
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global default logger
default_audit_logger = AuditLogger()
