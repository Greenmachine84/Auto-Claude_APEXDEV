"""Review prompt templates for code review agent.

World-Class Standards:
- Structured prompts for consistent output
- Language-aware review guidance
- Configurable review focus areas

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReviewPrompts:
    """Prompt templates for code review.
    
    Contains templates for different review scenarios.
    """
    
    # Standard file review prompt
    FILE_REVIEW_TEMPLATE: str = """You are an expert code reviewer. Analyze the following {language} code and provide detailed feedback.

File: {file_path}

```{language}
{content}
```

{diff_section}

Provide your review in the following JSON format:
{{
  "findings": [
    {{
      "id": "F001",
      "category": "security|performance|quality|style|documentation",
      "severity": "critical|high|medium|low|info",
      "message": "Description of the issue",
      "line_start": 10,
      "line_end": 12,
      "suggestion": "How to fix it"
    }}
  ],
  "suggestions": [
    {{
      "id": "S001",
      "title": "Improvement title",
      "description": "Why this would be better",
      "line_start": 15,
      "original_code": "current code",
      "suggested_code": "improved code"
    }}
  ]
}}

Focus on:
1. Security vulnerabilities and risks
2. Bugs and logic errors
3. Performance issues
4. Code quality and maintainability
5. Best practices for {language}
"""
    
    # Improvement suggestions prompt
    IMPROVEMENT_TEMPLATE: str = """Analyze the following {language} code and suggest improvements.

```{language}
{code}
```

Provide suggestions in JSON format:
{{
  "suggestions": [
    {{
      "id": "S001",
      "title": "Improvement title",
      "description": "Detailed explanation",
      "line_start": 1,
      "original_code": "current code",
      "suggested_code": "improved code",
      "category": "performance|readability|maintainability|security"
    }}
  ]
}}

Consider:
- Code clarity and readability
- Performance optimizations
- Modern {language} patterns
- Error handling
- Documentation
"""
    
    # Best practices check prompt
    BEST_PRACTICES_TEMPLATE: str = """Check the following {language} code against best practices.

```{language}
{code}
```

Provide findings in JSON format:
{{
  "findings": [
    {{
      "id": "BP001",
      "category": "best_practice",
      "severity": "medium|low|info",
      "message": "Description of the violation",
      "line_start": 1,
      "suggestion": "Recommended approach"
    }}
  ]
}}

Check for:
- SOLID principles
- DRY violations
- Proper error handling
- Input validation
- Resource management
- Naming conventions
- Documentation completeness
"""
    
    # Language-specific guidance
    LANGUAGE_GUIDANCE: Dict[str, str] = field(default_factory=lambda: {
        "python": """Python-specific guidance:
- PEP 8 style compliance
- Type hints usage
- Context managers for resources
- List/dict comprehensions where appropriate
- Proper exception handling""",
        "javascript": """JavaScript-specific guidance:
- ES6+ features usage
- Async/await patterns
- Proper error handling
- Memory leak prevention
- Event listener cleanup""",
        "typescript": """TypeScript-specific guidance:
- Proper type annotations
- Avoid 'any' type
- Interface vs type usage
- Null/undefined handling
- Generic constraints""",
        "java": """Java-specific guidance:
- SOLID principles
- Exception handling
- Resource management (try-with-resources)
- Null safety
- Effective Java patterns""",
        "go": """Go-specific guidance:
- Error handling patterns
- Goroutine safety
- Defer usage
- Interface design
- Package organization""",
        "rust": """Rust-specific guidance:
- Ownership and borrowing
- Error handling with Result/Option
- Lifetime annotations
- Trait implementations
- Unsafe code review""",
    })
    
    def build_file_review_prompt(
        self,
        file_path: str,
        content: str,
        diff: Optional[str] = None,
        language: str = "unknown",
    ) -> str:
        """Build a file review prompt.
        
        Args:
            file_path: Path to the file
            content: File content
            diff: Optional diff showing changes
            language: Programming language
            
        Returns:
            Formatted prompt string
        """
        diff_section = ""
        if diff:
            diff_section = f"\nChanges (diff):\n```diff\n{diff}\n```\n"
        
        prompt = self.FILE_REVIEW_TEMPLATE.format(
            file_path=file_path,
            content=content,
            language=language,
            diff_section=diff_section,
        )
        
        # Add language-specific guidance
        if language in self.LANGUAGE_GUIDANCE:
            prompt += f"\n\n{self.LANGUAGE_GUIDANCE[language]}"
        
        return prompt
    
    def build_improvement_prompt(
        self,
        code: str,
        language: str,
    ) -> str:
        """Build an improvement suggestions prompt."""
        prompt = self.IMPROVEMENT_TEMPLATE.format(
            code=code,
            language=language,
        )
        
        if language in self.LANGUAGE_GUIDANCE:
            prompt += f"\n\n{self.LANGUAGE_GUIDANCE[language]}"
        
        return prompt
    
    def build_best_practices_prompt(
        self,
        code: str,
        language: str,
    ) -> str:
        """Build a best practices check prompt."""
        prompt = self.BEST_PRACTICES_TEMPLATE.format(
            code=code,
            language=language,
        )
        
        if language in self.LANGUAGE_GUIDANCE:
            prompt += f"\n\n{self.LANGUAGE_GUIDANCE[language]}"
        
        return prompt


class ReviewPromptBuilder:
    """Builder for custom review prompts.
    
    Allows building complex prompts with multiple focus areas.
    """
    
    def __init__(self):
        self._focus_areas: List[str] = []
        self._language: str = "unknown"
        self._context: str = ""
        self._output_format: str = "json"
    
    def set_language(self, language: str) -> "ReviewPromptBuilder":
        """Set the programming language."""
        self._language = language
        return self
    
    def add_focus(self, focus: str) -> "ReviewPromptBuilder":
        """Add a focus area for the review."""
        self._focus_areas.append(focus)
        return self
    
    def add_context(self, context: str) -> "ReviewPromptBuilder":
        """Add additional context."""
        self._context = context
        return self
    
    def set_output_format(self, format: str) -> "ReviewPromptBuilder":
        """Set the expected output format."""
        self._output_format = format
        return self
    
    def build(self, code: str) -> str:
        """Build the final prompt."""
        focus_text = "\n".join(f"- {f}" for f in self._focus_areas) if self._focus_areas else "- General code quality"
        
        prompt = f"""Analyze the following {self._language} code.

```{self._language}
{code}
```

{self._context}

Focus on:
{focus_text}

Provide your analysis in {self._output_format} format.
"""
        return prompt
    
    def reset(self) -> "ReviewPromptBuilder":
        """Reset the builder."""
        self._focus_areas = []
        self._language = "unknown"
        self._context = ""
        self._output_format = "json"
        return self
