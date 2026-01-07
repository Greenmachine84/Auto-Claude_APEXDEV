"""
Documentation service.

Provides high-level API for generating, managing,
and exporting documentation.
"""

from pathlib import Path
from typing import Any, Optional

from .config import (
    DocumentationConfig,
    DocumentationType,
    ExportConfig,
    OutputFormat,
    get_default_config,
)
from .models import (
    DocumentationEntry,
    DocumentationIndex,
)
from .generators import (
    ApiDocGenerator,
    GuideGenerator,
    ReferenceGenerator,
)
from .exporters import (
    MarkdownExporter,
    HtmlExporter,
)


class DocumentationService:
    """High-level documentation generation service."""

    def __init__(self, config: Optional[DocumentationConfig] = None):
        """
        Initialize documentation service.

        Args:
            config: Documentation configuration (uses default if not provided)
        """
        self.config = config or get_default_config()
        self.index = DocumentationIndex(version=self.config.project_version)

        # Initialize generators
        self._generators = {
            DocumentationType.API: ApiDocGenerator(self.config),
            DocumentationType.GUIDE: GuideGenerator(self.config),
            DocumentationType.REFERENCE: ReferenceGenerator(self.config),
        }

        # Initialize exporters
        self._exporters = {
            OutputFormat.MARKDOWN: MarkdownExporter(ExportConfig(
                output_dir=self.config.output_dir / "md",
            )),
            OutputFormat.HTML: HtmlExporter(ExportConfig(
                output_dir=self.config.output_dir / "html",
            )),
        }

    def generate_all(self) -> DocumentationIndex:
        """
        Generate all documentation from configured sources.

        Returns:
            Documentation index with all entries
        """
        # Generate API docs
        if DocumentationType.API in self.config.doc_types:
            for source_dir in self.config.source_dirs:
                entries = self._generators[DocumentationType.API].generate_from_directory(
                    source_dir
                )
                for entry in entries:
                    self.index.add_entry(entry)

        # Generate guides
        if DocumentationType.GUIDE in self.config.doc_types:
            guide_generator = self._generators[DocumentationType.GUIDE]
            for template_id in guide_generator.list_templates():
                entry = guide_generator.generate_from_template_id(template_id)
                if entry:
                    self.index.add_entry(entry)

        return self.index

    def generate_api_docs(self, source_dir: Path) -> list[DocumentationEntry]:
        """
        Generate API documentation from a directory.

        Args:
            source_dir: Source directory path

        Returns:
            List of documentation entries
        """
        generator = self._generators[DocumentationType.API]
        entries = generator.generate_from_directory(source_dir)

        for entry in entries:
            self.index.add_entry(entry)

        return entries

    def generate_from_module(self, module: Any) -> list[DocumentationEntry]:
        """
        Generate documentation from a Python module.

        Args:
            module: Python module

        Returns:
            List of documentation entries
        """
        generator = self._generators[DocumentationType.API]
        entries = generator.generate(module)

        for entry in entries:
            self.index.add_entry(entry)

        return entries

    def add_guide(
        self,
        title: str,
        content: str,
        tags: Optional[list[str]] = None
    ) -> DocumentationEntry:
        """
        Add a guide to the documentation.

        Args:
            title: Guide title
            content: Guide content (Markdown)
            tags: Optional tags

        Returns:
            Created documentation entry
        """
        entry_id = title.lower().replace(" ", "-")

        entry = DocumentationEntry(
            id=entry_id,
            title=title,
            content=content,
            entry_type="guide",
            tags=tags or ["guide"],
        )

        self.index.add_entry(entry)
        return entry

    def add_entry(self, entry: DocumentationEntry) -> None:
        """
        Add an entry to the documentation index.

        Args:
            entry: Documentation entry
        """
        self.index.add_entry(entry)

    def get_entry(self, entry_id: str) -> Optional[DocumentationEntry]:
        """
        Get an entry by ID.

        Args:
            entry_id: Entry ID

        Returns:
            Documentation entry if found
        """
        return self.index.entries.get(entry_id)

    def search(self, query: str) -> list[DocumentationEntry]:
        """
        Search documentation.

        Args:
            query: Search query

        Returns:
            Matching entries
        """
        return self.index.search(query)

    def export(
        self,
        output_format: Optional[OutputFormat] = None,
        output_dir: Optional[Path] = None
    ) -> list[Path]:
        """
        Export documentation to specified format.

        Args:
            output_format: Output format (uses config default if not specified)
            output_dir: Output directory (uses config default if not specified)

        Returns:
            List of exported file paths
        """
        formats = [output_format] if output_format else self.config.output_formats
        all_paths = []

        for fmt in formats:
            exporter = self._exporters.get(fmt)
            if exporter:
                if output_dir:
                    exporter.config.output_dir = output_dir / fmt.value

                paths = exporter.export_full(
                    self.index,
                    project_name=self.config.project_name,
                    project_version=self.config.project_version,
                )
                all_paths.extend(paths)

        return all_paths

    def export_markdown(self, output_dir: Optional[Path] = None) -> list[Path]:
        """
        Export documentation to Markdown.

        Args:
            output_dir: Output directory

        Returns:
            List of exported file paths
        """
        return self.export(OutputFormat.MARKDOWN, output_dir)

    def export_html(self, output_dir: Optional[Path] = None) -> list[Path]:
        """
        Export documentation to HTML.

        Args:
            output_dir: Output directory

        Returns:
            List of exported file paths
        """
        return self.export(OutputFormat.HTML, output_dir)

    def clear(self) -> None:
        """Clear all documentation entries."""
        self.index = DocumentationIndex(version=self.config.project_version)

    def get_stats(self) -> dict:
        """
        Get documentation statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_entries": len(self.index.entries),
            "categories": {
                cat: len(ids)
                for cat, ids in self.index.categories.items()
            },
            "tags": {
                tag: len(ids)
                for tag, ids in self.index.tags.items()
            },
            "version": self.index.version,
            "generated_at": self.index.generated_at.isoformat(),
        }


def create_documentation_service(
    source_dirs: Optional[list[Path]] = None,
    output_dir: Optional[Path] = None,
    project_name: str = "Documentation",
    project_version: str = "1.0.0"
) -> DocumentationService:
    """
    Create a documentation service with custom configuration.

    Args:
        source_dirs: Source directories to document
        output_dir: Output directory for generated docs
        project_name: Project name
        project_version: Project version

    Returns:
        Configured DocumentationService
    """
    config = DocumentationConfig(
        source_dirs=source_dirs or [],
        output_dir=output_dir or Path("docs/generated"),
        project_name=project_name,
        project_version=project_version,
        doc_types=[
            DocumentationType.API,
            DocumentationType.GUIDE,
            DocumentationType.REFERENCE,
        ],
        output_formats=[
            OutputFormat.MARKDOWN,
            OutputFormat.HTML,
        ],
    )

    return DocumentationService(config)
