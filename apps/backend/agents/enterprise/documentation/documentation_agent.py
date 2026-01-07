"""Documentation Agent for automated documentation generation.

World-Class Standards:
- Comprehensive docstring generation
- API documentation
- README generation
- LLM-agnostic design

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from typing import Any, ClassVar, Dict, List, Optional
import json

from ..base_enterprise_agent import BaseEnterpriseAgent, LLMRouter
from ..config import AgentCapability, EnterpriseAgentConfig
from ..types import (
    DocstringStyle,
    DocumentationResult,
    EnterpriseAgentType,
)
from .docstring_generator import DocstringGenerator, GeneratedDocstring
from .readme_generator import ReadmeGenerator
from .api_doc_generator import APIDocGenerator


class DocumentationAgent(BaseEnterpriseAgent):
    """Agent for automated documentation generation.
    
    Provides comprehensive documentation capabilities:
    - Docstring generation (Google, NumPy, Sphinx styles)
    - README generation
    - API documentation
    - Changelog updates
    
    Attributes:
        docstring_generator: Docstring generation utility
        readme_generator: README generation utility
        api_doc_generator: API documentation generator
    """
    
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.DOCUMENTATION
    AGENT_CATEGORY: ClassVar[str] = "documentation"
    
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = """You are an expert technical writer with deep knowledge of:
1. Code documentation best practices
2. Multiple docstring styles (Google, NumPy, Sphinx)
3. API documentation standards
4. README structure and content
5. Clear, concise technical writing

Generate comprehensive, accurate documentation.
Focus on clarity and usefulness.
Follow language-specific conventions."""
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize the documentation agent."""
        super().__init__(config, llm_router)
        
        # Add documentation capability
        self.add_capability(AgentCapability.DOCUMENTATION)
        
        # Initialize generators
        self.docstring_generator = DocstringGenerator()
        self.readme_generator = ReadmeGenerator()
        self.api_doc_generator = APIDocGenerator()
    
    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Documentation agent that generates docstrings, READMEs, "
            "and API documentation. Supports multiple styles and follows "
            "language-specific conventions."
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation task based on context.
        
        Args:
            context: Must contain 'code' and 'doc_type'
            
        Returns:
            Documentation generation results
        """
        if "code" not in context:
            return {
                "status": "error",
                "message": "Context must contain 'code'",
            }
        
        code = context["code"]
        doc_type = context.get("doc_type", "docstring")
        style = context.get("style", "google")
        language = context.get("language", "python")
        
        if doc_type == "docstring":
            result = await self.generate_docstrings(
                code=code,
                language=language,
                style=DocstringStyle(style) if style else DocstringStyle.GOOGLE,
            )
        elif doc_type == "readme":
            result = await self.generate_readme(
                code=code,
                project_name=context.get("project_name", "Project"),
            )
        elif doc_type == "api":
            result = await self.generate_api_docs(code=code)
        else:
            result = await self.generate_docstrings(code=code)
        
        return {
            "status": "success",
            "documentation": result,
            "doc_type": doc_type,
        }
    
    async def generate_docstrings(
        self,
        code: str,
        language: str = "python",
        style: DocstringStyle = DocstringStyle.GOOGLE,
    ) -> str:
        """Generate docstrings for code.
        
        Args:
            code: Source code to document
            language: Programming language
            style: Docstring style (google, numpy, sphinx)
            
        Returns:
            Code with added docstrings
        """
        style_guide = self._get_style_guide(style)
        
        prompt = f"""Add comprehensive docstrings to the following {language} code.

Docstring Style: {style.value}

{style_guide}

Source Code:
```{language}
{code}
```

Requirements:
1. Document all public functions, classes, and methods
2. Include parameter descriptions with types
3. Include return value descriptions
4. Include raises/exceptions if applicable
5. Add examples for complex functions
6. Keep descriptions clear and concise

Provide the complete code with docstrings added."""
        
        return await self.complete(prompt)
    
    async def generate_readme(
        self,
        code: str,
        project_name: str,
        description: Optional[str] = None,
    ) -> str:
        """Generate README for a project.
        
        Args:
            code: Sample code or main module
            project_name: Name of the project
            description: Optional project description
            
        Returns:
            Generated README markdown
        """
        prompt = f"""Generate a comprehensive README.md for the project.

Project Name: {project_name}
{f"Description: {description}" if description else ""}

Sample Code:
```
{code}
```

Generate a README with:
1. Project title and description
2. Installation instructions
3. Quick start guide
4. Usage examples
5. API reference (if applicable)
6. Configuration options
7. Contributing guidelines
8. License section

