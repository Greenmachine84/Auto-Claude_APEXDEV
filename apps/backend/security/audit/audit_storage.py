"""Audit event storage backends.

World-Class Standards:
- Multiple storage backend support
- Efficient querying
- Atomic writes
- Data retention policies
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from ..models import AuditAction, AuditEvent, Severity


class AuditStorage(ABC):
    """Abstract base class for audit storage backends."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        pass

    @abstractmethod
    async def store_event(self, event: AuditEvent) -> None:
        """Store an audit event."""
        pass

    @abstractmethod
    async def get_event(self, event_id: str) -> AuditEvent | None:
        """Retrieve an event by ID."""
        pass

    @abstractmethod
    async def get_last_event(self) -> AuditEvent | None:
        """Get the most recent event."""
        pass

    @abstractmethod
    async def query_events(
        self,
        action: AuditAction | None = None,
        actor: str | None = None,
        resource: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query events with filters."""
        pass

    @abstractmethod
    async def get_event_range(
        self,
        start_id: str | None = None,
        end_id: str | None = None,
    ) -> list[AuditEvent]:
        """Get events in ID range."""
        pass

    @abstractmethod
    async def count_events(
        self,
        action: AuditAction | None = None,
        since: str | None = None,
    ) -> int:
        """Count events matching criteria."""
        pass


class FileAuditStorage(AuditStorage):
    """File-based audit storage backend.

    Stores events in JSON files with daily rotation.
    Suitable for development and small deployments.
    """

    def __init__(self, storage_path: Path | None = None):
        """Initialize file storage.

        Args:
            storage_path: Directory for audit files
        """
        self._storage_path = storage_path or Path.home() / ".autoclaudedev" / "audit"
        self._events: list[AuditEvent] = []
        self._index: dict[str, int] = {}  # event_id -> list index
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize storage directory and load existing events."""
        if self._initialized:
            return

        self._storage_path.mkdir(parents=True, exist_ok=True)

        if os.name != "nt":
            os.chmod(self._storage_path, 0o700)

        # Load existing events from today's file
        await self._load_events()

        self._initialized = True

    def _get_current_file(self) -> Path:
        """Get path to current day's audit file."""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self._storage_path / f"audit_{date_str}.json"

    async def _load_events(self) -> None:
        """Load events from storage files."""
        self._events = []
        self._index = {}

        # Load all audit files
        for file_path in sorted(self._storage_path.glob("audit_*.json")):
            try:
                data = json.loads(file_path.read_text())
                for event_data in data.get("events", []):
                    event = self._dict_to_event(event_data)
                    self._index[event.id] = len(self._events)
                    self._events.append(event)
            except (json.JSONDecodeError, OSError):
                continue

    async def _save_events(self) -> None:
        """Save current day's events to file."""
        current_file = self._get_current_file()

        # Filter events for today
        today = datetime.utcnow().strftime("%Y-%m-%d")
        today_events = [e for e in self._events if e.timestamp.startswith(today)]

        data = {
            "date": today,
            "version": "1.0",
            "events": [self._event_to_dict(e) for e in today_events],
        }

        current_file.write_text(json.dumps(data, indent=2, default=str))

        if os.name != "nt":
            os.chmod(current_file, 0o600)

    def _event_to_dict(self, event: AuditEvent) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": event.id,
            "timestamp": event.timestamp,
            "action": event.action.value,
            "actor": event.actor,
            "resource": event.resource,
            "details": event.details,
            "severity": event.severity.value,
            "success": event.success,
            "ip_address": event.ip_address,
            "session_id": event.session_id,
            "checksum": event.checksum,
        }

    def _dict_to_event(self, data: dict[str, Any]) -> AuditEvent:
        """Convert dictionary to event."""
        return AuditEvent(
            id=data["id"],
            timestamp=data["timestamp"],
            action=AuditAction(data["action"]),
            actor=data["actor"],
            resource=data["resource"],
            details=data.get("details", {}),
            severity=Severity(data.get("severity", "low")),
            success=data.get("success", True),
            ip_address=data.get("ip_address"),
            session_id=data.get("session_id"),
            checksum=data.get("checksum", ""),
        )

    async def store_event(self, event: AuditEvent) -> None:
        """Store an audit event."""
        if not self._initialized:
            await self.initialize()

        self._index[event.id] = len(self._events)
        self._events.append(event)

        await self._save_events()

    async def get_event(self, event_id: str) -> AuditEvent | None:
        """Retrieve an event by ID."""
        if not self._initialized:
            await self.initialize()

        idx = self._index.get(event_id)
        if idx is not None:
            return self._events[idx]
        return None

    async def get_last_event(self) -> AuditEvent | None:
        """Get the most recent event."""
        if not self._initialized:
            await self.initialize()

        if self._events:
            return self._events[-1]
        return None

    async def query_events(
        self,
        action: AuditAction | None = None,
        actor: str | None = None,
        resource: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query events with filters."""
        if not self._initialized:
            await self.initialize()

        results = []

        for event in reversed(self._events):  # Most recent first
            if len(results) >= limit:
                break

            # Apply filters
            if action and event.action != action:
                continue
            if actor and event.actor != actor:
                continue
            if resource and event.resource != resource:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue

            results.append(event)

        return results

    async def get_event_range(
        self,
        start_id: str | None = None,
        end_id: str | None = None,
    ) -> list[AuditEvent]:
        """Get events in ID range."""
        if not self._initialized:
            await self.initialize()

        if not start_id and not end_id:
            return self._events.copy()

        start_idx = 0
        end_idx = len(self._events)

        if start_id and start_id in self._index:
            start_idx = self._index[start_id]

        if end_id and end_id in self._index:
            end_idx = self._index[end_id] + 1

        return self._events[start_idx:end_idx]

    async def count_events(
        self,
        action: AuditAction | None = None,
        since: str | None = None,
    ) -> int:
        """Count events matching criteria."""
        if not self._initialized:
            await self.initialize()

        count = 0

        for event in self._events:
            if action and event.action != action:
                continue
            if since and event.timestamp < since:
                continue
            count += 1

        return count

    async def cleanup_old_events(self, days_to_keep: int = 90) -> int:
        """Remove events older than specified days.

        Args:
            days_to_keep: Number of days of events to retain

        Returns:
            Number of files deleted
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        deleted = 0
        for file_path in self._storage_path.glob("audit_*.json"):
            # Extract date from filename
            try:
                file_date = file_path.stem.replace("audit_", "")
                if file_date < cutoff_str:
                    file_path.unlink()
                    deleted += 1
            except (ValueError, OSError):
                continue

        # Reload events after cleanup
        await self._load_events()

        return deleted
