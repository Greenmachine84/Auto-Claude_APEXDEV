"""Memory bridge for cross-system synchronization.

Provides synchronization with external memory systems
like Graphiti, import/export functionality, and
conflict resolution.

Part of Phase 2: Memory System Architecture
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol

from ..types.episode_types import EpisodeRecord

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Status of synchronization operation."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CONFLICT = "conflict"
    SKIPPED = "skipped"


@dataclass
class SyncResult:
    """Result of a synchronization operation."""

    status: SyncStatus
    synced_count: int = 0
    failed_count: int = 0
    conflict_count: int = 0
    errors: list[str] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "synced_count": self.synced_count,
            "failed_count": self.failed_count,
            "conflict_count": self.conflict_count,
            "errors": self.errors,
            "conflicts": self.conflicts,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


class ConflictResolution(Enum):
    """Strategies for conflict resolution."""

    LOCAL_WINS = "local_wins"  # Keep local version
    REMOTE_WINS = "remote_wins"  # Keep remote version
    MERGE = "merge"  # Attempt merge
    MANUAL = "manual"  # Require manual resolution
    NEWEST = "newest"  # Keep newest by timestamp


class ExternalMemoryProvider(Protocol):
    """Protocol for external memory system providers."""

    async def connect(self) -> bool:
        """Establish connection to external system."""
        ...

    async def disconnect(self) -> None:
        """Close connection."""
        ...

    async def fetch_episodes(
        self, since: datetime | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch episodes from external system."""
        ...

    async def push_episodes(self, episodes: list[EpisodeRecord]) -> SyncResult:
        """Push episodes to external system."""
        ...


@dataclass
class BridgeConfig:
    """Configuration for memory bridge."""

    enabled: bool = True
    sync_interval_seconds: int = 60
    conflict_resolution: ConflictResolution = ConflictResolution.NEWEST
    batch_size: int = 100
    max_retries: int = 3
    retry_delay_seconds: int = 5
    sync_on_startup: bool = True
    sync_on_shutdown: bool = True


