"""
Base template class.

Provides abstract base class for documentation templates.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import TemplateConfig
from ..models import DocumentationEntry, DocumentationIndex


@dataclass
class TemplateContext:
    """Context data for template rendering."""

    entry: DocumentationEntry | None = None
    index: DocumentationIndex | None = None
    config: TemplateConfig | None = None
    project_name: str = ""
    project_version: str = ""
    base_url: str = ""
    breadcrumbs: list[tuple[str, str]] = field(default_factory=list)
    navigation: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTemplate(ABC):
    """Abstract base class for documentation templates."""

    def __init__(self, config: TemplateConfig):
        """
        Initialize template.

        Args:
            config: Template configuration
        """
        self.config = config

    @abstractmethod
    def render(self, context: TemplateContext) -> str:
        """
        Render template with context.

        Args:
            context: Template context

        Returns:
            Rendered output
        """
        pass

    @abstractmethod
    def render_entry(self, entry: DocumentationEntry) -> str:
        """
        Render a documentation entry.

        Args:
            entry: Documentation entry

        Returns:
            Rendered output
        """
        pass

    @abstractmethod
    def render_index(self, index: DocumentationIndex) -> str:
        """
        Render documentation index.

        Args:
            index: Documentation index

        Returns:
            Rendered output
        """
        pass

    def render_toc(self, entries: list[DocumentationEntry]) -> str:
        """
        Render table of contents.

        Args:
            entries: List of documentation entries

        Returns:
            Rendered table of contents
        """
        lines = []
        for entry in entries:
            indent = "  " * (entry.metadata.get("level", 0))
            lines.append(f"{indent}- [{entry.title}](#{entry.id})")
        return "\n".join(lines)

    def render_breadcrumbs(self, breadcrumbs: list[tuple[str, str]]) -> str:
        """
        Render breadcrumb navigation.

        Args:
            breadcrumbs: List of (title, url) tuples

        Returns:
            Rendered breadcrumbs
        """
        parts = [f"[{title}]({url})" for title, url in breadcrumbs]
        return " > ".join(parts)

    def format_code(self, code: str, language: str = "") -> str:
        """
        Format code block.

        Args:
            code: Code content
            language: Programming language

        Returns:
            Formatted code block
        """
        return f"```{language}\n{code}\n```"

    def escape(self, text: str) -> str:
        """
        Escape special characters.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        return text

    def get_template_path(self, template_name: str) -> Path:
        """
        Get path to a template file.

        Args:
            template_name: Name of the template

        Returns:
            Path to template file
        """
        return self.config.template_dir / template_name

    def load_template(self, template_name: str) -> str:
        """
        Load template content from file.

        Args:
            template_name: Name of the template

        Returns:
            Template content
        """
        path = self.get_template_path(template_name)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""
