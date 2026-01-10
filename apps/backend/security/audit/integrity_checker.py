"""Audit log integrity verification.

World-Class Standards:
- Cryptographic chain validation
- Tamper detection
- Gap detection
- Verification reporting
"""

import hashlib
import json
from dataclasses import dataclass

from ..models import AuditEvent


@dataclass
class IntegrityReport:
    """Report from integrity verification."""

    valid: bool
    total_events: int
    verified_events: int
    first_invalid_id: str | None = None
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class IntegrityChecker:
    """Verifies integrity of audit log chain.

    Ensures:
    - Event checksums are valid
    - Chain links are unbroken
    - No events have been tampered with
    - No events are missing from chain
    """

    def compute_checksum(
        self,
        event: AuditEvent,
        previous_checksum: str | None = None,
    ) -> str:
        """Compute expected checksum for an event.

        Args:
            event: Audit event to compute checksum for
            previous_checksum: Checksum of previous event in chain

        Returns:
            SHA-256 checksum hex string
        """
        data = {
            "action": event.action.value,
            "actor": event.actor,
            "resource": event.resource,
            "timestamp": event.timestamp,
            "details": event.details or {},
            "previous_checksum": previous_checksum or "",
        }

        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_event(
        self,
        event: AuditEvent,
        previous_checksum: str | None = None,
    ) -> bool:
        """Verify a single event's integrity.

        Args:
            event: Event to verify
            previous_checksum: Expected previous checksum

        Returns:
            True if event is valid
        """
        expected = self.compute_checksum(event, previous_checksum)
        return event.checksum == expected

    def verify_chain(self, events: list[AuditEvent]) -> bool:
        """Verify integrity of event chain.

        Args:
            events: Ordered list of events to verify

        Returns:
            True if entire chain is valid
        """
        if not events:
            return True

        previous_checksum = None

        for event in events:
            if not self.verify_event(event, previous_checksum):
                return False
            previous_checksum = event.checksum

        return True

    def verify_chain_detailed(
        self,
        events: list[AuditEvent],
    ) -> IntegrityReport:
        """Verify chain with detailed report.

        Args:
            events: Ordered list of events to verify

        Returns:
            Detailed integrity report
        """
        if not events:
            return IntegrityReport(
                valid=True,
                total_events=0,
                verified_events=0,
            )

        errors = []
        previous_checksum = None
        verified_count = 0
        first_invalid_id = None

        for i, event in enumerate(events):
            expected = self.compute_checksum(event, previous_checksum)

            if event.checksum != expected:
                if first_invalid_id is None:
                    first_invalid_id = event.id
                errors.append(
                    f"Event {event.id} at position {i}: checksum mismatch. "
                    f"Expected {expected[:16]}..., got {event.checksum[:16]}..."
                )
            else:
                verified_count += 1

            previous_checksum = event.checksum

        return IntegrityReport(
            valid=len(errors) == 0,
            total_events=len(events),
            verified_events=verified_count,
            first_invalid_id=first_invalid_id,
            errors=errors,
        )

    def detect_gaps(
        self,
        events: list[AuditEvent],
    ) -> list[tuple[str, str]]:
        """Detect potential gaps in event sequence.

        Uses timestamp analysis to find suspicious gaps.

        Args:
            events: Ordered list of events

        Returns:
            List of (before_id, after_id) tuples indicating gaps
        """
        if len(events) < 2:
            return []

        gaps = []

        # Parse timestamps and look for large gaps
        from datetime import datetime

        for i in range(len(events) - 1):
            current = events[i]
            next_event = events[i + 1]

            try:
                current_time = datetime.fromisoformat(
                    current.timestamp.replace("Z", "+00:00")
                )
                next_time = datetime.fromisoformat(
                    next_event.timestamp.replace("Z", "+00:00")
                )

                # Gap of more than 1 hour is suspicious
                gap_seconds = (next_time - current_time).total_seconds()
                if gap_seconds > 3600:
                    gaps.append((current.id, next_event.id))
            except (ValueError, TypeError):
                continue

        return gaps

    def repair_chain(
        self,
        events: list[AuditEvent],
    ) -> list[AuditEvent]:
        """Attempt to repair a broken chain by recomputing checksums.

        WARNING: This should only be used for recovery, as it
        destroys the original integrity verification.

        Args:
            events: Events with potentially broken chain

        Returns:
            Events with repaired checksums
        """
        if not events:
            return []

        repaired = []
        previous_checksum = None

        for event in events:
            new_checksum = self.compute_checksum(event, previous_checksum)

            # Create new event with updated checksum
            repaired_event = AuditEvent(
                id=event.id,
                timestamp=event.timestamp,
                action=event.action,
                actor=event.actor,
                resource=event.resource,
                details=event.details,
                severity=event.severity,
                success=event.success,
                ip_address=event.ip_address,
                session_id=event.session_id,
                checksum=new_checksum,
            )

            repaired.append(repaired_event)
            previous_checksum = new_checksum

        return repaired