class MemoryBridge:
    """Bridge for synchronizing with external memory systems.

    Supports bidirectional sync with external systems like
    Graphiti, handling conflicts and ensuring data consistency.

    Usage:
        bridge = MemoryBridge(config)
        bridge.register_provider("graphiti", graphiti_provider)

        # Manual sync
        result = await bridge.sync("graphiti")

        # Start background sync
        await bridge.start_background_sync()
    """

    def __init__(self, config: BridgeConfig | None = None):
        """Initialize memory bridge.

        Args:
            config: Bridge configuration
        """
        self._config = config or BridgeConfig()
        self._providers: dict[str, ExternalMemoryProvider] = {}
        self._local_store: Any | None = None
        self._sync_task: asyncio.Task | None = None
        self._last_sync: dict[str, datetime] = {}
        self._sync_callbacks: list[Callable[[str, SyncResult], None]] = []

    def register_provider(self, name: str, provider: ExternalMemoryProvider) -> None:
        """Register an external memory provider.

        Args:
            name: Provider name (e.g., "graphiti")
            provider: Provider instance implementing protocol
        """
        self._providers[name] = provider
        logger.info("Registered memory provider: %s", name)

    def unregister_provider(self, name: str) -> None:
        """Unregister a provider."""
        if name in self._providers:
            del self._providers[name]
            logger.info("Unregistered memory provider: %s", name)

    def set_local_store(self, store: Any) -> None:
        """Set reference to local memory store."""
        self._local_store = store

    def add_sync_callback(self, callback: Callable[[str, SyncResult], None]) -> None:
        """Add callback to be notified of sync results."""
        self._sync_callbacks.append(callback)

    async def sync(
        self, provider_name: str | None = None, direction: str = "bidirectional"
    ) -> dict[str, SyncResult]:
        """Synchronize with external providers.

        Args:
            provider_name: Specific provider or None for all
            direction: "push", "pull", or "bidirectional"

        Returns:
            Dict mapping provider names to sync results
        """
        results: dict[str, SyncResult] = {}

        providers = (
            {provider_name: self._providers[provider_name]}
            if provider_name and provider_name in self._providers
            else self._providers
        )

        for name, provider in providers.items():
            try:
                result = await self._sync_provider(name, provider, direction)
                results[name] = result
                self._last_sync[name] = datetime.utcnow()

                # Notify callbacks
                for callback in self._sync_callbacks:
                    try:
                        callback(name, result)
                    except Exception as e:
                        logger.error("Sync callback error: %s", e)

            except Exception as e:
                logger.error("Sync failed for %s: %s", name, e)
                results[name] = SyncResult(status=SyncStatus.FAILED, errors=[str(e)])

        return results

    async def start_background_sync(self) -> None:
        """Start background synchronization task."""
        if not self._config.enabled:
            logger.info("Background sync disabled")
            return

        if self._sync_task and not self._sync_task.done():
            logger.warning("Background sync already running")
            return

        # Sync on startup if configured
        if self._config.sync_on_startup:
            await self.sync()

        self._sync_task = asyncio.create_task(self._background_sync_loop())
        logger.info(
            "Started background sync (interval=%ds)", self._config.sync_interval_seconds
        )

    async def stop_background_sync(self) -> None:
        """Stop background synchronization."""
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
            self._sync_task = None

        # Sync on shutdown if configured
        if self._config.sync_on_shutdown:
            await self.sync(direction="push")

        logger.info("Stopped background sync")

    async def import_data(
        self, source: str, data: list[dict[str, Any]], overwrite: bool = False
    ) -> SyncResult:
        """Import data from external source.

        Args:
            source: Source identifier
            data: List of episode data dictionaries
            overwrite: Whether to overwrite existing records

        Returns:
            Import result
        """
        start_time = datetime.utcnow()
        synced = 0
        failed = 0
        conflicts = 0
        errors: list[str] = []
        conflict_records: list[dict[str, Any]] = []

        for item in data:
            try:
                # Convert to episode record
                episode = EpisodeRecord.from_dict(item)

                # Check for existing
                existing = await self._get_local_episode(episode.id)

                if existing:
                    if overwrite:
                        await self._update_local_episode(episode)
                        synced += 1
                    else:
                        # Conflict
                        resolved = await self._resolve_conflict(existing, episode)
                        if resolved:
                            await self._update_local_episode(resolved)
                            synced += 1
                        else:
                            conflicts += 1
                            conflict_records.append(item)
                else:
                    await self._store_local_episode(episode)
                    synced += 1

            except Exception as e:
                failed += 1
                errors.append(f"Failed to import item: {e}")

        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        status = SyncStatus.SUCCESS
        if failed > 0 or conflicts > 0:
            status = SyncStatus.PARTIAL if synced > 0 else SyncStatus.FAILED

        return SyncResult(
            status=status,
            synced_count=synced,
            failed_count=failed,
            conflict_count=conflicts,
            errors=errors,
            conflicts=conflict_records,
            duration_ms=duration,
        )

    async def export_data(
        self, since: datetime | None = None, agent_ids: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Export data for backup or transfer.

        Args:
            since: Only export records after this timestamp
            agent_ids: Filter to specific agents

        Returns:
            List of episode data dictionaries
        """
        episodes = await self._get_local_episodes(since=since, agent_ids=agent_ids)
        return [ep.to_dict() for ep in episodes]

    # ===== Private Methods =====

    async def _sync_provider(
        self, name: str, provider: ExternalMemoryProvider, direction: str
    ) -> SyncResult:
        """Sync with a single provider."""
        start_time = datetime.utcnow()

        # Connect to provider
        if not await provider.connect():
            return SyncResult(
                status=SyncStatus.FAILED, errors=[f"Failed to connect to {name}"]
            )

        try:
            synced = 0
            failed = 0
            conflicts_list: list[dict[str, Any]] = []
            errors: list[str] = []

            # Pull from remote
            if direction in ("pull", "bidirectional"):
                last_sync = self._last_sync.get(name)
                remote_episodes = await provider.fetch_episodes(
                    since=last_sync, limit=self._config.batch_size
                )

                for remote_data in remote_episodes:
                    try:
                        episode = EpisodeRecord.from_dict(remote_data)
                        await self._store_local_episode(episode)
                        synced += 1
                    except Exception as e:
                        failed += 1
                        errors.append(str(e))

            # Push to remote
            if direction in ("push", "bidirectional"):
                local_episodes = await self._get_local_episodes(
                    since=self._last_sync.get(name)
                )

                if local_episodes:
                    result = await provider.push_episodes(local_episodes)
                    synced += result.synced_count
                    failed += result.failed_count
                    errors.extend(result.errors)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            status = SyncStatus.SUCCESS
            if failed > 0:
                status = SyncStatus.PARTIAL if synced > 0 else SyncStatus.FAILED

            return SyncResult(
                status=status,
                synced_count=synced,
                failed_count=failed,
                errors=errors,
                conflicts=conflicts_list,
                duration_ms=duration,
            )

        finally:
            await provider.disconnect()

    async def _background_sync_loop(self) -> None:
        """Background sync loop."""
        while True:
            try:
                await asyncio.sleep(self._config.sync_interval_seconds)
                await self.sync()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Background sync error: %s", e)

    async def _resolve_conflict(
        self, local: EpisodeRecord, remote: EpisodeRecord
    ) -> EpisodeRecord | None:
        """Resolve conflict between local and remote records."""
        strategy = self._config.conflict_resolution

        if strategy == ConflictResolution.LOCAL_WINS:
            return local
        elif strategy == ConflictResolution.REMOTE_WINS:
            return remote
        elif strategy == ConflictResolution.NEWEST:
            return local if local.updated_at >= remote.updated_at else remote
        elif strategy == ConflictResolution.MERGE:
            # Simple merge: combine metadata, keep newer content
            merged = remote if remote.updated_at >= local.updated_at else local
            merged.metadata.tags = list(set(local.metadata.tags + remote.metadata.tags))
            return merged
        else:
            # Manual resolution required
            return None

    async def _store_local_episode(self, episode: EpisodeRecord) -> None:
        """Store episode in local store."""
        # Placeholder - actual implementation uses MemoryManager
        pass

    async def _update_local_episode(self, episode: EpisodeRecord) -> None:
        """Update episode in local store."""
        # Placeholder - actual implementation uses MemoryManager
        pass

    async def _get_local_episode(self, episode_id: str) -> EpisodeRecord | None:
        """Get episode from local store."""
        # Placeholder - actual implementation uses MemoryManager
        return None

    async def _get_local_episodes(
        self, since: datetime | None = None, agent_ids: list[str] | None = None
    ) -> list[EpisodeRecord]:
        """Get episodes from local store."""
        # Placeholder - actual implementation uses MemoryManager
        return []
