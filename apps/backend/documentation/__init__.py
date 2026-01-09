"""
Documentation Module.

This module provides comprehensive documentation generation,
management, and export capabilities for the Auto-Claude system.

Features:
- API documentation generation from code
- Markdown and HTML export
- Interactive documentation viewer
- Code example extraction
- Cross-reference linking
- Version-aware documentation

Components:
- Config: Documentation configuration and settings
- Models: Data models for documentation entities
- Generators: Documentation generators (API, guides, reference)
- Templates: Documentation templates (Markdown, HTML)
- Parsers: Source code and docstring parsers
- Exporters: Export to various formats (MD, HTML, PDF)
"""

from .config import (
    DocumentationConfig,
    ExportConfig,
    TemplateConfig,
)
from .exporters import (
    HtmlExporter,
    MarkdownExporter,
)
from .generators import (
    ApiDocGenerator,
    GuideGenerator,
    ReferenceGenerator,
)
from .models import (
    ApiEndpoint,
    CodeExample,
    CrossReference,
    DocumentationEntry,
)

__all__ = [
    # Config
    "DocumentationConfig",
    "ExportConfig",
    "TemplateConfig",
    # Models
    "DocumentationEntry",
    "ApiEndpoint",
    "CodeExample",
    "CrossReference",
    # Generators
    "ApiDocGenerator",
    "GuideGenerator",
    "ReferenceGenerator",
    # Exporters
    "MarkdownExporter",
    "HtmlExporter",
]

__version__ = "1.0.0"
