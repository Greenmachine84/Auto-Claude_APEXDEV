"""
Metrics Storage - Phase 8 Implementation.

Persistence layer for analytics metrics.

World-Class Standards:
- Write-ahead logging for durability
- Efficient querying with indexes
- Configurable retention policies
- Multiple storage backend support
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import json
import sqlite3
from pathlib import Path

from ..models import MetricEvent, CostRecord, SUPPORTED_PROVIDERS
from ..config import AnalyticsConfig, default_config

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    async def store_event(self, event: MetricEvent) -> None:
        """Store a single event."""
        pass
    
    @abstractmethod
    async def store_events(self, events: List[MetricEvent]) -> None:
        """Store multiple events."""
        pass
    
    @abstractmethod
    async def store_cost_record(self, record: CostRecord) -> None:
        """Store a cost record."""
        pass
    
    @abstractmethod
    async def query_events(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[MetricEvent]:
        """Query events with filters."""
        pass
    
    @abstractmethod
    async def query_cost_records(
        self,
        user_id: str,
        provider: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[CostRecord]:
        """Query cost records."""
        pass
    
    @abstractmethod
    async def cleanup_old_data(self, retention_days: int) -> int:
        """Remove data older than retention period."""
        pass


class SQLiteStorage(StorageBackend):
    """
    SQLite storage backend for analytics.
    
    Features:
    - WAL mode for performance
    - Indexed queries
    - Automatic schema migration
    """
    
    def __init__(self, db_path: str = "analytics.db") -> None:
        """Initialize SQLite storage."""
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._initialized = False
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,
            )
            self._connection.row_factory = sqlite3.Row
            
            # Enable WAL mode for better performance
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=NORMAL")
            
            if not self._initialized:
                self._create_schema()
                self._initialized = True
        
        return self._connection
    
    def _create_schema(self) -> None:
        """Create database schema."""
        conn = self._get_connection()
        
        # Events table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metric_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                agent_id TEXT,
                provider TEXT,
                model TEXT,
                value REAL DEFAULT 1.0,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cost records table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cost_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                timestamp TEXT NOT NULL,
                agent_id TEXT,
                task_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for efficient queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_user_time 
            ON metric_events(user_id, timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_provider_time 
            ON metric_events(provider, timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_user_provider 
            ON cost_records(user_id, provider, timestamp)
        """)
        
        logger.info("SQLite schema initialized at %s", self.db_path)
    
    async def store_event(self, event: MetricEvent) -> None:
        """Store a single event."""
        conn = self._get_connection()
        
        conn.execute("""
            INSERT INTO metric_events 
            (id, event_type, timestamp, user_id, agent_id, provider, model, value, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id,
            event.event_type.value,
            event.timestamp,
            event.user_id,
            event.agent_id,
            event.provider,
            event.model,
            event.value,
            json.dumps(event.metadata),
        ))
    
    async def store_events(self, events: List[MetricEvent]) -> None:
        """Store multiple events in a batch."""
        if not events:
            return
        
        conn = self._get_connection()
        
        conn.executemany("""
            INSERT INTO metric_events 
            (id, event_type, timestamp, user_id, agent_id, provider, model, value, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                event.id,
                event.event_type.value,
                event.timestamp,
                event.user_id,
                event.agent_id,
                event.provider,
                event.model,
                event.value,
                json.dumps(event.metadata),
            )
            for event in events
        ])
        
        logger.debug("Stored %d events", len(events))
    
    async def store_cost_record(self, record: CostRecord) -> None:
        """Store a cost record."""
        conn = self._get_connection()
        
        conn.execute("""
            INSERT INTO cost_records 
            (id, user_id, provider, model, prompt_tokens, completion_tokens, 
             cost_usd, timestamp, agent_id, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id,
            record.user_id,
            record.provider,
            record.model,
            record.prompt_tokens,
            record.completion_tokens,
            record.cost_usd,
            record.timestamp,
            record.agent_id,
            record.task_id,
        ))
    
    async def query_events(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[MetricEvent]:
        """Query events with filters."""
        conn = self._get_connection()
        
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if provider:
            if provider not in SUPPORTED_PROVIDERS:
                raise ValueError(
                    f"Unknown provider: {provider}. "
                    f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
                )
            conditions.append("provider = ?")
            params.append(provider)
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.isoformat())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor = conn.execute(f"""
            SELECT * FROM metric_events 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        """, params + [limit])
        
        from ..models import EventType
        
        events = []
        for row in cursor.fetchall():
            events.append(MetricEvent(
                id=row["id"],
                event_type=EventType(row["event_type"]),
                timestamp=row["timestamp"],
                user_id=row["user_id"],
                agent_id=row["agent_id"],
                provider=row["provider"],
                model=row["model"],
                value=row["value"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            ))
        
        return events
    
    async def query_cost_records(
        self,
        user_id: str,
        provider: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[CostRecord]:
        """Query cost records."""
        conn = self._get_connection()
        
        conditions = ["user_id = ?"]
        params = [user_id]
        
        if provider:
            if provider not in SUPPORTED_PROVIDERS:
                raise ValueError(
                    f"Unknown provider: {provider}. "
                    f"Must be one of: {', '.join(SUPPORTED_PROVIDERS)}"
                )
            conditions.append("provider = ?")
            params.append(provider)
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.isoformat())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.isoformat())
        
        where_clause = " AND ".join(conditions)
        
        cursor = conn.execute(f"""
            SELECT * FROM cost_records 
            WHERE {where_clause}
            ORDER BY timestamp DESC
        """, params)
        
        records = []
        for row in cursor.fetchall():
            records.append(CostRecord(
                id=row["id"],
                user_id=row["user_id"],
                provider=row["provider"],
                model=row["model"],
                prompt_tokens=row["prompt_tokens"],
                completion_tokens=row["completion_tokens"],
                cost_usd=row["cost_usd"],
                timestamp=row["timestamp"],
                agent_id=row["agent_id"],
                task_id=row["task_id"],
            ))
        
        return records
    
    async def cleanup_old_data(self, retention_days: int) -> int:
        """Remove data older than retention period."""
        conn = self._get_connection()
        cutoff = (datetime.utcnow() - timedelta(days=retention_days)).isoformat()
        
        # Delete old events
        cursor = conn.execute(
            "DELETE FROM metric_events WHERE timestamp < ?",
            (cutoff,)
        )
        events_deleted = cursor.rowcount
        
        # Delete old cost records
        cursor = conn.execute(
            "DELETE FROM cost_records WHERE timestamp < ?",
            (cutoff,)
        )
        costs_deleted = cursor.rowcount
        
        total_deleted = events_deleted + costs_deleted
        if total_deleted > 0:
            logger.info(
                "Cleaned up %d events and %d cost records older than %d days",
                events_deleted, costs_deleted, retention_days
            )
        
        return total_deleted
    
    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


class MetricsStorage:
    """
    Main storage interface for metrics.
    
    Provides a unified interface for storing and querying metrics
    with configurable backend.
    """
    
    def __init__(self, config: Optional[AnalyticsConfig] = None) -> None:
        """Initialize metrics storage."""
        self.config = config or default_config
        
        # Initialize backend based on config
        if self.config.storage.storage_type == "sqlite":
            self._backend = SQLiteStorage(self.config.storage.sqlite_path)
        else:
            # Default to SQLite
            self._backend = SQLiteStorage(self.config.storage.sqlite_path)
        
        logger.info("MetricsStorage initialized with %s backend", 
                   self.config.storage.storage_type)
    
    async def store_event(self, event: MetricEvent) -> None:
        """Store a metric event."""
        await self._backend.store_event(event)
    
    async def store_events(self, events: List[MetricEvent]) -> None:
        """Store multiple events."""
        await self._backend.store_events(events)
    
    async def store_cost_record(self, record: CostRecord) -> None:
        """Store a cost record."""
        await self._backend.store_cost_record(record)
    
    async def query_events(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[MetricEvent]:
        """Query events."""
        return await self._backend.query_events(
            user_id, provider, start_time, end_time, limit
        )
    
    async def query_cost_records(
        self,
        user_id: str,
        provider: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[CostRecord]:
        """Query cost records."""
        return await self._backend.query_cost_records(
            user_id, provider, start_time, end_time
        )
    
    async def cleanup(self) -> int:
        """Cleanup old data based on retention policy."""
        return await self._backend.cleanup_old_data(
            self.config.metrics.retention_days
        )
    
    def close(self) -> None:
        """Close storage connections."""
        if hasattr(self._backend, "close"):
            self._backend.close()
