"""Fluent prompt builder.

Part of Phase 2: LLM Architecture
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PromptSection:
    """A section of a prompt."""

    name: str
    content: str
    priority: int = 0
    optional: bool = False


class PromptBuilder:
    """Fluent builder for constructing prompts."""

    def __init__(self):
        self._system: str | None = None
        self._sections: list[PromptSection] = []
        self._context: dict[str, str] = {}
        self._examples: list[dict[str, str]] = []
        self._instructions: list[str] = []
        self._constraints: list[str] = []
        self._output_format: str | None = None
        self._variables: dict[str, Any] = {}

    def system(self, content: str) -> "PromptBuilder":
        """Set system prompt."""
        self._system = content
        return self

    def section(
        self, name: str, content: str, priority: int = 0, optional: bool = False
    ) -> "PromptBuilder":
        """Add a named section."""
        self._sections.append(
            PromptSection(
                name=name, content=content, priority=priority, optional=optional
            )
        )
        return self

    def context(self, key: str, value: str) -> "PromptBuilder":
        """Add context information."""
        self._context[key] = value
        return self

    def example(self, user: str, assistant: str) -> "PromptBuilder":
        """Add a few-shot example."""
        self._examples.append({"user": user, "assistant": assistant})
        return self

    def instruction(self, text: str) -> "PromptBuilder":
        """Add an instruction."""
        self._instructions.append(text)
        return self

    def constraint(self, text: str) -> "PromptBuilder":
        """Add a constraint."""
        self._constraints.append(text)
        return self

    def output_format(self, format_spec: str) -> "PromptBuilder":
        """Set expected output format."""
        self._output_format = format_spec
        return self

    def variable(self, name: str, value: Any) -> "PromptBuilder":
        """Set a variable value."""
        self._variables[name] = value
        return self

    def build(self) -> str:
        """Build the final prompt."""
        parts = []

        if self._system:
            parts.append(self._system)

        # Context section
        if self._context:
            context_parts = ["## Context"]
            for key, value in self._context.items():
                context_parts.append(f"**{key}**: {value}")
            parts.append("\n".join(context_parts))

        # Sorted sections
        sorted_sections = sorted(self._sections, key=lambda s: s.priority, reverse=True)
        for section in sorted_sections:
            parts.append(f"## {section.name}\n{section.content}")

        # Instructions
        if self._instructions:
            parts.append("## Instructions")
            for i, inst in enumerate(self._instructions, 1):
                parts.append(f"{i}. {inst}")

        # Constraints
        if self._constraints:
            parts.append("## Constraints")
            for constraint in self._constraints:
                parts.append(f"- {constraint}")

        # Examples
        if self._examples:
            parts.append("## Examples")
            for ex in self._examples:
                parts.append(f"User: {ex['user']}")
                parts.append(f"Assistant: {ex['assistant']}")
                parts.append("")

        # Output format
        if self._output_format:
            parts.append(f"## Expected Output Format\n{self._output_format}")

        prompt = "\n\n".join(parts)

        # Variable substitution
        for name, value in self._variables.items():
            prompt = prompt.replace(f"{{{{{name}}}}}", str(value))

        return prompt

    def build_messages(self) -> list[dict[str, str]]:
        """Build as chat messages."""
        messages = []

        if self._system:
            messages.append({"role": "system", "content": self._system})

        for example in self._examples:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})

        # Build user content from remaining parts
        user_parts = []
        if self._context:
            for key, value in self._context.items():
                user_parts.append(f"{key}: {value}")

        if self._instructions:
            user_parts.append("Instructions:")
            for inst in self._instructions:
                user_parts.append(f"- {inst}")

        if user_parts:
            messages.append({"role": "user", "content": "\n".join(user_parts)})

        return messages
