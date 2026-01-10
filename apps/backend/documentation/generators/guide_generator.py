"""
Guide documentation generator.

Generates user guides and tutorials from templates
and structured content.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..config import DocumentationConfig
from ..models import (
    CodeExample,
    CrossReference,
    DocumentationEntry,
)
from .base import BaseGenerator


@dataclass
class GuideSection:
    """A section in a guide."""

    title: str
    content: str
    level: int = 2
    examples: list[CodeExample] = field(default_factory=list)
    subsections: list["GuideSection"] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = []
        heading = "#" * self.level
        lines.append(f"{heading} {self.title}")
        lines.append("")
        lines.append(self.content)
        lines.append("")

        for example in self.examples:
            lines.append(example.to_markdown())
            lines.append("")

        for subsection in self.subsections:
            lines.append(subsection.to_markdown())

        return "\n".join(lines)


@dataclass
class GuideTemplate:
    """Template for generating guides."""

    id: str
    title: str
    description: str
    sections: list[GuideSection] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    estimated_time: str | None = None


class GuideGenerator(BaseGenerator):
    """Generates user guides and tutorials."""

    def __init__(self, config: DocumentationConfig):
        """Initialize guide generator."""
        super().__init__(config)
        self.templates: dict[str, GuideTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default guide templates."""
        self.templates["getting-started"] = GuideTemplate(
            id="getting-started",
            title="Getting Started",
            description="Quick start guide for new users",
            sections=[
                GuideSection(
                    title="Prerequisites",
                    content="Before you begin, ensure you have:",
                    level=2,
                ),
                GuideSection(
                    title="Installation",
                    content="Install the package using pip:",
                    level=2,
                    examples=[
                        CodeExample(
                            id="install-pip",
                            title="Install via pip",
                            code="pip install auto-claude",
                            language="shell",
                        )
                    ],
                ),
                GuideSection(
                    title="Quick Start",
                    content="Create your first agent:",
                    level=2,
                ),
            ],
            tags=["beginner", "setup"],
            estimated_time="15 minutes",
        )

        self.templates["agent-development"] = GuideTemplate(
            id="agent-development",
            title="Agent Development Guide",
            description="Learn how to develop custom agents",
            sections=[
                GuideSection(
                    title="Understanding Agents",
                    content="Agents are autonomous components that perform tasks.",
                    level=2,
                ),
                GuideSection(
                    title="Creating Your First Agent",
                    content="Follow these steps to create a basic agent:",
                    level=2,
                ),
                GuideSection(
                    title="Agent Configuration",
                    content="Configure your agent behavior:",
                    level=2,
                ),
            ],
            prerequisites=["getting-started"],
            tags=["intermediate", "development"],
            estimated_time="30 minutes",
        )

    def generate(self, source: Any) -> list[DocumentationEntry]:
        """
        Generate guide documentation.

        Args:
            source: Guide template or structured content

        Returns:
            List of documentation entries
        """
        if isinstance(source, GuideTemplate):
            return [self._generate_from_template(source)]
        elif isinstance(source, dict):
            template = self._dict_to_template(source)
            return [self._generate_from_template(template)]
        return []

    def generate_from_file(self, file_path: Path) -> list[DocumentationEntry]:
        """
        Generate guide documentation from a file.

        Args:
            file_path: Path to guide source file (Markdown or YAML)

        Returns:
            List of documentation entries
        """
        entries = []

        if file_path.suffix == ".md":
            entries.append(self._parse_markdown_guide(file_path))
        elif file_path.suffix in (".yaml", ".yml"):
            entries.extend(self._parse_yaml_guide(file_path))

        return entries

    def _generate_from_template(self, template: GuideTemplate) -> DocumentationEntry:
        """Generate documentation entry from template."""
        lines = []

        # Header
        lines.append(f"# {template.title}")
        lines.append("")
        lines.append(template.description)
        lines.append("")

        # Metadata
        if template.estimated_time:
            lines.append(f"⏱️ **Estimated Time:** {template.estimated_time}")
            lines.append("")

        if template.prerequisites:
            lines.append("**Prerequisites:**")
            for prereq in template.prerequisites:
                lines.append(f"- [{prereq}](#{prereq})")
            lines.append("")

        # Sections
        for section in template.sections:
            lines.append(section.to_markdown())

        content = "\n".join(lines)

        # Create cross-references for prerequisites
        cross_refs = [
            CrossReference(
                target_id=prereq,
                target_title=prereq.replace("-", " ").title(),
                reference_type="prerequisite",
            )
            for prereq in template.prerequisites
        ]

        return DocumentationEntry(
            id=template.id,
            title=template.title,
            content=content,
            entry_type="guide",
            tags=template.tags,
            cross_refs=cross_refs,
        )

    def _parse_markdown_guide(self, file_path: Path) -> DocumentationEntry:
        """Parse a Markdown guide file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Extract title from first heading
        title = file_path.stem.replace("-", " ").title()
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        return DocumentationEntry(
            id=self.get_entry_id(file_path.stem),
            title=title,
            content=content,
            entry_type="guide",
            source_file=file_path,
            tags=["guide"],
        )

    def _parse_yaml_guide(self, file_path: Path) -> list[DocumentationEntry]:
        """Parse a YAML guide definition file."""
        import yaml

        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        entries = []

        if isinstance(data, list):
            for item in data:
                template = self._dict_to_template(item)
                entries.append(self._generate_from_template(template))
        elif isinstance(data, dict):
            template = self._dict_to_template(data)
            entries.append(self._generate_from_template(template))

        return entries

    def _dict_to_template(self, data: dict) -> GuideTemplate:
        """Convert dictionary to GuideTemplate."""
        sections = []
        for section_data in data.get("sections", []):
            sections.append(self._dict_to_section(section_data))

        return GuideTemplate(
            id=data.get("id", "unknown"),
            title=data.get("title", "Untitled"),
            description=data.get("description", ""),
            sections=sections,
            prerequisites=data.get("prerequisites", []),
            tags=data.get("tags", []),
            estimated_time=data.get("estimated_time"),
        )

    def _dict_to_section(self, data: dict) -> GuideSection:
        """Convert dictionary to GuideSection."""
        examples = []
        for ex_data in data.get("examples", []):
            examples.append(
                CodeExample(
                    id=ex_data.get("id", "example"),
                    title=ex_data.get("title", ""),
                    code=ex_data.get("code", ""),
                    language=ex_data.get("language", "python"),
                )
            )

        subsections = [
            self._dict_to_section(sub) for sub in data.get("subsections", [])
        ]

        return GuideSection(
            title=data.get("title", ""),
            content=data.get("content", ""),
            level=data.get("level", 2),
            examples=examples,
            subsections=subsections,
        )

    def register_template(self, template: GuideTemplate) -> None:
        """Register a new guide template."""
        self.templates[template.id] = template

    def get_template(self, template_id: str) -> GuideTemplate | None:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def list_templates(self) -> list[str]:
        """List all available template IDs."""
        return list(self.templates.keys())

    def generate_from_template_id(
        self, template_id: str
    ) -> DocumentationEntry | None:
        """Generate documentation from a template ID."""
        template = self.get_template(template_id)
        if template:
            return self._generate_from_template(template)
        return None
