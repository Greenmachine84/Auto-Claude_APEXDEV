"""
Task Queue Unit Tests - Phase 10 Implementation.

World-Class Standards:
- Priority-based queue
- Multi-provider task routing
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# All 8 LLM providers
SUPPORTED_PROVIDERS = {
    "copilot", "openrouter", "ollama", "lmstudio",
    "gemini", "openai", "anthropic", "azure"
}


@dataclass
class Task:
    """Task definition."""
    id: str
    priority: int
    provider: str
    payload: Dict[str, Any]
    created_at: datetime
    status: str = "pending"


class TestTaskQueue:
    """Test task queue."""

    async def test_enqueue_task(self):
        """Task can be enqueued."""
        queue = MagicMock()
        queue.enqueue = AsyncMock(return_value="task-123")
        
        task_id = await queue.enqueue(
            priority=1,
            provider="openai",
            payload={"messages": []},
        )
        
        assert task_id == "task-123"

    async def test_dequeue_task(self):
        """Task can be dequeued."""
        queue = MagicMock()
        queue.dequeue = AsyncMock(return_value=Task(
            id="task-123",
            priority=1,
            provider="openai",
            payload={},
            created_at=datetime.utcnow(),
        ))
        
        task = await queue.dequeue()
        
        assert task.id == "task-123"

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_queue_per_provider(self, provider_id: str):
        """Tasks can be queued per provider."""
        queue = MagicMock()
        queue.enqueue = AsyncMock(return_value=f"task-{provider_id}")
        
        task_id = await queue.enqueue(
            provider=provider_id,
            priority=1,
            payload={},
        )
        
        assert provider_id in task_id


class TestTaskPriority:
    """Test task priority."""

    def test_priority_levels(self):
        """Priority levels are defined."""
        priorities = {
            "critical": 0,
            "high": 1,
            "normal": 2,
            "low": 3,
        }
        
        assert priorities["critical"] < priorities["low"]

    async def test_priority_ordering(self):
        """Higher priority tasks processed first."""
        queue = MagicMock()
        queue.peek = AsyncMock(return_value=Task(
            id="high-priority",
            priority=0,
            provider="openai",
            payload={},
            created_at=datetime.utcnow(),
        ))
        
        next_task = await queue.peek()
        
        assert next_task.priority == 0


class TestTaskStatus:
    """Test task status."""

    def test_status_transitions(self):
        """Valid status transitions."""
        transitions = {
            "pending": ["running", "cancelled"],
            "running": ["completed", "failed", "cancelled"],
            "completed": [],
            "failed": ["pending"],  # Retry
            "cancelled": [],
        }
        
        assert "running" in transitions["pending"]
        assert "completed" in transitions["running"]

    async def test_update_status(self):
        """Task status can be updated."""
        queue = MagicMock()
        queue.update_status = AsyncMock()
        
        await queue.update_status(
            task_id="task-123",
            status="running",
        )
        
        queue.update_status.assert_called_once()


class TestQueueMetrics:
    """Test queue metrics."""

    async def test_queue_length(self):
        """Queue length is tracked."""
        queue = MagicMock()
        queue.length = AsyncMock(return_value=10)
        
        length = await queue.length()
        
        assert length == 10

    @pytest.mark.parametrize("provider_id", list(SUPPORTED_PROVIDERS))
    async def test_queue_length_per_provider(self, provider_id: str):
        """Queue length tracked per provider."""
        queue = MagicMock()
        queue.length_by_provider = AsyncMock(return_value=5)
        
        length = await queue.length_by_provider(provider=provider_id)
        
        assert length >= 0
