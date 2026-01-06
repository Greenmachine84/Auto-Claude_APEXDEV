"""Knowledge graph for semantic relationships.

Part of Phase 2: Memory System Architecture
"""

import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class EdgeType(Enum):
    RELATES_TO = "relates_to"
    DERIVED_FROM = "derived_from"
    CAUSED_BY = "caused_by"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    IMPLEMENTS = "implements"
    USES = "uses"


@dataclass
class KGNode:
    """A node in the knowledge graph."""
    id: str
    node_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "node_type": self.node_type, "name": self.name,
                "properties": self.properties, "created_at": self.created_at.isoformat()}


@dataclass
class KGEdge:
    """An edge connecting two nodes."""
    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "source_id": self.source_id, "target_id": self.target_id,
                "edge_type": self.edge_type.value, "weight": self.weight,
                "properties": self.properties, "created_at": self.created_at.isoformat()}


class KnowledgeGraph:
    """SQLite-backed knowledge graph."""
    
    def __init__(self, db_path: str):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._init_db()
    
    def _init_db(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT,
                embedding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES nodes(id),
                FOREIGN KEY (target_id) REFERENCES nodes(id)
            );
            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
            CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
        """)
        self._conn.commit()
    
    def add_node(self, node: KGNode) -> str:
        self._conn.execute(
            "INSERT OR REPLACE INTO nodes (id, node_type, name, properties, embedding, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (node.id, node.node_type, node.name, json.dumps(node.properties),
             json.dumps(node.embedding) if node.embedding else None, node.created_at)
        )
        self._conn.commit()
        return node.id
    
    def add_edge(self, edge: KGEdge) -> str:
        self._conn.execute(
            "INSERT OR REPLACE INTO edges (id, source_id, target_id, edge_type, weight, properties, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (edge.id, edge.source_id, edge.target_id, edge.edge_type.value, edge.weight, json.dumps(edge.properties), edge.created_at)
        )
        self._conn.commit()
        return edge.id
    
    def get_node(self, node_id: str) -> Optional[KGNode]:
        row = self._conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)).fetchone()
        if not row:
            return None
        return KGNode(id=row[0], node_type=row[1], name=row[2], properties=json.loads(row[3] or "{}"),
                     embedding=json.loads(row[4]) if row[4] else None, created_at=row[5])
    
    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[KGNode]:
        query = "SELECT target_id FROM edges WHERE source_id = ?"
        params: List[Any] = [node_id]
        if edge_type:
            query += " AND edge_type = ?"
            params.append(edge_type.value)
        
        rows = self._conn.execute(query, params).fetchall()
        nodes = []
        for (target_id,) in rows:
            node = self.get_node(target_id)
            if node:
                nodes.append(node)
        return nodes
    
    def traverse(self, start_id: str, max_depth: int = 3) -> Dict[str, Set[str]]:
        visited: Dict[str, Set[str]] = {"nodes": set(), "edges": set()}
        self._dfs(start_id, 0, max_depth, visited)
        return visited
    
    def _dfs(self, node_id: str, depth: int, max_depth: int, visited: Dict[str, Set[str]]) -> None:
        if depth > max_depth or node_id in visited["nodes"]:
            return
        visited["nodes"].add(node_id)
        
        edges = self._conn.execute(
            "SELECT id, target_id FROM edges WHERE source_id = ?", (node_id,)
        ).fetchall()
        
        for edge_id, target_id in edges:
            visited["edges"].add(edge_id)
            self._dfs(target_id, depth + 1, max_depth, visited)
