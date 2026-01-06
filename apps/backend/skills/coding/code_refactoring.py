"""Code refactoring skill.

Refactors existing code to improve quality, readability, and maintainability.

Capabilities:
- Extract functions/methods
- Rename identifiers
- Simplify complex logic
- Apply design patterns
- Improve performance
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillCategory, SkillStatus


class RefactoringType:
    """Types of refactoring operations."""
    EXTRACT_FUNCTION = "extract_function"
    EXTRACT_CLASS = "extract_class"
    RENAME = "rename"
    SIMPLIFY = "simplify"
    INLINE = "inline"
    MOVE = "move"
    OPTIMIZE = "optimize"
    APPLY_PATTERN = "apply_pattern"


@dataclass
class RefactoringChange:
    """A single refactoring change."""
    type: str
    description: str
    before: str
    after: str
    line_start: int
    line_end: int
    file_path: Optional[str] = None


class CodeRefactoringSkill(BaseSkill):
    """Refactor existing code for improved quality.
    
    Analyzes code and suggests or applies refactoring operations
    to improve code quality, readability, and maintainability.
    
    Example:
        skill = CodeRefactoringSkill()
        context = SkillContext(
            task_id="task_123",
            input_data={
                "code": "def foo(x): return x*2",
                "refactoring_type": "rename",
                "options": {"new_name": "double_value"},
            }
        )
        result = await skill.run(context)
    """
    
    name = "code_refactoring"
    description = "Refactor code to improve quality and maintainability"
    category = SkillCategory.CODING
    required_tools = ["file_read", "file_edit"]
    required_permissions = {"read_files", "write_files", "llm_access"}
    version = "1.0.0"
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        if "code" not in input_data:
            return False
        if not input_data.get("code", "").strip():
            return False
        return True
    
    def get_dependencies(self) -> List[str]:
        """Dependencies on other skills."""
        return []  # Could depend on code_explanation for understanding
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """Execute code refactoring.
        
        Args:
            context: Execution context with code to refactor
            
        Returns:
            SkillResult with refactored code
        """
        input_data = context.input_data
        code = input_data.get("code", "")
        refactoring_type = input_data.get("refactoring_type", "simplify")
        options = input_data.get("options", {})
        
        # Analyze code and determine refactoring
        changes = self._analyze_refactoring(code, refactoring_type, options)
        
        # Apply refactoring
        refactored_code = self._apply_refactoring(code, changes)
        
        return SkillResult(
            skill_name=self.name,
            status=SkillStatus.COMPLETED,
            output={
                "original_code": code,
                "refactored_code": refactored_code,
                "changes": [self._change_to_dict(c) for c in changes],
                "refactoring_type": refactoring_type,
            },
            tokens_used=0,
        )
    
    def _analyze_refactoring(
        self,
        code: str,
        refactoring_type: str,
        options: Dict[str, Any],
    ) -> List[RefactoringChange]:
        """Analyze code and determine refactoring changes."""
        # Placeholder - will use LLM for analysis
        changes = []
        
        if refactoring_type == RefactoringType.RENAME and "new_name" in options:
            changes.append(RefactoringChange(
                type=RefactoringType.RENAME,
                description=f"Rename identifier to {options['new_name']}",
                before="",
                after="",
                line_start=1,
                line_end=1,
            ))
        
        return changes
    
    def _apply_refactoring(
        self,
        code: str,
        changes: List[RefactoringChange],
    ) -> str:
        """Apply refactoring changes to code."""
        # Placeholder - actual implementation with LLM
        return code
    
    def _change_to_dict(self, change: RefactoringChange) -> Dict[str, Any]:
        """Convert RefactoringChange to dictionary."""
        return {
            "type": change.type,
            "description": change.description,
            "before": change.before,
            "after": change.after,
            "line_start": change.line_start,
            "line_end": change.line_end,
            "file_path": change.file_path,
        }
