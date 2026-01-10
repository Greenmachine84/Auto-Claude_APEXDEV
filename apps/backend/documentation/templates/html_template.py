"""
HTML template.

Renders documentation entries in HTML format.
"""

import html

from ..config import TemplateConfig
from ..models import (
    CodeExample,
    CrossReference,
    DocumentationEntry,
    DocumentationIndex,
)
from .base import BaseTemplate, TemplateContext


class HtmlTemplate(BaseTemplate):
    """Renders documentation as HTML."""

    def __init__(self, config: TemplateConfig):
        """Initialize HTML template."""
        super().__init__(config)
        self._highlight_theme = config.code_theme or "github-dark"

    def render(self, context: TemplateContext) -> str:
        """
        Render template with context.

        Args:
            context: Template context

        Returns:
            Rendered HTML
        """
        head = self._render_head(context)
        body = self._render_body(context)

        return f"""<!DOCTYPE html>
<html lang="en">
{head}
{body}
</html>"""

    def _render_head(self, context: TemplateContext) -> str:
        """Render HTML head section."""
        title = context.entry.title if context.entry else context.project_name
        custom_css = ""
        if self.config.custom_css:
            custom_css = f'<link rel="stylesheet" href="{self.config.custom_css}">'

        return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.escape(title)} - {self.escape(context.project_name)}</title>
    <meta name="generator" content="Auto-Claude Documentation">
    <meta name="version" content="{context.project_version}">
    <style>
        :root {{
            --primary-color: #3b82f6;
            --text-color: #1f2937;
            --bg-color: #ffffff;
            --code-bg: #f3f4f6;
            --border-color: #e5e7eb;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        nav.breadcrumbs {{ color: #6b7280; margin-bottom: 1rem; }}
        nav.breadcrumbs a {{ color: var(--primary-color); text-decoration: none; }}
        h1, h2, h3 {{ margin-top: 2rem; }}
        code {{ background: var(--code-bg); padding: 0.2em 0.4em; border-radius: 4px; }}
        pre {{ background: var(--code-bg); padding: 1rem; border-radius: 8px; overflow-x: auto; }}
        pre code {{ background: none; padding: 0; }}
        .tag {{ background: var(--primary-color); color: white; padding: 0.2em 0.6em;
                border-radius: 4px; font-size: 0.85em; margin-right: 0.5em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid var(--border-color); padding: 0.75rem; text-align: left; }}
        th {{ background: var(--code-bg); }}
        .admonition {{ border-left: 4px solid var(--primary-color); padding: 1rem;
                       margin: 1rem 0; background: var(--code-bg); border-radius: 0 8px 8px 0; }}
        .admonition.warning {{ border-color: #f59e0b; }}
        .admonition.danger {{ border-color: #ef4444; }}
        .toc {{ background: var(--code-bg); padding: 1rem; border-radius: 8px; }}
        .toc ul {{ list-style: none; padding-left: 1rem; }}
        footer {{ margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--border-color);
                  color: #6b7280; font-size: 0.9em; }}
    </style>
    {custom_css}
</head>"""

    def _render_body(self, context: TemplateContext) -> str:
        """Render HTML body section."""
        parts = ["<body>"]

        # Navigation
        if context.navigation:
            parts.append(self._render_nav(context.navigation))

        # Breadcrumbs
        if context.breadcrumbs and self.config.include_breadcrumbs:
            parts.append(self._render_breadcrumbs(context.breadcrumbs))

        # Main content
        parts.append("<main>")
        if context.entry:
            parts.append(self.render_entry(context.entry))
        parts.append("</main>")

        # Footer
        parts.append(self._render_footer(context))

        # Custom JS
        if self.config.custom_js:
            parts.append(f'<script src="{self.config.custom_js}"></script>')

        parts.append("</body>")
        return "\n".join(parts)

    def render_entry(self, entry: DocumentationEntry) -> str:
        """
        Render a documentation entry.

        Args:
            entry: Documentation entry

        Returns:
            Rendered HTML
        """
        parts = []

        # Title
        parts.append(f"<h1>{self.escape(entry.title)}</h1>")

        # Tags
        if entry.tags:
            tags_html = "".join(
                [f'<span class="tag">{self.escape(tag)}</span>' for tag in entry.tags]
            )
            parts.append(f'<div class="tags">{tags_html}</div>')

        # Source link
        if entry.source_file:
            source_url = str(entry.source_file)
            if entry.source_line:
                source_url += f"#L{entry.source_line}"
            parts.append(f'<p><a href="{source_url}">View Source</a></p>')

        # Table of contents
        if self.config.include_toc:
            toc = self._generate_toc(entry.content)
            if toc:
                parts.append('<nav class="toc">')
                parts.append("<h2>Contents</h2>")
                parts.append(toc)
                parts.append("</nav>")

        # Main content (convert Markdown to HTML)
        content_html = self._markdown_to_html(entry.content)
        parts.append(f'<div class="content">{content_html}</div>')

        # Examples
        if entry.examples:
            parts.append('<section class="examples">')
            parts.append("<h2>Examples</h2>")
            for example in entry.examples:
                parts.append(self._render_example(example))
            parts.append("</section>")

        # Cross-references
        if entry.cross_refs:
            parts.append('<section class="see-also">')
            parts.append("<h2>See Also</h2>")
            parts.append("<ul>")
            for ref in entry.cross_refs:
                parts.append(f"<li>{self._render_cross_ref(ref)}</li>")
            parts.append("</ul>")
            parts.append("</section>")

        return "\n".join(parts)

    def render_index(self, index: DocumentationIndex) -> str:
        """
        Render documentation index.

        Args:
            index: Documentation index

        Returns:
            Rendered HTML index
        """
        parts = []

        parts.append("<h1>Documentation Index</h1>")
        parts.append(f"<p><strong>Version:</strong> {index.version}</p>")
        parts.append(
            f"<p><strong>Generated:</strong> {index.generated_at.strftime('%Y-%m-%d %H:%M')}</p>"
        )

        # Categories
        for category, entry_ids in index.categories.items():
            parts.append(f"<h2>{self.escape(category.title())}</h2>")
            parts.append("<ul>")
            for entry_id in entry_ids:
                entry = index.entries.get(entry_id)
                if entry:
                    parts.append(
                        f'<li><a href="{entry_id}.html">{self.escape(entry.title)}</a></li>'
                    )
            parts.append("</ul>")

        return "\n".join(parts)

    def _render_nav(self, navigation: list[dict]) -> str:
        """Render navigation sidebar."""
        parts = ['<nav class="sidebar">']
        parts.append("<ul>")

        for item in navigation:
            title = self.escape(item.get("title", ""))
            url = item.get("url", "#")
            children = item.get("children", [])

            parts.append(f'<li><a href="{url}">{title}</a>')

            if children:
                parts.append("<ul>")
                for child in children:
                    child_title = self.escape(child.get("title", ""))
                    child_url = child.get("url", "#")
                    parts.append(f'<li><a href="{child_url}">{child_title}</a></li>')
                parts.append("</ul>")

            parts.append("</li>")

        parts.append("</ul>")
        parts.append("</nav>")
        return "\n".join(parts)

    def _render_breadcrumbs(self, breadcrumbs: list[tuple[str, str]]) -> str:
        """Render breadcrumb navigation."""
        links = [
            f'<a href="{url}">{self.escape(title)}</a>' for title, url in breadcrumbs
        ]
        return f'<nav class="breadcrumbs">{" &gt; ".join(links)}</nav>'

    def _render_footer(self, context: TemplateContext) -> str:
        """Render page footer."""
        return f"""<footer>
    <p>Generated by {self.escape(context.project_name)} Documentation</p>
    <p>Version {context.project_version}</p>
</footer>"""

    def _render_example(self, example: CodeExample) -> str:
        """Render a code example."""
        parts = []

        if example.title:
            parts.append(f"<h3>{self.escape(example.title)}</h3>")

        if example.description:
            parts.append(f"<p>{self.escape(example.description)}</p>")

        code = self.escape(example.code)
        parts.append(
            f'<pre><code class="language-{example.language}">{code}</code></pre>'
        )

        if example.output:
            parts.append("<p><strong>Output:</strong></p>")
            parts.append(f"<pre><code>{self.escape(example.output)}</code></pre>")

        return "\n".join(parts)

    def _render_cross_ref(self, ref: CrossReference) -> str:
        """Render a cross-reference."""
        url = ref.url if ref.url else f"{ref.target_id}.html"
        link = f'<a href="{url}">{self.escape(ref.target_title)}</a>'

        if ref.description:
            return f"{link} - {self.escape(ref.description)}"
        return link

    def _generate_toc(self, content: str) -> str:
        """Generate HTML table of contents from content."""
        items = []
        for line in content.split("\n"):
            if line.startswith("## "):
                title = line[3:].strip()
                anchor = title.lower().replace(" ", "-")
                items.append(f'<li><a href="#{anchor}">{self.escape(title)}</a></li>')
            elif line.startswith("### "):
                title = line[4:].strip()
                anchor = title.lower().replace(" ", "-")
                items.append(
                    f'<li class="indent"><a href="#{anchor}">{self.escape(title)}</a></li>'
                )

        if items:
            return "<ul>" + "\n".join(items) + "</ul>"
        return ""

    def _markdown_to_html(self, markdown: str) -> str:
        """Basic Markdown to HTML conversion."""
        lines = []
        in_code_block = False
        code_lang = ""

        for line in markdown.split("\n"):
            # Code blocks
            if line.startswith("```"):
                if in_code_block:
                    lines.append("</code></pre>")
                    in_code_block = False
                else:
                    code_lang = line[3:].strip()
                    lines.append(f'<pre><code class="language-{code_lang}">')
                    in_code_block = True
                continue

            if in_code_block:
                lines.append(self.escape(line))
                continue

            # Headings
            if line.startswith("### "):
                anchor = line[4:].strip().lower().replace(" ", "-")
                lines.append(f'<h3 id="{anchor}">{self.escape(line[4:])}</h3>')
            elif line.startswith("## "):
                anchor = line[3:].strip().lower().replace(" ", "-")
                lines.append(f'<h2 id="{anchor}">{self.escape(line[3:])}</h2>')
            elif line.startswith("# "):
                lines.append(f"<h1>{self.escape(line[2:])}</h1>")
            elif line.startswith("- "):
                lines.append(f"<li>{self.escape(line[2:])}</li>")
            elif line.strip():
                lines.append(f"<p>{self.escape(line)}</p>")

        return "\n".join(lines)

    def escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return html.escape(str(text))

    def render_table(self, headers: list[str], rows: list[list[str]]) -> str:
        """
        Render an HTML table.

        Args:
            headers: Column headers
            rows: Table rows

        Returns:
            Rendered table
        """
        parts = ["<table>"]

        # Header
        parts.append("<thead><tr>")
        for header in headers:
            parts.append(f"<th>{self.escape(header)}</th>")
        parts.append("</tr></thead>")

        # Body
        parts.append("<tbody>")
        for row in rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{self.escape(cell)}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")

        parts.append("</table>")
        return "\n".join(parts)
