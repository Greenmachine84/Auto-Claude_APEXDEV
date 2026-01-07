"""Documentation capability for enterprise agents.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class DocFormat(str, Enum):
    """Documentation output format."""
    MARKDOWN = "markdown"
    HTML = "html"
    RST = "rst"
    PLAIN = "plain"


class DocstringStyle(str, Enum):
    """Docstring style."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"


@dataclass
class DocOutput:
    """Documentation output."""
    content: str
    format: DocFormat = DocFormat.MARKDOWN
    title: str = ""
    sections: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "format": self.format.value,
            "title": self.title,
            "sections": self.sections,
            "metadata": self.metadata,
        }
    
    def to_html(self) -> str:
        """Convert markdown to basic HTML."""
        if self.format != DocFormat.MARKDOWN:
            return self.content
        
        html = self.content
        
        # Headers
        import re
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Code blocks
        html = re.sub(r'```(\w+)?\n([^`]+)```', r'<pre><code>\2</code></pre>', html)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold/italic
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        
        return html


class DocumentationCapability:
    """Provides documentation generation capabilities to agents.
    
    Generates various types of documentation including
    docstrings, READMEs, and API docs.
    """
    
    def __init__(self):
        """Initialize the capability."""
        pass
    
    def generate_docstring(
        self,
        function_info: Dict[str, Any],
        style: DocstringStyle = DocstringStyle.GOOGLE,
    ) -> str:
        """Generate a docstring for a function.
        
        Args:
            function_info: Function metadata (name, params, return_type)
            style: Docstring style
            
        Returns:
            Generated docstring
        """
        if style == DocstringStyle.GOOGLE:
            return self._google_docstring(function_info)
        elif style == DocstringStyle.NUMPY:
            return self._numpy_docstring(function_info)
        elif style == DocstringStyle.SPHINX:
            return self._sphinx_docstring(function_info)
        else:
            return self._google_docstring(function_info)
    
    def _google_docstring(self, info: Dict[str, Any]) -> str:
        """Generate Google-style docstring."""
        lines = ['"""[Summary].', '']
        
        params = info.get("params", [])
        if params:
            lines.append('Args:')
            for param in params:
                name = param.get("name", "")
                ptype = param.get("type", "")
                desc = param.get("description", "[Description]")
                if ptype:
                    lines.append(f"    {name} ({ptype}): {desc}")
                else:
                    lines.append(f"    {name}: {desc}")
            lines.append('')
        
        return_type = info.get("return_type")
        if return_type and return_type != "None":
            lines.append('Returns:')
            lines.append(f"    {return_type}: [Description].")
            lines.append('')
        
        raises = info.get("raises", [])
        if raises:
            lines.append('Raises:')
            for exc in raises:
                lines.append(f"    {exc}: [When raised].")
            lines.append('')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _numpy_docstring(self, info: Dict[str, Any]) -> str:
        """Generate NumPy-style docstring."""
        lines = ['"""[Summary].', '']
        
        params = info.get("params", [])
        if params:
            lines.append('Parameters')
            lines.append('----------')
            for param in params:
                name = param.get("name", "")
                ptype = param.get("type", "object")
                lines.append(f"{name} : {ptype}")
                lines.append(f"    [Description].")
            lines.append('')
        
        return_type = info.get("return_type")
        if return_type and return_type != "None":
            lines.append('Returns')
            lines.append('-------')
            lines.append(return_type)
            lines.append('    [Description].')
            lines.append('')
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _sphinx_docstring(self, info: Dict[str, Any]) -> str:
        """Generate Sphinx-style docstring."""
        lines = ['"""[Summary].', '']
        
        params = info.get("params", [])
        for param in params:
            name = param.get("name", "")
            ptype = param.get("type", "")
            lines.append(f":param {name}: [Description].")
            if ptype:
                lines.append(f":type {name}: {ptype}")
        
        return_type = info.get("return_type")
        if return_type and return_type != "None":
            lines.append(f":returns: [Description].")
            lines.append(f":rtype: {return_type}")
        
        lines.append('')
        lines.append('"""')
        return '\n'.join(lines)
    
    def generate_readme(
        self,
        project_info: Dict[str, Any],
    ) -> DocOutput:
        """Generate README documentation.
        
        Args:
            project_info: Project metadata
            
        Returns:
            Generated README
        """
        name = project_info.get("name", "Project")
        description = project_info.get("description", "")
        features = project_info.get("features", [])
        
        sections = []
        
        # Title
        lines = [f"# {name}", ""]
        if description:
            lines.append(description)
            lines.append("")
        
        # Features
        if features:
            lines.append("## Features")
            lines.append("")
            for feature in features:
                lines.append(f"- {feature}")
            lines.append("")
            sections.append({"title": "Features", "content": "\n".join(f"- {f}" for f in features)})
        
        # Installation
        lines.append("## Installation")
        lines.append("")
        lines.append("```bash")
        lines.append(f"pip install {name.lower().replace(' ', '-')}")
        lines.append("```")
        lines.append("")
        sections.append({"title": "Installation", "content": f"pip install {name.lower().replace(' ', '-')}"})
        
        # Usage
        lines.append("## Usage")
        lines.append("")
        lines.append("```python")
        lines.append(f"from {name.lower().replace(' ', '_')} import main")
        lines.append("")
        lines.append("# Your code here")
        lines.append("```")
        lines.append("")
        
        # License
        lines.append("## License")
        lines.append("")
        lines.append(f"This project is licensed under the {project_info.get('license', 'MIT')} License.")
        
        return DocOutput(
            content="\n".join(lines),
            format=DocFormat.MARKDOWN,
            title=name,
            sections=sections,
            metadata=project_info,
        )
    
    def generate_api_doc(
        self,
        endpoints: List[Dict[str, Any]],
    ) -> DocOutput:
        """Generate API documentation.
        
        Args:
            endpoints: List of API endpoint definitions
            
        Returns:
            Generated API documentation
        """
        lines = ["# API Reference", ""]
        sections = []
        
        for endpoint in endpoints:
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")
            description = endpoint.get("description", "")
            
            lines.append(f"## `{method}` {path}")
            lines.append("")
            if description:
                lines.append(description)
                lines.append("")
            
            # Parameters
            params = endpoint.get("parameters", [])
            if params:
                lines.append("### Parameters")
                lines.append("")
                lines.append("| Name | Type | Required | Description |")
                lines.append("|------|------|----------|-------------|")
                for param in params:
                    req = "✓" if param.get("required") else ""
                    lines.append(
                        f"| {param.get('name', '')} | "
                        f"{param.get('type', 'string')} | "
                        f"{req} | "
                        f"{param.get('description', '')} |"
                    )
                lines.append("")
            
            sections.append({
                "title": f"{method} {path}",
                "content": description,
            })
        
        return DocOutput(
            content="\n".join(lines),
            format=DocFormat.MARKDOWN,
            title="API Reference",
            sections=sections,
        )
    
    def merge_docs(
        self,
        docs: List[DocOutput],
    ) -> DocOutput:
        """Merge multiple documentation outputs.
        
        Args:
            docs: List of documentation outputs
            
        Returns:
            Merged documentation
        """
        all_content = []
        all_sections = []
        
        for doc in docs:
            all_content.append(doc.content)
            all_sections.extend(doc.sections)
        
        return DocOutput(
            content="\n\n---\n\n".join(all_content),
            format=docs[0].format if docs else DocFormat.MARKDOWN,
            title="Combined Documentation",
            sections=all_sections,
        )
