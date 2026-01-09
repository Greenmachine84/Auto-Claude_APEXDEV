"""Docstring generation skill.

Generates comprehensive docstrings for code.

Capabilities:
- Generate function docstrings
- Generate class docstrings
- Generate module docstrings
- Support multiple docstring formats
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from skills.core.base_skill import (
    BaseSkill,
    SkillCategory,
    SkillContext,
    SkillResult,
    SkillStatus,
)


class DocstringFormat(Enum):
    """Supported docstring formats."""

    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    EPYTEXT = "epytext"


@dataclass
class GeneratedDocstring:
    """A generated docstring."""

    target_name: str
    target_type: str  # function, class, module
    docstring: str
    format: DocstringFormat


class DocstringGenerationSkill(BaseSkill):
    """Generate comprehensive docstrings.

    Uses LLM to analyze code and generate appropriate docstrings
    following the specified format.

    Example:
        skill = DocstringGenerationSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "def add(a, b): return a + b",
                "format": "google",
            }
        )
        result = await skill.run(context)
    """

    name = "docstring_generation"
    description = "Generate docstrings for code"
    category = SkillCategory.DOCUMENTATION
    required_tools = ["file_read"]
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute docstring generation.

        Args:
            context: Execution context with code to document

        Returns:
            SkillResult with generated docstrings
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        format_str = input_data.get("format", "google")
        doc_format = DocstringFormat(format_str)

        # Analyze code structure
        targets = self._find_documentable_items(code)

        # Generate docstrings
        docstrings = []
        for target in targets:
            docstring = self._generate_docstring(target, doc_format)
            docstrings.append(docstring)

        # Generate updated code
        updated_code = self._insert_docstrings(code, docstrings)

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "updated_code": updated_code,
                "docstrings": [self._docstring_to_dict(d) for d in docstrings],
                "count": len(docstrings),
                "format": doc_format.value,
            },
            tokens_used=0,
        )

    def _find_documentable_items(self, code: str) -> list[dict[str, Any]]:
        """Find items that need docstrings."""
        items = []
        lines = code.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                name = (
                    stripped.split("(")[0].replace("async def ", "").replace("def ", "")
                )
                items.append({"name": name, "type": "function", "line": i})
            elif stripped.startswith("class "):
                name = stripped.split("(")[0].split(":")[0].replace("class ", "")
                items.append({"name": name, "type": "class", "line": i})
        return items

    def _generate_docstring(
        self, target: dict[str, Any], doc_format: DocstringFormat
    ) -> GeneratedDocstring:
        """Generate docstring for a target."""
        # Placeholder - will use LLM
        if doc_format == DocstringFormat.GOOGLE:
            template = f'''"""Summary for {target["name"]}.

    Args:
        TODO: Add arguments

    Returns:
        TODO: Add return value
    """'''
        else:
            template = f'''"""Summary for {target["name"]}."""'''

        return GeneratedDocstring(
            target_name=target["name"],
            target_type=target["type"],
            docstring=template,
            format=doc_format,
        )

    def _insert_docstrings(
        self, code: str, docstrings: list[GeneratedDocstring]
    ) -> str:
        """Insert docstrings into code."""
        # Placeholder - will properly insert
        return code

    def _docstring_to_dict(self, docstring: GeneratedDocstring) -> dict[str, Any]:
        """Convert GeneratedDocstring to dictionary."""
        return {
            "target_name": docstring.target_name,
            "target_type": docstring.target_type,
            "docstring": docstring.docstring,
            "format": docstring.format.value,
        }
