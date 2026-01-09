"""LLM Prompts module.

Provides prompt engineering infrastructure:
- Prompt templates with variable substitution
- Fluent prompt builder
- Prompt registry for reusability
- Variable management

Part of Phase 2: LLM Architecture
"""

from .prompt_builder import PromptBuilder
from .prompt_registry import PromptRegistry
from .prompt_template import PromptTemplate, TemplateVariable
from .variables import VariableContext, VariableResolver

__all__ = [
    "PromptTemplate",
    "TemplateVariable",
    "PromptBuilder",
    "PromptRegistry",
    "VariableResolver",
    "VariableContext",
]
