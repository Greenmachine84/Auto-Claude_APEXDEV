"""
Markdown exporter.

Exports documentation entries to Markdown files.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import ExportConfig
from ..models import DocumentationEntry, DocumentationIndex
from ..templates.markdown_template import MarkdownTemplate
from ..templates.base import TemplateContext, TemplateConfig


class MarkdownExporter:
    """Exports documentation to Markdown format."""

    def __init__(self, config: ExportConfig):
        """
        Initialize exporter.

        Args:
            config: Export configuration
        """
        self.config = config
        self.template = MarkdownTemplate(TemplateConfig())
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def export_entry(
        self,
        entry: DocumentationEntry,
        filename: Optional[str] = None
    ) -> Path:
        """
        Export a single documentation entry.

        Args:
            entry: Documentation entry to export
            filename: Optional filename (default: entry.id.md)

        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"{entry.id}.md"

        output_path = self.config.output_dir / filename

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build context
        context = TemplateContext(
            entry=entry,
            base_url=self.config.base_url,
        )

        if self.config.include_version:
            context.metadata["version"] = entry.metadata.get("version", "1.0.0")

        if self.config.include_timestamp:
            context.metadata["generated"] = datetime.now().isoformat()

        # Render and write
        content = self.template.render(context)
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def export_entries(
        self,
        entries: list[DocumentationEntry],
        subdir: str = ""
    ) -> list[Path]:
        """
        Export multiple documentation entries.

        Args:
            entries: List of entries to export
            subdir: Optional subdirectory

        Returns:
            List of exported file paths
        """
        paths = []
        output_dir = self.config.output_dir

        if subdir:
            output_dir = output_dir / subdir
            output_dir.mkdir(parents=True, exist_ok=True)

        for entry in entries:
            filename = f"{entry.id}.md"
            path = output_dir / filename

            context = TemplateContext(entry=entry, base_url=self.config.base_url)
            content = self.template.render(context)
            path.write_text(content, encoding="utf-8")

            paths.append(path)

        return paths

    def export_index(
        self,
        index: DocumentationIndex,
        filename: str = "index.md"
    ) -> Path:
        """
        Export documentation index.

        Args:
            index: Documentation index
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.config.output_dir / filename

        content = self.template.render_index(index)

        # Add header
        header = f"""---
title: Documentation Index
generated: {datetime.now().isoformat()}
version: {index.version}
---

"""
        output_path.write_text(header + content, encoding="utf-8")

        return output_path

    def export_full(
        self,
        index: DocumentationIndex,
        project_name: str = "",
        project_version: str = ""
    ) -> list[Path]:
        """
        Export full documentation including all entries and index.

        Args:
            index: Documentation index
            project_name: Project name
            project_version: Project version

        Returns:
            List of all exported file paths
        """
        paths = []

        # Export all entries
        for entry_id, entry in index.entries.items():
            # Organize by entry type
            subdir = entry.entry_type
            if subdir:
                (self.config.output_dir / subdir).mkdir(parents=True, exist_ok=True)
                filename = f"{subdir}/{entry.id}.md"
            else:
                filename = f"{entry.id}.md"

            path = self.export_entry(entry, filename)
            paths.append(path)

        # Export index
        if self.config.create_index:
            index_path = self.export_index(index)
            paths.append(index_path)

            # Create category indexes
            for category, entry_ids in index.categories.items():
                category_index = self._create_category_index(
                    category,
                    [index.entries[eid] for eid in entry_ids if eid in index.entries]
                )
                category_path = self.config.output_dir / category / "index.md"
                category_path.parent.mkdir(parents=True, exist_ok=True)
                category_path.write_text(category_index, encoding="utf-8")
                paths.append(category_path)

        return paths

    def _create_category_index(
        self,
        category: str,
        entries: list[DocumentationEntry]
    ) -> str:
        """Create index page for a category."""
        lines = [
            f"# {category.title()}",
            "",
            f"Documentation for {category} components.",
            "",
            "## Contents",
            "",
        ]

        for entry in entries:
            lines.append(f"- [{entry.title}]({entry.id}.md)")

        return "\n".join(lines)

    def export_sidebar(
        self,
        index: DocumentationIndex,
        filename: str = "_sidebar.md"
    ) -> Path:
        """
        Export sidebar navigation.

        Args:
            index: Documentation index
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.config.output_dir / filename

        lines = ["<!-- Documentation Sidebar -->", ""]

        for category, entry_ids in index.categories.items():
            lines.append(f"- **{category.title()}**")

            for entry_id in entry_ids:
                entry = index.entries.get(entry_id)
                if entry:
                    lines.append(f"  - [{entry.title}]({category}/{entry.id}.md)")

            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")

        return output_path

    def export_readme(
        self,
        index: DocumentationIndex,
        project_name: str,
        project_description: str = ""
    ) -> Path:
        """
        Export README file.

        Args:
            index: Documentation index
            project_name: Project name
            project_description: Project description

        Returns:
            Path to exported file
        """
        output_path = self.config.output_dir / "README.md"

        lines = [
            f"# {project_name} Documentation",
            "",
        ]

        if project_description:
            lines.append(project_description)
            lines.append("")

        lines.extend([
            "## Quick Links",
            "",
            "- [Getting Started](guides/getting-started.md)",
            "- [API Reference](api/index.md)",
            "- [Configuration](reference/configuration.md)",
            "",
            "## Categories",
            "",
        ])

        for category, entry_ids in index.categories.items():
            count = len(entry_ids)
            lines.append(f"- [{category.title()}]({category}/index.md) ({count} pages)")

        lines.extend([
            "",
            "---",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        ])

        output_path.write_text("\n".join(lines), encoding="utf-8")

        return output_path
