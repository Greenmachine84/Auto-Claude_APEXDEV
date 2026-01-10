"""
Documentation templates.

Provides templates for rendering documentation
in various formats including Markdown and HTML.
"""

from .base import BaseTemplate
from .html_template import HtmlTemplate
from .markdown_template import MarkdownTemplate

__all__ = [
    "BaseTemplate",
    "MarkdownTemplate",
    "HtmlTemplate",
]
