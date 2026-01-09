"""
Markdown template.

Renders documentation entries in Markdown format.
"""

from ..config import TemplateConfig
from ..models import (
    CodeExample,
    CrossReference,
    DocumentationEntry,
    DocumentationIndex,
)
from .base import BaseTemplate, TemplateContext


class MarkdownTemplate(BaseTemplate):
    """Renders documentation as Markdown."""

    def __init__(self, config: TemplateConfig):
        """Initialize Markdown template."""
        super().__init__(config)

    def render(self, context: TemplateContext) -> str:
        """
        Render template with context.

        Args:
            context: Template context

        Returns:
            Rendered Markdown
        """
        lines = []

        # Front matter (YAML)
        if context.metadata:
            lines.append("---")
            for key, value in context.metadata.items():
                if isinstance(value, list):
                    lines.append(f"{key}:")
                    for item in value:
                        lines.append(f"  - {item}")
                else:
                    lines.append(f"{key}: {value}")
            lines.append("---")
            lines.append("")

        # Breadcrumbs
        if context.breadcrumbs and self.config.include_breadcrumbs:
            lines.append(self.render_breadcrumbs(context.breadcrumbs))
            lines.append("")

        # Main content
        if context.entry:
            lines.append(self.render_entry(context.entry))

        return "\n".join(lines)

    def render_entry(self, entry: DocumentationEntry) -> str:
        """
        Render a documentation entry.

        Args:
            entry: Documentation entry

        Returns:
            Rendered Markdown
        """
        lines = []

        # Title
        lines.append(f"# {entry.title}")
        lines.append("")

        # Metadata badges
        if entry.tags:
            badges = " ".join([f"`{tag}`" for tag in entry.tags])
            lines.append(badges)
            lines.append("")

        # Source link
        if entry.source_file:
            source_link = f"[View Source]({entry.source_file}"
            if entry.source_line:
                source_link += f"#L{entry.source_line}"
            source_link += ")"
            lines.append(source_link)
            lines.append("")

        # Table of contents
        if self.config.include_toc:
            toc = self._generate_toc(entry.content)
            if toc:
                lines.append("## Table of Contents")
                lines.append("")
                lines.append(toc)
                lines.append("")

        # Main content
        lines.append(entry.content)
        lines.append("")

        # Examples
        if entry.examples:
            lines.append("## Examples")
            lines.append("")
            for example in entry.examples:
                lines.append(self._render_example(example))
                lines.append("")

        # Cross-references
        if entry.cross_refs:
            lines.append("## See Also")
            lines.append("")
            for ref in entry.cross_refs:
                lines.append(f"- {self._render_cross_ref(ref)}")
            lines.append("")

        return "\n".join(lines)

    def render_index(self, index: DocumentationIndex) -> str:
        """
        Render documentation index.

        Args:
            index: Documentation index

        Returns:
            Rendered Markdown index
        """
        lines = []

        lines.append("# Documentation Index")
        lines.append("")
        lines.append(f"**Version:** {index.version}")
        lines.append(f"**Generated:** {index.generated_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Group by category
        for category, entry_ids in index.categories.items():
            lines.append(f"## {category.title()}")
            lines.append("")

            for entry_id in entry_ids:
                entry = index.entries.get(entry_id)
                if entry:
                    lines.append(f"- [{entry.title}]({entry_id}.md)")

            lines.append("")

        # Tags section
        if index.tags:
            lines.append("## Tags")
            lines.append("")
            for tag, entry_ids in index.tags.items():
                count = len(entry_ids)
                lines.append(f"- **{tag}** ({count} entries)")
            lines.append("")

        return "\n".join(lines)

    def _generate_toc(self, content: str) -> str:
        """Generate table of contents from content headings."""
        lines = []
        for line in content.split("\n"):
            if line.startswith("## "):
                title = line[3:].strip()
                anchor = title.lower().replace(" ", "-")
                lines.append(f"- [{title}](#{anchor})")
            elif line.startswith("### "):
                title = line[4:].strip()
                anchor = title.lower().replace(" ", "-")
                lines.append(f"  - [{title}](#{anchor})")
        return "\n".join(lines)

    def _render_example(self, example: CodeExample) -> str:
        """Render a code example."""
        lines = []

        if example.title:
            lines.append(f"### {example.title}")
            lines.append("")

        if example.description:
            lines.append(example.description)
            lines.append("")

        lines.append(f"```{example.language}")
        lines.append(example.code)
        lines.append("```")

        if example.output:
            lines.append("")
            lines.append("**Output:**")
            lines.append("```")
            lines.append(example.output)
            lines.append("```")

        return "\n".join(lines)

    def _render_cross_ref(self, ref: CrossReference) -> str:
        """Render a cross-reference."""
        link = f"[{ref.target_title}]"
        if ref.url:
            link += f"({ref.url})"
        else:
            link += f"({ref.target_id}.md)"

        if ref.description:
            return f"{link} - {ref.description}"
        return link

    def render_nav(self, navigation: list[dict]) -> str:
        """
        Render navigation sidebar.

        Args:
            navigation: Navigation structure

        Returns:
            Rendered navigation
        """
        lines = []

        for item in navigation:
            title = item.get("title", "")
            url = item.get("url", "#")
            children = item.get("children", [])

            lines.append(f"- [{title}]({url})")

            for child in children:
                child_title = child.get("title", "")
                child_url = child.get("url", "#")
                lines.append(f"  - [{child_title}]({child_url})")

        return "\n".join(lines)

    def render_table(self, headers: list[str], rows: list[list[str]]) -> str:
        """
        Render a Markdown table.

        Args:
            headers: Column headers
            rows: Table rows

        Returns:
            Rendered table
        """
        lines = []

        # Header row
        lines.append("| " + " | ".join(headers) + " |")

        # Separator
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Data rows
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    def render_admonition(
        self, content: str, admonition_type: str = "note", title: str = ""
    ) -> str:
        """
        Render an admonition (callout).

        Args:
            content: Admonition content
            admonition_type: Type (note, warning, tip, etc.)
            title: Optional title

        Returns:
            Rendered admonition
        """
        icon = {
            "note": "ℹ️",
            "warning": "⚠️",
            "tip": "💡",
            "danger": "🚫",
            "success": "✅",
        }.get(admonition_type, "📝")

        lines = []
        header = f"> {icon}"
        if title:
            header += f" **{title}**"
        else:
            header += f" **{admonition_type.title()}**"

        lines.append(header)
        lines.append(">")

        for line in content.split("\n"):
            lines.append(f"> {line}")

        return "\n".join(lines)
