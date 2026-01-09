"""Skills Framework Module.

Phase 3 of 10 - Skills, Tools & Orchestration Architecture

This module provides the skills framework for agent capabilities:
- Core skill infrastructure (base, registry, executor)
- Coding skills (generation, refactoring, explanation, translation)
- Testing skills (generation, execution, coverage)
- Review skills (code, security, architecture)
- Documentation skills (docstrings, README, API docs)
- Analysis skills (dependency, complexity, impact)

Skills are reusable capability units that agents use to accomplish tasks.

Example:
    from skills import SkillRegistry, SkillExecutor
    from skills.coding import CodeGenerationSkill

    registry = SkillRegistry()
    registry.register(CodeGenerationSkill())

    executor = SkillExecutor(registry)
    result = await executor.execute("code_generation", context)

See Also:
    - PHASE3_SKILLS_TOOLS_ORCHESTRATION_ARCHITECTURE.md
    - NAMING_ALIGNMENT_STANDARDS.md
"""

from skills.core.base_skill import BaseSkill
from skills.core.skill_config import SkillConfig
from skills.core.skill_executor import SkillExecutor
from skills.core.skill_registry import SkillRegistry
from skills.types.result_types import SkillError, SkillResult
from skills.types.skill_types import SkillCategory, SkillStatus

__all__ = [
    # Core
    "BaseSkill",
    "SkillRegistry",
    "SkillExecutor",
    "SkillConfig",
    # Types
    "SkillCategory",
    "SkillStatus",
    "SkillResult",
    "SkillError",
]

__version__ = "1.0.0"
__phase__ = 3
