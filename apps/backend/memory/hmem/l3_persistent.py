"""L3 persistent storage tier.

Part of Phase 2: Memory System Architecture
"""

import json
import logging
import pickle
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class L3PersistentStore(Generic[T]):
    """SQLite-backed persistent storage."""

    def __init__(self, db_path: str):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                value_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_storage_created ON storage(created_at)"
        )
        self._conn.commit()

    def get(self, key: str) -> T | None:
        row = self._conn.execute(
            "SELECT value, value_type FROM storage WHERE key = ?", (key,)
        ).fetchone()

        if row is None:
            return None

        self._conn.execute(
            "UPDATE storage SET access_count = access_count + 1 WHERE key = ?", (key,)
        )
        self._conn.commit()

        return self._deserialize(row[0], row[1])

    def set(self, key: str, value: T, metadata: dict | None = None) -> None:
        serialized, value_type = self._serialize(value)
        now = datetime.utcnow()

        self._conn.execute(
            """INSERT OR REPLACE INTO storage 
               (key, value, value_type, created_at, updated_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (key, serialized, value_type, now, now, json.dumps(metadata or {})),
        )
        self._conn.commit()

    def delete(self, key: str) -> bool:
        cursor = self._conn.execute("DELETE FROM storage WHERE key = ?", (key,))
        self._conn.commit()
        return cursor.rowcount > 0

    def clear(self) -> int:
        cursor = self._conn.execute("DELETE FROM storage")
        self._conn.commit()
        return cursor.rowcount

    def size(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM storage").fetchone()[0]

    def _serialize(self, value: T) -> tuple[bytes, str]:
        try:
            return json.dumps(value).encode(), "json"
        except (TypeError, ValueError):
            return pickle.dumps(value), "pickle"

    def _deserialize(self, data: bytes, value_type: str) -> T:
        if value_type == "json":
            return json.loads(data.decode())
        return pickle.loads(data)

    def vacuum(self) -> None:
        self._conn.execute("VACUUM")

    def close(self) -> None:
        self._conn.close()
