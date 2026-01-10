"""
Documentation configuration.

Provides configuration settings for documentation generation,
export, and template rendering.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class OutputFormat(Enum):
    """Documentation output formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class DocumentationType(Enum):
    """Types of documentation."""

    API = "api"
    GUIDE = "guide"
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    CHANGELOG = "changelog"


class CodeLanguage(Enum):
    """Supported code languages for examples."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    SHELL = "shell"
    JSON = "json"
    YAML = "yaml"


@dataclass
class TemplateConfig:
    """Template configuration."""

    template_dir: Path = field(default_factory=lambda: Path("templates"))
    default_template: str = "default"
    syntax_highlighting: bool = True
    include_toc: bool = True
    include_breadcrumbs: bool = True
    max_heading_depth: int = 4
    code_theme: str = "github-dark"
    custom_css: str | None = None
    custom_js: str | None = None


@dataclass
class ExportConfig:
    """Export configuration."""

    output_dir: Path = field(default_factory=lambda: Path("docs/generated"))
    format: OutputFormat = OutputFormat.MARKDOWN
    include_timestamp: bool = True
    include_version: bool = True
    create_index: bool = True
    minify_html: bool = False
    embed_images: bool = False
    base_url: str = ""
    asset_prefix: str = "assets/"


@dataclass
class ParserConfig:
    """Parser configuration."""

    extract_docstrings: bool = True
    extract_type_hints: bool = True
    extract_examples: bool = True
    extract_todos: bool = False
    include_private: bool = False
    include_dunder: bool = False
    follow_imports: bool = True
    max_depth: int = 5


@dataclass
class DocumentationConfig:
    """Main documentation configuration."""

    # Paths
    source_dirs: list[Path] = field(default_factory=list)
    output_dir: Path = field(default_factory=lambda: Path("docs"))
    template_dir: Path = field(default_factory=lambda: Path("templates"))

    # Generation settings
    doc_types: list[DocumentationType] = field(
        default_factory=lambda: [DocumentationType.API, DocumentationType.GUIDE]
    )
    output_formats: list[OutputFormat] = field(
        default_factory=lambda: [OutputFormat.MARKDOWN]
    )

    # Feature flags
    include_examples: bool = True
    include_cross_refs: bool = True
    include_source_links: bool = True
    generate_index: bool = True
    generate_search: bool = True

    # Metadata
    project_name: str = "Auto-Claude"
    project_version: str = "1.0.0"
    project_description: str = ""
    author: str = ""
    license: str = "MIT"

    # Sub-configs
    template: TemplateConfig = field(default_factory=TemplateConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    parser: ParserConfig = field(default_factory=ParserConfig)

    # Filters
    include_patterns: list[str] = field(default_factory=lambda: ["**/*.py"])
    exclude_patterns: list[str] = field(
        default_factory=lambda: ["**/__pycache__/**", "**/test_*.py"]
    )

    def __post_init__(self):
        """Validate and normalize configuration."""
        # Ensure paths are Path objects
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.template_dir, str):
            self.template_dir = Path(self.template_dir)

        # Normalize source dirs
        self.source_dirs = [
            Path(d) if isinstance(d, str) else d for d in self.source_dirs
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_dirs": [str(d) for d in self.source_dirs],
            "output_dir": str(self.output_dir),
            "template_dir": str(self.template_dir),
            "doc_types": [t.value for t in self.doc_types],
            "output_formats": [f.value for f in self.output_formats],
            "include_examples": self.include_examples,
            "include_cross_refs": self.include_cross_refs,
            "include_source_links": self.include_source_links,
            "generate_index": self.generate_index,
            "generate_search": self.generate_search,
            "project_name": self.project_name,
            "project_version": self.project_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentationConfig":
        """Create from dictionary."""
        # Convert string values back to enums
        if "doc_types" in data:
            data["doc_types"] = [DocumentationType(t) for t in data["doc_types"]]
        if "output_formats" in data:
            data["output_formats"] = [OutputFormat(f) for f in data["output_formats"]]
        return cls(**data)


def get_default_config() -> DocumentationConfig:
    """Get default documentation configuration."""
    return DocumentationConfig(
        source_dirs=[
            Path("apps/backend"),
            Path("apps/frontend/src"),
        ],
        output_dir=Path("docs/generated"),
        doc_types=[
            DocumentationType.API,
            DocumentationType.GUIDE,
            DocumentationType.REFERENCE,
        ],
        output_formats=[
            OutputFormat.MARKDOWN,
            OutputFormat.HTML,
        ],
        project_name="Auto-Claude APEX",
        project_description="AI-powered development automation platform",
    )
