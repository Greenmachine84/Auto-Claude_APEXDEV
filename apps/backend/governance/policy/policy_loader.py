"""
Policy Loader - Phase 9 Implementation.

Load and reload policies from files and databases.

World-Class Standards:
- Hot-reload without downtime
- Multiple source support
- Validation on load
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import yaml

from ..models import Policy
from .rules import RuleParser, RuleValidator

logger = logging.getLogger(__name__)


class PolicyLoader:
    """
    Loads policies from various sources.

    Supports JSON files, YAML files, and database storage
    with hot-reload capability.
    """

    def __init__(self) -> None:
        self._parser = RuleParser()
        self._validator = RuleValidator()
        self._loaded_policies: dict[str, Policy] = {}
        self._file_mtimes: dict[str, float] = {}
        self._watch_enabled: bool = False
        self._watch_interval: int = 30  # seconds

    def load_from_file(self, file_path: str) -> Policy | None:
        """
        Load a policy from a file.

        Supports .json and .yaml/.yml extensions.
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"Policy file not found: {file_path}")
            return None

        try:
            content = path.read_text()

            if path.suffix == ".json":
                policy = self._parser.parse_json(content)
            elif path.suffix in (".yaml", ".yml"):
                policy = self._parser.parse_yaml(content)
            else:
                logger.error(f"Unsupported file format: {path.suffix}")
                return None

            # Validate
            errors = self._validator.validate_policy(policy)
            if errors:
                for error in errors:
                    logger.warning(f"Policy validation: {error}")

            # Track file for hot-reload
            self._file_mtimes[file_path] = path.stat().st_mtime
            self._loaded_policies[policy.id] = policy

            logger.info(f"Loaded policy: {policy.id} from {file_path}")
            return policy

        except Exception as e:
            logger.error(f"Failed to load policy from {file_path}: {e}")
            return None

    def load_from_directory(self, dir_path: str) -> list[Policy]:
        """Load all policies from a directory."""
        path = Path(dir_path)
        policies = []

        if not path.exists() or not path.is_dir():
            logger.error(f"Policy directory not found: {dir_path}")
            return policies

        for file_path in path.glob("*.json"):
            policy = self.load_from_file(str(file_path))
            if policy:
                policies.append(policy)

        for file_path in path.glob("*.yaml"):
            policy = self.load_from_file(str(file_path))
            if policy:
                policies.append(policy)

        for file_path in path.glob("*.yml"):
            policy = self.load_from_file(str(file_path))
            if policy:
                policies.append(policy)

        logger.info(f"Loaded {len(policies)} policies from {dir_path}")
        return policies

    def load_from_dict(self, data: dict[str, Any]) -> Policy | None:
        """Load a policy from a dictionary."""
        try:
            policy = self._parser.parse_policy(data)

            errors = self._validator.validate_policy(policy)
            if errors:
                for error in errors:
                    logger.warning(f"Policy validation: {error}")

            self._loaded_policies[policy.id] = policy
            return policy

        except Exception as e:
            logger.error(f"Failed to load policy from dict: {e}")
            return None

    def load_from_database(
        self, connection: Any, table: str = "policies"
    ) -> list[Policy]:
        """
        Load policies from database.

        Override this method for custom database implementations.
        """
        # Placeholder for database loading
        logger.info("Database policy loading not implemented")
        return []

    def check_for_updates(self) -> list[str]:
        """
        Check for file updates (for hot-reload).

        Returns list of policy IDs that were updated.
        """
        updated = []

        for file_path, mtime in list(self._file_mtimes.items()):
            path = Path(file_path)
            if not path.exists():
                continue

            current_mtime = path.stat().st_mtime
            if current_mtime > mtime:
                policy = self.load_from_file(file_path)
                if policy:
                    updated.append(policy.id)
                    logger.info(f"Hot-reloaded policy: {policy.id}")

        return updated

    async def start_watching(self, interval: int = 30) -> None:
        """Start watching for policy file changes."""
        self._watch_enabled = True
        self._watch_interval = interval

        while self._watch_enabled:
            await asyncio.sleep(self._watch_interval)
            updated = self.check_for_updates()
            if updated:
                logger.info(f"Hot-reload: {len(updated)} policies updated")

    def stop_watching(self) -> None:
        """Stop watching for policy file changes."""
        self._watch_enabled = False

    def get_policy(self, policy_id: str) -> Policy | None:
        """Get a loaded policy by ID."""
        return self._loaded_policies.get(policy_id)

    def list_policies(self) -> list[Policy]:
        """List all loaded policies."""
        return list(self._loaded_policies.values())

    def unload_policy(self, policy_id: str) -> bool:
        """Unload a policy."""
        if policy_id in self._loaded_policies:
            del self._loaded_policies[policy_id]
            logger.info(f"Unloaded policy: {policy_id}")
            return True
        return False

    def reload_all(self) -> int:
        """Reload all policies from their sources."""
        count = 0
        for file_path in list(self._file_mtimes.keys()):
            if self.load_from_file(file_path):
                count += 1
        logger.info(f"Reloaded {count} policies")
        return count

    def export_policy(self, policy_id: str, format: str = "json") -> str | None:
        """Export a policy to string format."""
        policy = self._loaded_policies.get(policy_id)
        if not policy:
            return None

        data = {
            "id": policy.id,
            "name": policy.name,
            "description": policy.description,
            "default_action": policy.default_action.value,
            "enabled": policy.enabled,
            "applies_to": policy.applies_to,
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "field": r.field,
                    "operator": r.operator.value,
                    "value": r.value,
                    "action": r.action.value,
                    "priority": r.priority,
                    "enabled": r.enabled,
                    "provider": r.provider,
                }
                for r in policy.rules
            ],
        }

        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "yaml":
            return yaml.dump(data, default_flow_style=False)
        else:
            return None
