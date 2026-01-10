"""Prompt registry for template management.

Part of Phase 2: LLM Architecture
"""

import json
import logging
import threading
from pathlib import Path
from typing import Optional

from .prompt_template import PromptTemplate, TemplateVariable, VariableType

logger = logging.getLogger(__name__)


class PromptRegistry:
    """Central registry for prompt templates."""

    _instance: Optional["PromptRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "PromptRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._templates: dict[str, PromptTemplate] = {}
                    cls._instance._categories: dict[str, list[str]] = {}
        return cls._instance

    def register(self, template: PromptTemplate) -> str:
        """Register a prompt template."""
        self._templates[template.id] = template

        if template.category not in self._categories:
            self._categories[template.category] = []
        if template.id not in self._categories[template.category]:
            self._categories[template.category].append(template.id)

        logger.info("Registered prompt template: %s", template.id)
        return template.id

    def get(self, template_id: str) -> PromptTemplate | None:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def render(self, template_id: str, **kwargs) -> str:
        """Render a template by ID."""
        template = self.get(template_id)
        if not template:
            raise KeyError(f"Template not found: {template_id}")
        return template.render(**kwargs)

    def list_by_category(self, category: str) -> list[PromptTemplate]:
        """List templates in a category."""
        template_ids = self._categories.get(category, [])
        return [self._templates[tid] for tid in template_ids if tid in self._templates]

    def list_categories(self) -> list[str]:
        """List all categories."""
        return list(self._categories.keys())

    def load_from_file(self, file_path: str) -> int:
        """Load templates from a JSON file."""
        path = Path(file_path)
        if not path.exists():
            logger.warning("Template file not found: %s", file_path)
            return 0

        with open(path) as f:
            data = json.load(f)

        count = 0
        for item in data.get("templates", []):
            variables = [
                TemplateVariable(
                    name=v["name"],
                    var_type=VariableType(v.get("type", "string")),
                    required=v.get("required", True),
                    default=v.get("default"),
                )
                for v in item.get("variables", [])
            ]

            template = PromptTemplate(
                id=item["id"],
                name=item["name"],
                template=item["template"],
                variables=variables,
                description=item.get("description", ""),
                category=item.get("category", "general"),
            )
            self.register(template)
            count += 1

        logger.info("Loaded %d templates from %s", count, file_path)
        return count

    def save_to_file(self, file_path: str) -> int:
        """Save templates to a JSON file."""
        data = {"templates": [t.to_dict() for t in self._templates.values()]}

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return len(self._templates)

    def clear(self) -> int:
        """Clear all templates."""
        count = len(self._templates)
        self._templates.clear()
        self._categories.clear()
        return count
