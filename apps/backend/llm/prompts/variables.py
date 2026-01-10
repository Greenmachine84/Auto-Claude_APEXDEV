"""Variable resolution and context management.

Part of Phase 2: LLM Architecture
"""

import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class VariableContext:
    """Context for variable resolution."""

    values: dict[str, Any] = field(default_factory=dict)
    parent: Optional["VariableContext"] = None

    def get(self, name: str, default: Any = None) -> Any:
        """Get a variable, checking parent contexts."""
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name, default)
        return default

    def set(self, name: str, value: Any) -> None:
        """Set a variable in this context."""
        self.values[name] = value

    def child(self) -> "VariableContext":
        """Create a child context."""
        return VariableContext(parent=self)

    def to_dict(self) -> dict[str, Any]:
        """Flatten to dictionary."""
        result = {}
        if self.parent:
            result.update(self.parent.to_dict())
        result.update(self.values)
        return result


class VariableResolver:
    """Resolves variables from multiple sources."""

    def __init__(self):
        self._sources: list[Callable[[str], Any | None]] = []
        self._cache: dict[str, Any] = {}
        self._computed: dict[str, Callable[[], Any]] = {}
        self._setup_default_sources()

    def _setup_default_sources(self) -> None:
        # Environment variables
        self._sources.append(lambda name: os.environ.get(name))

        # Built-in computed values
        self._computed["now"] = lambda: datetime.utcnow().isoformat()
        self._computed["date"] = lambda: datetime.utcnow().strftime("%Y-%m-%d")
        self._computed["time"] = lambda: datetime.utcnow().strftime("%H:%M:%S")

    def add_source(self, source: Callable[[str], Any | None]) -> None:
        """Add a variable source function."""
        self._sources.append(source)

    def add_computed(self, name: str, fn: Callable[[], Any]) -> None:
        """Add a computed variable."""
        self._computed[name] = fn

    def set(self, name: str, value: Any) -> None:
        """Set a cached variable."""
        self._cache[name] = value

    def resolve(self, name: str, default: Any = None) -> Any:
        """Resolve a variable from all sources."""
        # Check cache first
        if name in self._cache:
            return self._cache[name]

        # Check computed values
        if name in self._computed:
            return self._computed[name]()

        # Check sources in order
        for source in self._sources:
            value = source(name)
            if value is not None:
                return value

        return default

    def resolve_all(self, names: list[str]) -> dict[str, Any]:
        """Resolve multiple variables."""
        return {name: self.resolve(name) for name in names}

    def resolve_template(self, template: str) -> str:
        """Resolve all {{variable}} patterns in a string."""
        import re

        pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")

        def replace(match):
            name = match.group(1)
            value = self.resolve(name, f"{{{{{name}}}}}")
            return str(value)

        return pattern.sub(replace, template)

    def clear_cache(self) -> None:
        """Clear cached values."""
        self._cache.clear()
