"""Code translation skill.

Translates code between programming languages.

Capabilities:
- Language-to-language translation
- Preserve semantics
- Adapt to target language idioms
- Handle library mappings
"""

from dataclasses import dataclass, field
from typing import Any

from skills.core.base_skill import (
    BaseSkill,
    SkillCategory,
    SkillContext,
    SkillResult,
    SkillStatus,
)


@dataclass
class TranslationOutput:
    """Output from code translation."""

    translated_code: str
    source_language: str
    target_language: str
    notes: list[str] = field(default_factory=list)
    library_mappings: dict[str, str] = field(default_factory=dict)
    untranslatable_sections: list[str] = field(default_factory=list)


class CodeTranslationSkill(BaseSkill):
    """Translate code between programming languages.

    Uses LLM to translate code from one programming language
    to another while preserving semantics and adapting to
    target language idioms.

    Example:
        skill = CodeTranslationSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "def hello(): print('Hello')",
                "source_language": "python",
                "target_language": "javascript",
            }
        )
        result = await skill.run(context)
    """

    name = "code_translation"
    description = "Translate code between programming languages"
    category = SkillCategory.CODING
    required_tools = ["file_read", "file_write"]
    required_permissions = {"read_files", "write_files", "llm_access"}
    version = "1.0.0"

    SUPPORTED_LANGUAGES = [
        "python",
        "javascript",
        "typescript",
        "java",
        "csharp",
        "go",
        "rust",
        "cpp",
        "c",
        "ruby",
        "php",
        "swift",
        "kotlin",
    ]

    # Common library mappings between languages
    LIBRARY_MAPPINGS = {
        ("python", "javascript"): {
            "requests": "axios",
            "json": "JSON",
            "datetime": "Date",
        },
        ("javascript", "python"): {
            "axios": "requests",
            "lodash": "itertools",
        },
    }

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data:
            return False
        if not input_data.get("code", "").strip():
            return False
        source = input_data.get("source_language", "")
        target = input_data.get("target_language", "")
        if source not in self.SUPPORTED_LANGUAGES:
            return False
        if target not in self.SUPPORTED_LANGUAGES:
            return False
        if source == target:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute code translation.

        Args:
            context: Execution context with code to translate

        Returns:
            SkillResult with translated code
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        source_language = input_data.get("source_language", "python")
        target_language = input_data.get("target_language", "javascript")

        # Get library mappings
        mappings = self.LIBRARY_MAPPINGS.get((source_language, target_language), {})

        # Translate code (placeholder for LLM)
        translated = self._translate_code(
            code, source_language, target_language, mappings
        )

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "translated_code": translated.translated_code,
                "source_language": translated.source_language,
                "target_language": translated.target_language,
                "notes": translated.notes,
                "library_mappings": translated.library_mappings,
                "untranslatable_sections": translated.untranslatable_sections,
            },
            tokens_used=0,
        )

    def _translate_code(
        self,
        code: str,
        source: str,
        target: str,
        mappings: dict[str, str],
    ) -> TranslationOutput:
        """Translate code (placeholder for LLM)."""
        # Placeholder translation
        translated = f"// Translated from {source} to {target}\n{code}"

        return TranslationOutput(
            translated_code=translated,
            source_language=source,
            target_language=target,
            notes=[f"Translated from {source} to {target}"],
            library_mappings=mappings,
            untranslatable_sections=[],
        )
