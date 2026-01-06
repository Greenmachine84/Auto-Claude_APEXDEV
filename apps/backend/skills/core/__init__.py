"""Skills Core Module.

Provides the foundational infrastructure for the skills framework:
- BaseSkill: Abstract base class for all skills
- SkillRegistry: Central skill discovery and registration
- SkillExecutor: Skill execution with context management
- SkillConfig: Skill configuration and validation
"""

from skills.core.base_skill import BaseSkill
from skills.core.skill_registry import SkillRegistry
from skills.core.skill_executor import SkillExecutor
from skills.core.skill_config import SkillConfig

__all__ = [
    "BaseSkill",
    "SkillRegistry",
    "SkillExecutor",
    "SkillConfig",
]
