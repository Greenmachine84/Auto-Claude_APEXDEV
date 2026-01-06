"""Queue persistence.

Persists queue state for recovery.

Capabilities:
- Save/load tasks
- Checkpoint creation
- Recovery from failure
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from orchestrator.queue.task_model import Task


logger = logging.getLogger(__name__)


@dataclass
class QueuePersistence:
    """Persist queue to disk.
    
    Example:
        persistence = QueuePersistence("/path/to/queue")
        await persistence.save_task(task)
        tasks = await persistence.load_all()
    """
    
    storage_path: str
    
    def __post_init__(self) -> None:
        """Initialize storage."""
        os.makedirs(self.storage_path, exist_ok=True)
        self._tasks_dir = os.path.join(self.storage_path, "tasks")
        self._checkpoints_dir = os.path.join(self.storage_path, "checkpoints")
        os.makedirs(self._tasks_dir, exist_ok=True)
        os.makedirs(self._checkpoints_dir, exist_ok=True)
    
    async def save_task(self, task: Task) -> None:
        """Save task to storage."""
        path = os.path.join(self._tasks_dir, f"{task.id}.json")
        
        try:
            with open(path, "w") as f:
                json.dump(task.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task {task.id}: {e}")
    
    async def load_task(self, task_id: str) -> Optional[Task]:
        """Load task from storage."""
        path = os.path.join(self._tasks_dir, f"{task_id}.json")
        
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                return Task.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load task {task_id}: {e}")
        
        return None
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete task from storage."""
        path = os.path.join(self._tasks_dir, f"{task_id}.json")
        
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
        
        return False
    
    async def load_all(self) -> List[Task]:
        """Load all tasks."""
        tasks = []
        
        try:
            for filename in os.listdir(self._tasks_dir):
                if filename.endswith(".json"):
                    task_id = filename[:-5]
                    task = await self.load_task(task_id)
                    if task:
                        tasks.append(task)
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
        
        return tasks
    
    async def create_checkpoint(self, tasks: List[Task]) -> str:
        """Create a checkpoint."""
        checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self._checkpoints_dir, f"{checkpoint_id}.json")
        
        try:
            data = {
                "id": checkpoint_id,
                "created_at": datetime.now().isoformat(),
                "tasks": [t.to_dict() for t in tasks],
            }
            
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Checkpoint {checkpoint_id} created")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            raise
    
    async def restore_checkpoint(self, checkpoint_id: str) -> List[Task]:
        """Restore from checkpoint."""
        path = os.path.join(self._checkpoints_dir, f"{checkpoint_id}.json")
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
            logger.info(f"Restored {len(tasks)} tasks from checkpoint {checkpoint_id}")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            raise
    
    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints."""
        checkpoints = []
        
        try:
            for filename in os.listdir(self._checkpoints_dir):
                if filename.endswith(".json"):
                    path = os.path.join(self._checkpoints_dir, filename)
                    with open(path, "r") as f:
                        data = json.load(f)
                    checkpoints.append({
                        "id": data.get("id"),
                        "created_at": data.get("created_at"),
                        "task_count": len(data.get("tasks", [])),
                    })
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
        
        return sorted(checkpoints, key=lambda x: x["created_at"], reverse=True)
