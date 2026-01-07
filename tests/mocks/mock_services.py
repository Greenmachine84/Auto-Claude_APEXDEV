"""
Mock services for testing.

Provides mock implementations of external services including
HTTP clients, databases, caches, message queues, and file systems.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import asyncio
import json


class HttpMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HttpStatus(Enum):
    """Common HTTP status codes."""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


@dataclass
class HttpRequest:
    """HTTP request representation."""
    method: HttpMethod
    url: str
    headers: dict = field(default_factory=dict)
    body: Any = None
    params: dict = field(default_factory=dict)


@dataclass
class HttpResponse:
    """HTTP response representation."""
    status: int
    body: Any
    headers: dict = field(default_factory=dict)


class MockHttpClient:
    """Mock HTTP client for testing."""

    def __init__(self):
        self._responses: dict[tuple[str, str], HttpResponse] = {}
        self._request_history: list[HttpRequest] = []
        self._latency_ms = 0.0
        self._error_mode = False
        self._error: Optional[Exception] = None

    def set_response(
        self,
        method: HttpMethod,
        url: str,
        response: HttpResponse
    ) -> None:
        """Set canned response for request."""
        self._responses[(method.value, url)] = response

    def set_latency(self, latency_ms: float) -> None:
        """Set simulated latency."""
        self._latency_ms = latency_ms

    def set_error(self, error: Exception) -> None:
        """Set error mode."""
        self._error_mode = True
        self._error = error

    def clear_error(self) -> None:
        """Clear error mode."""
        self._error_mode = False
        self._error = None

    async def request(
        self,
        method: HttpMethod,
        url: str,
        **kwargs
    ) -> HttpResponse:
        """Make an HTTP request."""
        request = HttpRequest(
            method=method,
            url=url,
            headers=kwargs.get("headers", {}),
            body=kwargs.get("body") or kwargs.get("json"),
            params=kwargs.get("params", {})
        )
        self._request_history.append(request)

        if self._latency_ms > 0:
            await asyncio.sleep(self._latency_ms / 1000)

        if self._error_mode and self._error:
            raise self._error

        key = (method.value, url)
        if key in self._responses:
            return self._responses[key]

        return HttpResponse(
            status=HttpStatus.NOT_FOUND.value,
            body={"error": "Not found"}
        )

    async def get(self, url: str, **kwargs) -> HttpResponse:
        """GET request."""
        return await self.request(HttpMethod.GET, url, **kwargs)

    async def post(self, url: str, **kwargs) -> HttpResponse:
        """POST request."""
        return await self.request(HttpMethod.POST, url, **kwargs)

    async def put(self, url: str, **kwargs) -> HttpResponse:
        """PUT request."""
        return await self.request(HttpMethod.PUT, url, **kwargs)

    async def delete(self, url: str, **kwargs) -> HttpResponse:
        """DELETE request."""
        return await self.request(HttpMethod.DELETE, url, **kwargs)

    def get_request_history(self) -> list[HttpRequest]:
        """Get request history."""
        return self._request_history.copy()

    def clear_history(self) -> None:
        """Clear request history."""
        self._request_history.clear()


class MockDatabase:
    """Mock database for testing."""

    def __init__(self):
        self._tables: dict[str, list[dict]] = {}
        self._connected = False
        self._transaction_active = False
        self._query_history: list[dict] = []

    async def connect(self) -> bool:
        """Connect to database."""
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Disconnect from database."""
        self._connected = False

    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected

    async def execute(self, query: str, params: tuple = ()) -> int:
        """Execute a query."""
        self._query_history.append({
            "type": "execute",
            "query": query,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })
        return 1  # Affected rows

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[dict]:
        """Fetch one row."""
        self._query_history.append({
            "type": "fetch_one",
            "query": query,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })

        # Simple mock query parsing
        if "FROM" in query.upper():
            table = query.upper().split("FROM")[1].split()[0].lower()
            rows = self._tables.get(table, [])
            return rows[0] if rows else None

        return None

    async def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        """Fetch all rows."""
        self._query_history.append({
            "type": "fetch_all",
            "query": query,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })

        if "FROM" in query.upper():
            table = query.upper().split("FROM")[1].split()[0].lower()
            return self._tables.get(table, [])

        return []

    async def begin_transaction(self) -> None:
        """Begin a transaction."""
        self._transaction_active = True

    async def commit(self) -> None:
        """Commit transaction."""
        self._transaction_active = False

    async def rollback(self) -> None:
        """Rollback transaction."""
        self._transaction_active = False

    def seed_table(self, table: str, rows: list[dict]) -> None:
        """Seed a table with data."""
        self._tables[table] = rows

    def get_query_history(self) -> list[dict]:
        """Get query history."""
        return self._query_history.copy()


