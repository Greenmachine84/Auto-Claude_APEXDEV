"""README generator for documentation agent.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReadmeSection:
    """A section in a README."""

    title: str
    content: str
    order: int = 0
    subsections: list["ReadmeSection"] = field(default_factory=list)

    def to_markdown(self, level: int = 2) -> str:
        """Convert to markdown."""
        header = "#" * level
        lines = [f"{header} {self.title}", "", self.content, ""]

        for subsection in sorted(self.subsections, key=lambda x: x.order):
            lines.append(subsection.to_markdown(level + 1))

        return "\n".join(lines)


class ReadmeGenerator:
    """Generates README files from project information.

    Analyzes project structure and creates comprehensive
    README documentation.
    """

    STANDARD_SECTIONS = [
        "Description",
        "Features",
        "Installation",
        "Quick Start",
        "Usage",
        "API Reference",
        "Configuration",
        "Examples",
        "Contributing",
        "License",
    ]

    def __init__(self):
        """Initialize generator."""
        self._templates: dict[str, str] = {
            "installation_python": """
```bash
pip install {package_name}
```

Or install from source:

```bash
git clone {repo_url}
cd {package_name}
pip install -e .
```
""",
            "installation_node": """
```bash
npm install {package_name}
```

Or using yarn:

```bash
yarn add {package_name}
```
""",
            "contributing": """
Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows our coding standards and includes appropriate tests.
""",
            "license_mit": """
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
""",
        }

    def generate_structure(
        self,
        project_name: str,
        description: str,
        features: list[str] | None = None,
        language: str = "python",
    ) -> list[ReadmeSection]:
        """Generate README section structure.

        Args:
            project_name: Name of the project
            description: Project description
            features: List of features
            language: Primary programming language

        Returns:
            List of README sections
        """
        sections: list[ReadmeSection] = []

        # Description
        sections.append(
            ReadmeSection(
                title="Description",
                content=description,
                order=1,
            )
        )

        # Features
        if features:
            feature_list = "\n".join(f"- {f}" for f in features)
            sections.append(
                ReadmeSection(
                    title="Features",
                    content=feature_list,
                    order=2,
                )
            )

        # Installation
        install_template = self._templates.get(
            f"installation_{language}",
            self._templates["installation_python"],
        )
        sections.append(
            ReadmeSection(
                title="Installation",
                content=install_template.format(
                    package_name=project_name.lower().replace(" ", "-"),
                    repo_url=f"https://github.com/user/{project_name}",
                ),
                order=3,
            )
        )

        # Quick Start
        sections.append(
            ReadmeSection(
                title="Quick Start",
                content="[Add quick start guide]",
                order=4,
            )
        )

        # Usage
        sections.append(
            ReadmeSection(
                title="Usage",
                content="[Add usage examples]",
                order=5,
            )
        )

        # Contributing
        sections.append(
            ReadmeSection(
                title="Contributing",
                content=self._templates["contributing"],
                order=8,
            )
        )

        # License
        sections.append(
            ReadmeSection(
                title="License",
                content=self._templates["license_mit"],
                order=9,
            )
        )

        return sections

    def generate_markdown(
        self,
        project_name: str,
        sections: list[ReadmeSection],
        badges: list[str] | None = None,
    ) -> str:
        """Generate complete README markdown.

        Args:
            project_name: Name of the project
            sections: README sections
            badges: Optional badge markdown strings

        Returns:
            Complete README markdown
        """
        lines = [f"# {project_name}", ""]

        # Add badges
        if badges:
            lines.extend(badges)
            lines.append("")

        # Add sections
        for section in sorted(sections, key=lambda x: x.order):
            lines.append(section.to_markdown())

        return "\n".join(lines)

    def generate_badges(
        self,
        repo_owner: str,
        repo_name: str,
        language: str = "python",
    ) -> list[str]:
        """Generate standard badge markdown.

        Args:
            repo_owner: GitHub repository owner
            repo_name: Repository name
            language: Primary language

        Returns:
            List of badge markdown strings
        """
        badges = [
            f"![Build Status](https://github.com/{repo_owner}/{repo_name}/workflows/CI/badge.svg)",
            f"![License](https://img.shields.io/github/license/{repo_owner}/{repo_name})",
        ]

        if language == "python":
            badges.extend(
                [
                    f"![Python Version](https://img.shields.io/pypi/pyversions/{repo_name})",
                    f"![PyPI](https://img.shields.io/pypi/v/{repo_name})",
                ]
            )
        elif language in ("javascript", "typescript"):
            badges.extend(
                [
                    f"![npm](https://img.shields.io/npm/v/{repo_name})",
                    f"![npm downloads](https://img.shields.io/npm/dm/{repo_name})",
                ]
            )

        return badges

    def analyze_project(
        self,
        files: dict[str, str],
    ) -> dict[str, Any]:
        """Analyze project files to extract README content.

        Args:
            files: Map of file paths to contents

        Returns:
            Extracted project information
        """
        info: dict[str, Any] = {
            "name": "",
            "description": "",
            "version": "",
            "language": "python",
            "dependencies": [],
            "scripts": {},
        }

        # Check package.json (Node.js)
        if "package.json" in files:
            import json

            try:
                pkg = json.loads(files["package.json"])
                info["name"] = pkg.get("name", "")
                info["description"] = pkg.get("description", "")
                info["version"] = pkg.get("version", "")
                info["language"] = (
                    "typescript" if "typescript" in str(pkg) else "javascript"
                )
                info["dependencies"] = list(pkg.get("dependencies", {}).keys())
                info["scripts"] = pkg.get("scripts", {})
            except json.JSONDecodeError:
                pass

        # Check pyproject.toml (Python)
        if "pyproject.toml" in files:
            content = files["pyproject.toml"]
            # Basic parsing
            if 'name = "' in content:
                import re

                name_match = re.search(r'name = "([^"]+)"', content)
                if name_match:
                    info["name"] = name_match.group(1)
            info["language"] = "python"

        # Check setup.py (Python)
        if "setup.py" in files:
            info["language"] = "python"

        return info
