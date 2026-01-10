"""
Base documentation generator.

Provides abstract base class for all documentation generators.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..config import DocumentationConfig
from ..models import DocumentationEntry, DocumentationIndex


class BaseGenerator(ABC):
    """Abstract base class for documentation generators."""

    def __init__(self, config: DocumentationConfig):
        """
        Initialize generator.

        Args:
            config: Documentation configuration
        """
        self.config = config
        self.index = DocumentationIndex(version=config.project_version)

    @abstractmethod
    def generate(self, source: Any) -> list[DocumentationEntry]:
        """
        Generate documentation from source.

        Args:
            source: Source to generate documentation from

        Returns:
            List of documentation entries
        """
        pass

    @abstractmethod
    def generate_from_file(self, file_path: Path) -> list[DocumentationEntry]:
        """
        Generate documentation from a file.

        Args:
            file_path: Path to the source file

        Returns:
            List of documentation entries
        """
        pass

    def generate_from_directory(
        self, directory: Path, recursive: bool = True
    ) -> list[DocumentationEntry]:
        """
        Generate documentation from all files in a directory.

        Args:
            directory: Path to the directory
            recursive: Whether to process subdirectories

        Returns:
            List of documentation entries
        """
        entries = []

        if not directory.exists():
            return entries

        pattern = "**/*" if recursive else "*"

        for include_pattern in self.config.include_patterns:
            for file_path in directory.glob(pattern):
                if not file_path.is_file():
                    continue

                # Check if file matches include pattern
                if not self._matches_pattern(file_path, include_pattern):
                    continue

                # Check if file matches exclude pattern
                if self._should_exclude(file_path):
                    continue

                try:
                    file_entries = self.generate_from_file(file_path)
                    entries.extend(file_entries)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        return entries

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches include pattern."""
        import fnmatch

        return fnmatch.fnmatch(str(file_path), pattern)

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded."""
        import fnmatch

        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
        return False

    def build_index(self, entries: list[DocumentationEntry]) -> DocumentationIndex:
        """
        Build documentation index from entries.

        Args:
            entries: List of documentation entries

        Returns:
            Documentation index
        """
        for entry in entries:
            self.index.add_entry(entry)
        return self.index

    def get_entry_id(self, name: str, parent: str | None = None) -> str:
        """
        Generate unique entry ID.

        Args:
            name: Entry name
            parent: Optional parent ID

        Returns:
            Unique entry ID
        """
        # Normalize name to valid ID
        entry_id = name.lower().replace(" ", "-").replace("_", "-")

        if parent:
            return f"{parent}.{entry_id}"
        return entry_id