Use proper Markdown formatting."""
        
        return await self.complete(prompt)
    
    async def generate_api_docs(
        self,
        code: str,
        format: str = "markdown",
    ) -> str:
        """Generate API documentation.
        
        Args:
            code: Source code with API endpoints
            format: Output format (markdown, openapi)
            
        Returns:
            Generated API documentation
        """
        prompt = f"""Generate API documentation for the following code.

```
{code}
```

Output Format: {format}

For each endpoint/function:
1. Method and path (for REST APIs)
2. Description
3. Parameters with types
4. Request body schema (if applicable)
5. Response format
6. Error responses
7. Example request/response

Generate comprehensive, developer-friendly documentation."""
        
        return await self.complete(prompt)
    
    async def update_changelog(
        self,
        changes: List[str],
        version: str,
        existing_changelog: Optional[str] = None,
    ) -> str:
        """Generate changelog entry.
        
        Args:
            changes: List of changes to document
            version: Version number
            existing_changelog: Existing changelog to prepend to
            
        Returns:
            Updated changelog
        """
        prompt = f"""Generate a changelog entry for version {version}.

Changes:
{chr(10).join(f'- {change}' for change in changes)}

Format the changelog entry following Keep a Changelog conventions:
- Added (new features)
- Changed (changes to existing functionality)
- Deprecated (soon-to-be removed features)
- Removed (removed features)
- Fixed (bug fixes)
- Security (security fixes)

Generate only the new entry section."""
        
        entry = await self.complete(prompt)
        
        if existing_changelog:
            # Find where to insert (after header)
            lines = existing_changelog.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("## "):
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, entry)
            return "\n".join(lines)
        
        return entry
    
    async def suggest_improvements(
        self,
        documentation: str,
    ) -> List[str]:
        """Suggest improvements for existing documentation.
        
        Args:
            documentation: Existing documentation
            
        Returns:
            List of improvement suggestions
        """
        prompt = f"""Review this documentation and suggest improvements.

```
{documentation}
```

Provide suggestions in JSON format:
{{
  "suggestions": [
    {{
      "location": "Where in the doc",
      "issue": "What's wrong",
      "suggestion": "How to improve"
    }}
  ]
}}

Focus on:
- Clarity and readability
- Missing information
- Incorrect or outdated content
- Formatting issues
- Examples that could be added
"""
        
        response = await self.complete(prompt)
        
        try:
            data = json.loads(response)
            return [
                f"{s['location']}: {s['suggestion']}"
                for s in data.get("suggestions", [])
            ]
        except json.JSONDecodeError:
            return [response]
    
    def _get_style_guide(self, style: DocstringStyle) -> str:
        """Get style guide for docstring format."""
        guides = {
            DocstringStyle.GOOGLE: """
Google Style Guide:
- Use triple double quotes
- One-line summary, blank line, then details
- Args: section with param name, type in parens, description
- Returns: section with type and description
- Raises: section listing exceptions

Example:
    def function(arg1: str, arg2: int) -> bool:
        \"\"\"One-line summary.
        
        More detailed description.
        
        Args:
            arg1 (str): Description of arg1.
            arg2 (int): Description of arg2.
            
        Returns:
            bool: Description of return value.
            
        Raises:
            ValueError: If arg1 is empty.
        \"\"\"
""",
            DocstringStyle.NUMPY: """
NumPy Style Guide:
- Use triple double quotes
- Sections separated by headers with dashes
- Parameters, Returns, Raises sections

Example:
    def function(arg1, arg2):
        \"\"\"One-line summary.
        
        More detailed description.
        
        Parameters
        ----------
        arg1 : str
            Description of arg1.
        arg2 : int
            Description of arg2.
            
        Returns
        -------
        bool
            Description of return value.
            
        Raises
        ------
        ValueError
            If arg1 is empty.
        \"\"\"
""",
            DocstringStyle.SPHINX: """
Sphinx Style Guide:
- Use triple double quotes
- Use :param:, :type:, :returns:, :raises: directives

Example:
    def function(arg1, arg2):
        \"\"\"One-line summary.
        
        More detailed description.
        
        :param arg1: Description of arg1.
        :type arg1: str
        :param arg2: Description of arg2.
        :type arg2: int
        :returns: Description of return value.
        :rtype: bool
        :raises ValueError: If arg1 is empty.
        \"\"\"
""",
        }
        return guides.get(style, guides[DocstringStyle.GOOGLE])
