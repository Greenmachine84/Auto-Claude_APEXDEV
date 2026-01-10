"""Central registry for skill discovery and registration.

Provides:
- Skill registration and deregistration
- Skill discovery by name, category, or capability
- Skill dependency resolution
- Thread-safe operations

Example:
    registry = SkillRegistry()
    registry.register(CodeGenerationSkill())

    skill = registry.get("code_generation")
    coding_skills = registry.list_by_category(SkillCategory.CODING)
"""

import logging
from threading import RLock
from typing import Optional

from skills.core.base_skill import BaseSkill, SkillCategory

logger = logging.getLogger(__name__)


class SkillNotFoundError(Exception):
    """Raised when a requested skill is not found."""

    pass


class SkillAlreadyRegisteredError(Exception):
    """Raised when attempting to register a duplicate skill."""

    pass


class SkillRegistry:
    """Central registry for skill discovery and registration.

    Thread-safe singleton registry for managing skills. Supports
    registration, discovery, and dependency resolution.

    Attributes:
        _instance: Singleton instance
        _skills: Dictionary of registered skills
        _lock: Thread lock for safe operations
    """

    _instance: Optional["SkillRegistry"] = None
    _lock = RLock()

    def __new__(cls) -> "SkillRegistry":
        """Ensure singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        """Initialize the registry."""
        if self._initialized:
            return

        self._skills: dict[str, BaseSkill] = {}
        self._categories: dict[SkillCategory, set[str]] = {
            category: set() for category in SkillCategory
        }
        self._capabilities: dict[str, set[str]] = {}
        self._initialized = True
        logger.info("SkillRegistry initialized")

    def register(self, skill: BaseSkill) -> None:
        """Register a skill.

        Args:
            skill: Skill instance to register

        Raises:
            SkillAlreadyRegisteredError: If skill name already registered
        """
        with self._lock:
            if skill.name in self._skills:
                raise SkillAlreadyRegisteredError(
                    f"Skill '{skill.name}' is already registered"
                )

            self._skills[skill.name] = skill
            self._categories[skill.category].add(skill.name)

            # Index by required tools (capabilities)
            for tool in skill.required_tools:
                if tool not in self._capabilities:
                    self._capabilities[tool] = set()
                self._capabilities[tool].add(skill.name)

            logger.debug(f"Registered skill: {skill.name}")

    def register_class(self, skill_class: type[BaseSkill]) -> None:
        """Register a skill class (instantiates automatically).

        Args:
            skill_class: Skill class to instantiate and register
        """
        skill = skill_class()
        self.register(skill)

    def unregister(self, name: str) -> BaseSkill | None:
        """Unregister a skill by name.

        Args:
            name: Skill name to unregister

        Returns:
            The unregistered skill, or None if not found
        """
        with self._lock:
            skill = self._skills.pop(name, None)
            if skill:
                self._categories[skill.category].discard(name)
                for tool in skill.required_tools:
                    if tool in self._capabilities:
                        self._capabilities[tool].discard(name)
                logger.debug(f"Unregistered skill: {name}")
            return skill

    def get(self, name: str) -> BaseSkill:
        """Get a skill by name.

        Args:
            name: Skill name

        Returns:
            The skill instance

        Raises:
            SkillNotFoundError: If skill not found
        """
        with self._lock:
            skill = self._skills.get(name)
            if skill is None:
                raise SkillNotFoundError(f"Skill '{name}' not found")
            return skill

    def get_optional(self, name: str) -> BaseSkill | None:
        """Get a skill by name, returning None if not found.

        Args:
            name: Skill name

        Returns:
            The skill instance or None
        """
        with self._lock:
            return self._skills.get(name)

    def list_all(self) -> list[BaseSkill]:
        """List all registered skills.

        Returns:
            List of all skills
        """
        with self._lock:
            return list(self._skills.values())

    def list_by_category(self, category: SkillCategory) -> list[BaseSkill]:
        """List skills by category.

        Args:
            category: Skill category

        Returns:
            List of skills in the category
        """
        with self._lock:
            names = self._categories.get(category, set())
            return [self._skills[name] for name in names]

    def find_by_capability(self, capability: str) -> list[BaseSkill]:
        """Find skills that require a specific tool/capability.

        Args:
            capability: Tool name or capability

        Returns:
            List of skills requiring the capability
        """
        with self._lock:
            names = self._capabilities.get(capability, set())
            return [self._skills[name] for name in names]

    def find_by_tools(self, tools: list[str]) -> list[BaseSkill]:
        """Find skills that use any of the specified tools.

        Args:
            tools: List of tool names

        Returns:
            List of matching skills
        """
        result_names: set[str] = set()
        with self._lock:
            for tool in tools:
                result_names.update(self._capabilities.get(tool, set()))
            return [self._skills[name] for name in result_names]

    def resolve_dependencies(self, skill_name: str) -> list[str]:
        """Resolve skill dependencies in execution order.

        Args:
            skill_name: Skill to resolve dependencies for

        Returns:
            Ordered list of skill names to execute (dependencies first)

        Raises:
            SkillNotFoundError: If skill or dependency not found
        """
        resolved: list[str] = []
        visited: set[str] = set()

        def resolve(name: str) -> None:
            if name in visited:
                return
            visited.add(name)

            skill = self.get(name)
            for dep in skill.get_dependencies():
                if dep not in self._skills:
                    raise SkillNotFoundError(
                        f"Dependency '{dep}' of skill '{name}' not found"
                    )
                resolve(dep)

            resolved.append(name)

        resolve(skill_name)
        return resolved

    def get_skill_metadata(self, name: str) -> dict:
        """Get metadata for a skill.

        Args:
            name: Skill name

        Returns:
            Dictionary with skill metadata
        """
        skill = self.get(name)
        return {
            "name": skill.name,
            "description": skill.description,
            "category": skill.category.value,
            "required_tools": skill.required_tools,
            "required_permissions": list(skill.required_permissions),
            "version": skill.version,
            "dependencies": skill.get_dependencies(),
            "execution_count": skill.execution_count,
        }

    def get_all_metadata(self) -> list[dict]:
        """Get metadata for all registered skills.

        Returns:
            List of metadata dictionaries
        """
        return [self.get_skill_metadata(name) for name in self._skills]

    def clear(self) -> None:
        """Clear all registered skills."""
        with self._lock:
            self._skills.clear()
            for category in self._categories:
                self._categories[category].clear()
            self._capabilities.clear()
            logger.info("SkillRegistry cleared")

    @property
    def count(self) -> int:
        """Number of registered skills."""
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        return name in self._skills

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        return f"SkillRegistry(skills={self.count})"
