"""
HTML exporter.

Exports documentation entries to HTML files.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import ExportConfig
from ..models import DocumentationEntry, DocumentationIndex
from ..templates.html_template import HtmlTemplate
from ..templates.base import TemplateContext, TemplateConfig


class HtmlExporter:
    """Exports documentation to HTML format."""

    def __init__(self, config: ExportConfig):
        """
        Initialize exporter.

        Args:
            config: Export configuration
        """
        self.config = config
        self.template = HtmlTemplate(TemplateConfig())
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def export_entry(
        self,
        entry: DocumentationEntry,
        filename: Optional[str] = None,
        navigation: Optional[list] = None
    ) -> Path:
        """
        Export a single documentation entry.

        Args:
            entry: Documentation entry to export
            filename: Optional filename (default: entry.id.html)
            navigation: Optional navigation structure

        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"{entry.id}.html"

        output_path = self.config.output_dir / filename

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build context
        context = TemplateContext(
            entry=entry,
            base_url=self.config.base_url,
            navigation=navigation or [],
        )

        if self.config.include_version:
            context.metadata["version"] = entry.metadata.get("version", "1.0.0")
            context.project_version = entry.metadata.get("version", "1.0.0")

        if self.config.include_timestamp:
            context.metadata["generated"] = datetime.now().isoformat()

        # Render and write
        content = self.template.render(context)

        if self.config.minify_html:
            content = self._minify_html(content)

        output_path.write_text(content, encoding="utf-8")

        return output_path

    def export_entries(
        self,
        entries: list[DocumentationEntry],
        subdir: str = "",
        navigation: Optional[list] = None
    ) -> list[Path]:
        """
        Export multiple documentation entries.

        Args:
            entries: List of entries to export
            subdir: Optional subdirectory
            navigation: Optional navigation structure

        Returns:
            List of exported file paths
        """
        paths = []
        output_dir = self.config.output_dir

        if subdir:
            output_dir = output_dir / subdir
            output_dir.mkdir(parents=True, exist_ok=True)

        for entry in entries:
            filename = f"{entry.id}.html"
            path = output_dir / filename

            context = TemplateContext(
                entry=entry,
                base_url=self.config.base_url,
                navigation=navigation or [],
            )
            content = self.template.render(context)

            if self.config.minify_html:
                content = self._minify_html(content)

            path.write_text(content, encoding="utf-8")
            paths.append(path)

        return paths

    def export_index(
        self,
        index: DocumentationIndex,
        filename: str = "index.html",
        project_name: str = "",
        project_description: str = ""
    ) -> Path:
        """
        Export documentation index.

        Args:
            index: Documentation index
            filename: Output filename
            project_name: Project name
            project_description: Project description

        Returns:
            Path to exported file
        """
        output_path = self.config.output_dir / filename

        # Create a synthetic entry for the index
        index_entry = DocumentationEntry(
            id="index",
            title=f"{project_name} Documentation" if project_name else "Documentation Index",
            content=self.template.render_index(index),
            entry_type="index",
        )

        context = TemplateContext(
            entry=index_entry,
            index=index,
            project_name=project_name,
            project_version=index.version,
            base_url=self.config.base_url,
        )

        content = self.template.render(context)

        if self.config.minify_html:
            content = self._minify_html(content)

        output_path.write_text(content, encoding="utf-8")

        return output_path

    def export_full(
        self,
        index: DocumentationIndex,
        project_name: str = "",
        project_version: str = ""
    ) -> list[Path]:
        """
        Export full documentation including all entries, index, and assets.

        Args:
            index: Documentation index
            project_name: Project name
            project_version: Project version

        Returns:
            List of all exported file paths
        """
        paths = []

        # Build navigation structure
        navigation = self._build_navigation(index)

        # Export all entries
        for entry_id, entry in index.entries.items():
            # Organize by entry type
            subdir = entry.entry_type
            if subdir:
                (self.config.output_dir / subdir).mkdir(parents=True, exist_ok=True)
                filename = f"{subdir}/{entry.id}.html"
            else:
                filename = f"{entry.id}.html"

            path = self.export_entry(entry, filename, navigation)
            paths.append(path)

        # Export index
        if self.config.create_index:
            index_path = self.export_index(
                index,
                project_name=project_name,
            )
            paths.append(index_path)

            # Create category indexes
            for category, entry_ids in index.categories.items():
                category_entries = [
                    index.entries[eid]
                    for eid in entry_ids
                    if eid in index.entries
                ]
                category_path = self._export_category_index(
                    category,
                    category_entries,
                    navigation
                )
                paths.append(category_path)

        # Export assets
        assets_path = self._export_assets()
        if assets_path:
            paths.append(assets_path)

        return paths

    def _build_navigation(self, index: DocumentationIndex) -> list[dict]:
        """Build navigation structure from index."""
        nav = []

        for category, entry_ids in index.categories.items():
            category_nav = {
                "title": category.title(),
                "url": f"{category}/index.html",
                "children": [],
            }

            for entry_id in entry_ids:
                entry = index.entries.get(entry_id)
                if entry:
                    category_nav["children"].append({
                        "title": entry.title,
                        "url": f"{category}/{entry.id}.html",
                    })

            nav.append(category_nav)

        return nav

    def _export_category_index(
        self,
        category: str,
        entries: list[DocumentationEntry],
        navigation: list
    ) -> Path:
        """Export category index page."""
        output_path = self.config.output_dir / category / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create category index content
        content_lines = [
            f"<h1>{category.title()}</h1>",
            f"<p>Documentation for {category} components.</p>",
            "<h2>Contents</h2>",
            "<ul>",
        ]

        for entry in entries:
            content_lines.append(f'<li><a href="{entry.id}.html">{entry.title}</a></li>')

        content_lines.append("</ul>")

        index_entry = DocumentationEntry(
            id=f"{category}-index",
            title=f"{category.title()} Documentation",
            content="\n".join(content_lines),
            entry_type="index",
        )

        context = TemplateContext(
            entry=index_entry,
            base_url=self.config.base_url,
            navigation=navigation,
        )

        content = self.template.render(context)

        if self.config.minify_html:
            content = self._minify_html(content)

        output_path.write_text(content, encoding="utf-8")

        return output_path

    def _export_assets(self) -> Optional[Path]:
        """Export static assets (CSS, JS, images)."""
        assets_dir = self.config.output_dir / self.config.asset_prefix.rstrip("/")
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Create default CSS
        css_content = """
/* Documentation Styles */
:root {
    --primary-color: #3b82f6;
    --text-color: #1f2937;
    --bg-color: #ffffff;
    --code-bg: #f3f4f6;
    --border-color: #e5e7eb;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}

a { color: var(--primary-color); text-decoration: none; }
a:hover { text-decoration: underline; }

code {
    background: var(--code-bg);
    padding: 0.2em 0.4em;
    border-radius: 4px;
    font-family: 'Fira Code', Consolas, monospace;
}

pre {
    background: var(--code-bg);
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
}

pre code { background: none; padding: 0; }

.tag {
    background: var(--primary-color);
    color: white;
    padding: 0.2em 0.6em;
    border-radius: 4px;
    font-size: 0.85em;
    margin-right: 0.5em;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
}

th, td {
    border: 1px solid var(--border-color);
    padding: 0.75rem;
    text-align: left;
}

th { background: var(--code-bg); }

.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 250px;
    padding: 1rem;
    background: var(--code-bg);
    overflow-y: auto;
}

@media (max-width: 768px) {
    .sidebar { display: none; }
}
"""
        css_path = assets_dir / "styles.css"
        css_path.write_text(css_content, encoding="utf-8")

        # Create default JS
        js_content = """
// Documentation Scripts
document.addEventListener('DOMContentLoaded', function() {
    // Syntax highlighting (basic)
    document.querySelectorAll('pre code').forEach(function(block) {
        // Add line numbers
        const lines = block.textContent.split('\\n');
        if (lines.length > 3) {
            block.classList.add('line-numbers');
        }
    });

    // Copy code button
    document.querySelectorAll('pre').forEach(function(block) {
        const button = document.createElement('button');
        button.textContent = 'Copy';
        button.className = 'copy-btn';
        button.onclick = function() {
            navigator.clipboard.writeText(block.textContent);
            button.textContent = 'Copied!';
            setTimeout(function() { button.textContent = 'Copy'; }, 2000);
        };
        block.style.position = 'relative';
        block.appendChild(button);
    });

    // Search functionality
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.searchable').forEach(function(el) {
                const text = el.textContent.toLowerCase();
                el.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});
"""
        js_path = assets_dir / "scripts.js"
        js_path.write_text(js_content, encoding="utf-8")

        return assets_dir

    def _minify_html(self, html: str) -> str:
        """
        Minify HTML content.

        Args:
            html: HTML content

        Returns:
            Minified HTML
        """
        import re

        # Remove comments
        html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

        # Remove whitespace between tags
        html = re.sub(r">\s+<", "><", html)

        # Remove leading/trailing whitespace from lines
        html = "\n".join(line.strip() for line in html.split("\n"))

        # Remove empty lines
        html = re.sub(r"\n+", "\n", html)

        return html.strip()

    def export_search_index(self, index: DocumentationIndex) -> Path:
        """
        Export search index for client-side search.

        Args:
            index: Documentation index

        Returns:
            Path to search index file
        """
        import json

        search_data = []

        for entry_id, entry in index.entries.items():
            search_data.append({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content[:500],  # First 500 chars
                "type": entry.entry_type,
                "tags": entry.tags,
                "url": f"{entry.entry_type}/{entry.id}.html",
            })

        output_path = self.config.output_dir / "search-index.json"
        output_path.write_text(json.dumps(search_data, indent=2), encoding="utf-8")

        return output_path