class MockCache:
    """Mock cache for testing."""

    def __init__(self, default_ttl: int = 300):
        self._data: dict[str, tuple[Any, datetime]] = {}
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key in self._data:
            value, expiry = self._data[key]
            if datetime.now() < expiry:
                self._hits += 1
                return value
            else:
                del self._data[key]

        self._misses += 1
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set a value in cache."""
        ttl = ttl or self._default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._data[key] = (value, expiry)
        return True

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.get(key) is not None

    async def clear(self) -> int:
        """Clear all cache."""
        count = len(self._data)
        self._data.clear()
        return count

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
            "size": len(self._data)
        }


@dataclass
class QueueMessage:
    """Message in a queue."""
    id: str
    body: Any
    created_at: datetime = field(default_factory=datetime.now)
    attempts: int = 0


class MockMessageQueue:
    """Mock message queue for testing."""

    def __init__(self):
        self._queues: dict[str, list[QueueMessage]] = {}
        self._message_counter = 0
        self._handlers: dict[str, Callable] = {}

    async def publish(self, queue: str, message: Any) -> str:
        """Publish a message to a queue."""
        if queue not in self._queues:
            self._queues[queue] = []

        self._message_counter += 1
        msg_id = f"msg-{self._message_counter}"

        queue_msg = QueueMessage(id=msg_id, body=message)
        self._queues[queue].append(queue_msg)

        return msg_id

    async def consume(
        self,
        queue: str,
        count: int = 1
    ) -> list[QueueMessage]:
        """Consume messages from a queue."""
        if queue not in self._queues:
            return []

        messages = []
        for _ in range(count):
            if self._queues[queue]:
                msg = self._queues[queue].pop(0)
                msg.attempts += 1
                messages.append(msg)

        return messages

    async def peek(self, queue: str) -> Optional[QueueMessage]:
        """Peek at next message without consuming."""
        if queue in self._queues and self._queues[queue]:
            return self._queues[queue][0]
        return None

    async def queue_length(self, queue: str) -> int:
        """Get queue length."""
        return len(self._queues.get(queue, []))

    async def purge(self, queue: str) -> int:
        """Purge all messages from queue."""
        if queue in self._queues:
            count = len(self._queues[queue])
            self._queues[queue].clear()
            return count
        return 0


class MockFileSystem:
    """Mock file system for testing."""

    def __init__(self):
        self._files: dict[str, bytes] = {}
        self._directories: set[str] = set()

    async def read(self, path: str) -> Optional[bytes]:
        """Read file contents."""
        return self._files.get(path)

    async def write(self, path: str, content: bytes) -> bool:
        """Write file contents."""
        # Ensure parent directory exists
        parent = "/".join(path.split("/")[:-1])
        if parent:
            self._directories.add(parent)
        self._files[path] = content
        return True

    async def delete(self, path: str) -> bool:
        """Delete a file."""
        if path in self._files:
            del self._files[path]
            return True
        return False

    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        return path in self._files or path in self._directories

    async def list_dir(self, path: str) -> list[str]:
        """List directory contents."""
        results = []
        prefix = path.rstrip("/") + "/"
        for file_path in self._files:
            if file_path.startswith(prefix):
                relative = file_path[len(prefix):]
                if "/" not in relative:
                    results.append(relative)
        return results

    async def mkdir(self, path: str) -> bool:
        """Create directory."""
        self._directories.add(path)
        return True

    async def rmdir(self, path: str) -> bool:
        """Remove directory."""
        if path in self._directories:
            self._directories.remove(path)
            return True
        return False

    def seed_file(self, path: str, content: str) -> None:
        """Seed a file with content."""
        self._files[path] = content.encode()

    def get_all_files(self) -> list[str]:
        """Get all file paths."""
        return list(self._files.keys())
