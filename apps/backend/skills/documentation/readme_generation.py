"""README generation skill.

Generates comprehensive README files.

Capabilities:
- Generate project README
- Include badges and shields
- Add installation instructions
- Document usage examples
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
class ReadmeSection:
    """A section in the README."""

    title: str
    content: str
    order: int


@dataclass
class GeneratedReadme:
    """A generated README."""

    content: str
    sections: list[ReadmeSection] = field(default_factory=list)
    badges: list[str] = field(default_factory=list)


class ReadmeGenerationSkill(BaseSkill):
    """Generate comprehensive README files.

    Analyzes project structure and generates a professional
    README with all necessary sections.

    Example:
        skill = ReadmeGenerationSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "project_name": "my-project",
                "project_path": "/path/to/project",
                "include_badges": True,
            }
        )
        result = await skill.run(context)
    """

    name = "readme_generation"
    description = "Generate README files"
    category = SkillCategory.DOCUMENTATION
    required_tools = ["file_read", "directory_list"]
    required_permissions = {"read_files", "llm_access"}
    version = "1.0.0"

    DEFAULT_SECTIONS = [
        "Overview",
        "Installation",
        "Usage",
        "Configuration",
        "API Reference",
        "Contributing",
        "License",
    ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        if "project_name" not in input_data and "project_path" not in input_data:
            return False
        return True

    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute README generation.

        Args:
            context: Execution context with project info

        Returns:
            SkillResult with generated README
        """
        input_data = context.input_data
        project_name = input_data.get("project_name", "Project")
        project_path = input_data.get("project_path")
        include_badges = input_data.get("include_badges", True)
        sections = input_data.get("sections", self.DEFAULT_SECTIONS)

        # Analyze project
        project_info = self._analyze_project(project_path)

        # Generate badges
        badges = []
        if include_badges:
            badges = self._generate_badges(project_info)

        # Generate sections
        readme_sections = []
        for i, section in enumerate(sections):
            content = self._generate_section(section, project_info)
            readme_sections.append(
                ReadmeSection(
                    title=section,
                    content=content,
                    order=i,
                )
            )

        # Combine into README
        readme = self._build_readme(project_name, badges, readme_sections)

        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "readme": readme.content,
                "sections": [s.title for s in readme.sections],
                "badges": readme.badges,
            },
            tokens_used=0,
        )

    def _analyze_project(self, project_path: str | None) -> dict[str, Any]:
        """Analyze project structure."""
        # Placeholder - will analyze actual project
        return {
            "language": "python",
            "has_tests": True,
            "has_ci": True,
        }

    def _generate_badges(self, project_info: dict[str, Any]) -> list[str]:
        """Generate badge markdown."""
        badges = []
        if project_info.get("has_ci"):
            badges.append("![CI](https://img.shields.io/badge/CI-passing-green)")
        return badges

    def _generate_section(self, section: str, project_info: dict[str, Any]) -> str:
        """Generate content for a section."""
        # Placeholder - will use LLM
        return f"TODO: Add {section} content"

    def _build_readme(
        self,
        project_name: str,
        badges: list[str],
        sections: list[ReadmeSection],
    ) -> GeneratedReadme:
        """Build complete README."""
        lines = [f"# {project_name}\n"]

        if badges:
            lines.append(" ".join(badges) + "\n")

        for section in sorted(sections, key=lambda s: s.order):
            lines.append(f"\n## {section.title}\n")
            lines.append(section.content + "\n")

        return GeneratedReadme(
            content="\n".join(lines),
            sections=sections,
            badges=badges,
        )
