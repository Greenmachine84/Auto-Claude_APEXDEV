"""SQLite-based episode storage with FTS5 full-text search.

Part of Phase 2: Memory System Architecture
"""

import json
import logging
import sqlite3
import threading
from pathlib import Path

from ..types.episode_types import EpisodeOutcome, EpisodeRecord

logger = logging.getLogger(__name__)


class EpisodeStore:
    """SQLite-based persistent episode storage."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS episodes (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        agent_type TEXT,
        task_id TEXT,
        input_text TEXT,
        output_text TEXT,
        reasoning TEXT,
        outcome TEXT NOT NULL,
        severity INTEGER DEFAULT 2,
        tools_used TEXT,
        tool_invocations TEXT,
        duration_ms INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT,
        embedding BLOB
    );
    
    CREATE INDEX IF NOT EXISTS idx_episodes_agent ON episodes(agent_id);
    CREATE INDEX IF NOT EXISTS idx_episodes_task ON episodes(task_id);
    CREATE INDEX IF NOT EXISTS idx_episodes_created ON episodes(created_at);
    CREATE INDEX IF NOT EXISTS idx_episodes_outcome ON episodes(outcome);
    
    CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
        input_text, output_text, reasoning,
        content=episodes, content_rowid=rowid
    );
    
    CREATE TRIGGER IF NOT EXISTS episodes_ai AFTER INSERT ON episodes BEGIN
        INSERT INTO episodes_fts(rowid, input_text, output_text, reasoning)
        VALUES (new.rowid, new.input_text, new.output_text, new.reasoning);
    END;
    
    CREATE TRIGGER IF NOT EXISTS episodes_ad AFTER DELETE ON episodes BEGIN
        INSERT INTO episodes_fts(episodes_fts, rowid, input_text, output_text, reasoning)
        VALUES('delete', old.rowid, old.input_text, old.output_text, old.reasoning);
    END;
    """

    def __init__(self, db_path: str, enable_wal: bool = True):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._enable_wal = enable_wal
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self._db_path), detect_types=sqlite3.PARSE_DECLTYPES
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        if self._enable_wal:
            conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(self.SCHEMA)
        conn.commit()
        logger.info("Episode store initialized: %s", self._db_path)

    def store(self, episode: EpisodeRecord) -> str:
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO episodes 
               (id, agent_id, agent_type, task_id, input_text, output_text,
                reasoning, outcome, severity, tools_used, tool_invocations,
                duration_ms, created_at, updated_at, metadata, embedding)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                episode.id,
                episode.agent_id,
                episode.agent_type,
                episode.task_id,
                episode.input_text,
                episode.output_text,
                episode.reasoning,
                episode.outcome.value,
                episode.severity.value,
                json.dumps(episode.tools_used),
                json.dumps([t.to_dict() for t in episode.tool_invocations]),
                episode.duration_ms,
                episode.created_at,
                episode.updated_at,
                json.dumps(episode.metadata.to_dict()),
                json.dumps(episode.embedding) if episode.embedding else None,
            ),
        )
        conn.commit()
        return episode.id

    def get(self, episode_id: str) -> EpisodeRecord | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM episodes WHERE id = ?", (episode_id,)
        ).fetchone()
        return self._row_to_episode(row) if row else None

    def search_text(self, query: str, limit: int = 50) -> list[EpisodeRecord]:
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT e.* FROM episodes e
               JOIN episodes_fts fts ON e.rowid = fts.rowid
               WHERE episodes_fts MATCH ?
               ORDER BY rank LIMIT ?""",
            (query, limit),
        ).fetchall()
        return [self._row_to_episode(r) for r in rows]

    def delete(self, episode_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(self) -> int:
        conn = self._get_conn()
        return conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]

    def _row_to_episode(self, row: sqlite3.Row) -> EpisodeRecord:
        from ..types.episode_types import (
            EpisodeMetadata,
            EpisodeSeverity,
            ToolInvocation,
        )

        return EpisodeRecord(
            id=row["id"],
            agent_id=row["agent_id"],
            agent_type=row["agent_type"] or "",
            task_id=row["task_id"],
            input_text=row["input_text"],
            output_text=row["output_text"],
            reasoning=row["reasoning"],
            outcome=EpisodeOutcome(row["outcome"]),
            severity=EpisodeSeverity(row["severity"]),
            tools_used=json.loads(row["tools_used"] or "[]"),
            tool_invocations=[
                ToolInvocation.from_dict(t)
                for t in json.loads(row["tool_invocations"] or "[]")
            ],
            duration_ms=row["duration_ms"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            metadata=EpisodeMetadata.from_dict(json.loads(row["metadata"] or "{}")),
            embedding=json.loads(row["embedding"]) if row["embedding"] else None,
        )

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
