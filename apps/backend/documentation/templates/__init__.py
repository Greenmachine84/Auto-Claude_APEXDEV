"""
Documentation templates.

Provides templates for rendering documentation
in various formats including Markdown and HTML.
"""

from .base import BaseTemplate
from .markdown_template import MarkdownTemplate
from .html_template import HtmlTemplate

__all__ = [
    "BaseTemplate",
    "MarkdownTemplate",
    "HtmlTemplate",
]
