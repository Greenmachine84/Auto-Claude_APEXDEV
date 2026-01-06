"""Code generation skill.

Generates code from natural language specifications using LLM.

Capabilities:
- Generate code from specs
- Support multiple languages
- Include tests if requested
- Follow coding standards
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


@dataclass
class CodeGenerationInput:
    """Input for code generation."""
    specification: str
    language: str = "python"
    style_guide: Optional[str] = None
    include_tests: bool = False
    include_docstrings: bool = True
    context_files: List[str] = field(default_factory=list)
    max_tokens: int = 4096


@dataclass
class CodeGenerationOutput:
    """Output from code generation."""
    code: str
    language: str
    file_path: Optional[str] = None
    tests: Optional[str] = None
    explanation: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class CodeGenerationSkill(BaseSkill):
    """Generate code from natural language specifications.
    
    Uses LLM to transform specifications into working code.
    Supports multiple programming languages and coding standards.
    
    Example:
        skill = CodeGenerationSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "specification": "Create a function to sort a list",
                "language": "python",
                "include_tests": True,
            }
        )
        result = await skill.run(context)
    """
    
    name = "code_generation"
    description = "Generate code from natural language specifications"
    category = SkillCategory.CODING
    required_tools = ["file_write", "file_read"]
    required_permissions = {"write_files", "llm_access"}
    version = "1.0.0"
    
    # Supported languages
    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java", "csharp",
        "go", "rust", "cpp", "c", "ruby", "php", "swift", "kotlin",
    ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "specification" not in input_data:
            return False
        if not input_data.get("specification", "").strip():
            return False
        language = input_data.get("language", "python")
        if language not in self.SUPPORTED_LANGUAGES:
            return False
        return True
    
    def get_dependencies(self) -> List[str]:
        """No dependencies."""
        return []
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for LLM function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_code",
                    "description": "Generate code based on specification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Generated code",
                            },
                            "explanation": {
                                "type": "string",
                                "description": "Explanation of the code",
                            },
                            "imports": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Required imports",
                            },
                        },
                        "required": ["code"],
                    },
                },
            }
        ]
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute code generation.
        
        Args:
            context: Execution context with specification
            
        Returns:
            SkillResult with generated code
        """
        input_data = context.input_data
        specification = input_data.get("specification", "")
        language = input_data.get("language", "python")
        include_tests = input_data.get("include_tests", False)
        include_docstrings = input_data.get("include_docstrings", True)
        
        # Build prompt for LLM
        prompt = self._build_prompt(
            specification=specification,
            language=language,
            include_tests=include_tests,
            include_docstrings=include_docstrings,
        )
        
        # TODO: Integrate with LLM module from Phase 2
        # For now, return placeholder result
        generated_code = self._placeholder_generation(
            specification, language, include_docstrings
        )
        
        output = CodeGenerationOutput(
            code=generated_code,
            language=language,
            explanation=f"Generated {language} code based on specification",
            imports=[],
            dependencies=[],
        )
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "code": output.code,
                "language": output.language,
                "explanation": output.explanation,
                "imports": output.imports,
                "dependencies": output.dependencies,
            },
            tokens_used=0,  # Will be updated when LLM integrated
        )
    
    def _build_prompt(
        self,
        specification: str,
        language: str,
        include_tests: bool,
        include_docstrings: bool,
    ) -> str:
        """Build LLM prompt for code generation."""
        parts = [
            f"Generate {language} code based on the following specification:",
            "",
            specification,
            "",
            "Requirements:",
            f"- Language: {language}",
            "- Follow best practices and coding standards",
            "- Write clean, maintainable code",
        ]
        
        if include_docstrings:
            parts.append("- Include comprehensive docstrings")
        
        if include_tests:
            parts.append("- Include unit tests")
        
        return "\n".join(parts)
    
    def _placeholder_generation(
        self,
        specification: str,
        language: str,
        include_docstrings: bool,
    ) -> str:
        """Placeholder code generation (to be replaced with LLM)."""
        if language == "python":
            code = '''"""Generated module based on specification.

{spec}
"""

def generated_function():
    """Generated function placeholder.
    
    This is a placeholder. Actual implementation will be
    generated by LLM integration.
    """
    # TODO: Implement based on specification
    pass
'''.format(spec=specification[:100])
        else:
            code = f"// Generated {language} code placeholder\n// Specification: {specification[:50]}..."
        
        return code
