"""Promotion and demotion policies for H-MEM.

Part of Phase 2: Memory System Architecture
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class AccessPattern:
    """Track access patterns for a key."""

    key: str
    access_count: int = 0
    last_access: datetime = field(default_factory=datetime.utcnow)
    first_access: datetime = field(default_factory=datetime.utcnow)


class PromotionPolicy:
    """Determines when to promote data to higher tiers."""

    def __init__(
        self,
        min_access_count: int = 3,
        access_window: timedelta = timedelta(minutes=5),
        frequency_threshold: float = 0.5,
    ):
        self._min_access = min_access_count
        self._window = access_window
        self._threshold = frequency_threshold
        self._patterns: dict[str, AccessPattern] = {}

    def record_access(self, key: str) -> None:
        now = datetime.utcnow()
        if key not in self._patterns:
            self._patterns[key] = AccessPattern(key=key, first_access=now)

        pattern = self._patterns[key]
        pattern.access_count += 1
        pattern.last_access = now

    def should_promote(self, key: str) -> bool:
        pattern = self._patterns.get(key)
        if pattern is None:
            return False

        now = datetime.utcnow()
        age = now - pattern.first_access

        if pattern.access_count < self._min_access:
            return False

        if age < self._window:
            frequency = pattern.access_count / max(age.total_seconds(), 1)
            return frequency >= self._threshold

        return pattern.access_count >= self._min_access * 2

    def clear(self) -> None:
        self._patterns.clear()


class DemotionPolicy:
    """Determines when to demote data to lower tiers."""

    def __init__(
        self,
        idle_threshold: timedelta = timedelta(minutes=10),
        max_idle_count: int = 100,
    ):
        self._idle_threshold = idle_threshold
        self._max_idle = max_idle_count
        self._access_times: dict[str, datetime] = {}

    def record_access(self, key: str) -> None:
        self._access_times[key] = datetime.utcnow()

    def should_demote(self, key: str) -> bool:
        last_access = self._access_times.get(key)
        if last_access is None:
            return True

        idle_time = datetime.utcnow() - last_access
        return idle_time > self._idle_threshold

    def get_idle_keys(self, limit: int = 100) -> list:
        now = datetime.utcnow()
        idle_keys = [
            (key, now - access_time)
            for key, access_time in self._access_times.items()
            if now - access_time > self._idle_threshold
        ]
        idle_keys.sort(key=lambda x: x[1], reverse=True)
        return [key for key, _ in idle_keys[:limit]]

    def clear(self) -> None:
        self._access_times.clear()
