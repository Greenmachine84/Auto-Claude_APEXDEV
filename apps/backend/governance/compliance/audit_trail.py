"""
Audit Trail - Phase 9 Implementation.

Complete audit trail for governance actions.

World-Class Standards:
- Immutable records
- Chain verification
- Tamper detection
"""

import hashlib
import json
import logging
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Immutable audit entry with chain link."""

    id: str
    sequence: int
    timestamp: datetime
    actor: str
    action: str
    resource: str
    provider: str
    old_value: str | None
    new_value: str | None
    metadata: dict[str, Any]
    previous_hash: str
    entry_hash: str = ""

    def __post_init__(self) -> None:
        """Calculate entry hash."""
        if not self.entry_hash:
            self.entry_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash including previous hash."""
        data = (
            f"{self.id}:{self.sequence}:{self.timestamp.isoformat()}:"
            f"{self.actor}:{self.action}:{self.resource}:{self.provider}:"
            f"{self.old_value}:{self.new_value}:{self.previous_hash}"
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def verify(self) -> bool:
        """Verify entry hash."""
        return self.entry_hash == self._calculate_hash()


class AuditTrail:
    """
    Immutable audit trail with chain verification.

    Provides:
    - Tamper-evident logging
    - Chain integrity verification
    - Complete action history
    """

    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        self._lock = threading.Lock()
        self._sequence = 0

    def _generate_id(self) -> str:
        """Generate unique entry ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"AUD-{timestamp}"

    def _get_previous_hash(self) -> str:
        """Get hash of previous entry."""
        if not self._entries:
            return self.GENESIS_HASH
        return self._entries[-1].entry_hash

    def record(
        self,
        actor: str,
        action: str,
        resource: str,
        provider: str,
        old_value: Any | None = None,
        new_value: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """
        Record an audit entry.

        Args:
            actor: Who performed the action
            action: What action was performed
            resource: What resource was affected
            provider: Provider context
            old_value: Previous value (if applicable)
            new_value: New value (if applicable)
            metadata: Additional context

        Returns:
            Created audit entry
        """
        with self._lock:
            self._sequence += 1

            entry = AuditEntry(
                id=self._generate_id(),
                sequence=self._sequence,
                timestamp=datetime.utcnow(),
                actor=actor,
                action=action,
                resource=resource,
                provider=provider,
                old_value=json.dumps(old_value) if old_value else None,
                new_value=json.dumps(new_value) if new_value else None,
                metadata=metadata or {},
                previous_hash=self._get_previous_hash(),
            )

            self._entries.append(entry)

        logger.debug(f"Audit: {actor} -> {action} on {resource} ({provider})")
        return entry

    def record_policy_change(
        self,
        actor: str,
        provider: str,
        policy_id: str,
        old_policy: dict | None = None,
        new_policy: dict | None = None,
    ) -> AuditEntry:
        """Record policy change."""
        action = "policy_update" if old_policy else "policy_create"
        if new_policy is None and old_policy:
            action = "policy_delete"

        return self.record(
            actor=actor,
            action=action,
            resource=f"policy:{policy_id}",
            provider=provider,
            old_value=old_policy,
            new_value=new_policy,
        )

    def record_config_change(
        self,
        actor: str,
        provider: str,
        config_key: str,
        old_value: Any,
        new_value: Any,
    ) -> AuditEntry:
        """Record configuration change."""
        return self.record(
            actor=actor,
            action="config_update",
            resource=f"config:{config_key}",
            provider=provider,
            old_value=old_value,
            new_value=new_value,
        )

    def record_approval_action(
        self,
        actor: str,
        provider: str,
        request_id: str,
        action: str,
        metadata: dict | None = None,
    ) -> AuditEntry:
        """Record approval action."""
        return self.record(
            actor=actor,
            action=f"approval_{action}",
            resource=f"approval:{request_id}",
            provider=provider,
            metadata=metadata,
        )

    def verify_chain(self) -> tuple[bool, int, int | None]:
        """
        Verify chain integrity.

        Returns:
            Tuple of (is_valid, total_entries, first_invalid_sequence)
        """
        with self._lock:
            entries = self._entries.copy()

        if not entries:
            return True, 0, None

        # Verify first entry links to genesis
        if entries[0].previous_hash != self.GENESIS_HASH:
            return False, len(entries), 1

        # Verify chain
        for i, entry in enumerate(entries):
            # Verify entry hash
            if not entry.verify():
                return False, len(entries), entry.sequence

            # Verify chain link (except first)
            if i > 0:
                if entry.previous_hash != entries[i - 1].entry_hash:
                    return False, len(entries), entry.sequence

        return True, len(entries), None

    def get_entries(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        actor: str | None = None,
        provider: str | None = None,
        action: str | None = None,
        limit: int = 1000,
    ) -> list[AuditEntry]:
        """Query audit entries."""
        with self._lock:
            entries = self._entries.copy()

        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]
        if actor:
            entries = [e for e in entries if e.actor == actor]
        if provider:
            entries = [e for e in entries if e.provider == provider]
        if action:
            entries = [e for e in entries if action in e.action]

        return entries[-limit:]

    def get_by_resource(self, resource: str) -> list[AuditEntry]:
        """Get all entries for a resource."""
        with self._lock:
            return [e for e in self._entries if e.resource == resource]

    def get_statistics(self) -> dict[str, Any]:
        """Get audit trail statistics."""
        with self._lock:
            entries = self._entries.copy()

        if not entries:
            return {
                "total_entries": 0,
                "chain_valid": True,
            }

        is_valid, total, first_invalid = self.verify_chain()

        # Count by action type
        action_counts: dict[str, int] = {}
        for entry in entries:
            action = entry.action.split("_")[0]
            action_counts[action] = action_counts.get(action, 0) + 1

        # Count by provider
        provider_counts: dict[str, int] = {}
        for entry in entries:
            provider_counts[entry.provider] = provider_counts.get(entry.provider, 0) + 1

        return {
            "total_entries": total,
            "chain_valid": is_valid,
            "first_invalid": first_invalid,
            "first_entry": entries[0].timestamp.isoformat() if entries else None,
            "last_entry": entries[-1].timestamp.isoformat() if entries else None,
            "action_counts": action_counts,
            "provider_counts": provider_counts,
        }

    def export(self, path: str) -> int:
        """Export audit trail to file."""
        with self._lock:
            entries = self._entries.copy()

        data = []
        for entry in entries:
            entry_dict = asdict(entry)
            entry_dict["timestamp"] = entry.timestamp.isoformat()
            data.append(entry_dict)

        Path(path).write_text(json.dumps(data, indent=2))
        logger.info(f"Exported {len(data)} audit entries to {path}")
        return len(data)
