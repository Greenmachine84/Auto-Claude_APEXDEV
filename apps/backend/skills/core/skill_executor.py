"""Skill execution engine with context management.

Provides:
- Single skill execution
- Skill chain execution (sequential)
- Parallel skill execution
- Context propagation
- Result aggregation
- Error handling and recovery

Example:
    executor = SkillExecutor(registry)
    
    # Single skill
    result = await executor.execute("code_generation", context)
    
    # Skill chain
    results = await executor.execute_chain(
        ["code_generation", "test_generation", "code_review"],
        context
    )
    
    # Parallel execution
    results = await executor.execute_parallel(
        ["security_review", "architecture_review"],
        context
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio
import logging

from skills.core.base_skill import BaseSkill, SkillContext, SkillResult, SkillStatus
from skills.core.skill_registry import SkillRegistry, SkillNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class ExecutionPlan:
    """Plan for executing multiple skills."""
    skill_names: List[str]
    parallel: bool = False
    stop_on_failure: bool = True
    timeout_seconds: int = 600


@dataclass
class ChainResult:
    """Result from executing a skill chain."""
    results: List[SkillResult]
    success: bool
    total_tokens: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def failed_skills(self) -> List[str]:
        """Get names of skills that failed."""
        return [
            r.skill_name for r in self.results
            if r.status in (SkillStatus.FAILED, SkillStatus.TIMEOUT)
        ]
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "results": [r.to_dict() for r in self.results],
            "success": self.success,
            "total_tokens": self.total_tokens,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failed_skills": self.failed_skills,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


class SkillExecutor:
    """Execute skills with context management.
    
    Handles skill execution with proper context propagation,
    error handling, and result aggregation.
    
    Attributes:
        registry: Skill registry for skill lookup
        default_timeout: Default execution timeout in seconds
    """
    
    def __init__(
        self,
        registry: Optional[SkillRegistry] = None,
        default_timeout: int = 300,
    ) -> None:
        """Initialize the executor.
        
        Args:
            registry: Skill registry (uses singleton if not provided)
            default_timeout: Default timeout for skill execution
        """
        self.registry = registry or SkillRegistry()
        self.default_timeout = default_timeout
        self._execution_history: List[SkillResult] = []
        self._max_history = 1000
    
    async def execute(
        self,
        skill_name: str,
        context: SkillContext,
    ) -> SkillResult:
        """Execute a single skill.
        
        Args:
            skill_name: Name of skill to execute
            context: Execution context
            
        Returns:
            SkillResult with output or error
        """
        try:
            skill = self.registry.get(skill_name)
        except SkillNotFoundError as e:
            logger.error(f"Skill not found: {skill_name}")
            return SkillResult(
                skill_name=skill_name,
                status=SkillStatus.FAILED,
                error=str(e),
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
        
        # Execute with lifecycle management
        result = await skill.run(context)
        
        # Track history
        self._add_to_history(result)
        
        return result
    
    async def execute_with_dependencies(
        self,
        skill_name: str,
        context: SkillContext,
    ) -> ChainResult:
        """Execute a skill with all its dependencies.
        
        Args:
            skill_name: Name of skill to execute
            context: Execution context
            
        Returns:
            ChainResult with all dependency results
        """
        # Resolve dependencies
        execution_order = self.registry.resolve_dependencies(skill_name)
        
        # Execute in order
        return await self.execute_chain(execution_order, context)
    
    async def execute_chain(
        self,
        skill_names: List[str],
        context: SkillContext,
        stop_on_failure: bool = True,
    ) -> ChainResult:
        """Execute skills sequentially.
        
        Results from each skill are available to subsequent skills
        through the context.
        
        Args:
            skill_names: List of skill names to execute
            context: Initial execution context
            stop_on_failure: Stop chain on first failure
            
        Returns:
            ChainResult with all results
        """
        started_at = datetime.utcnow()
        results: List[SkillResult] = []
        total_tokens = 0
        success = True
        
        # Create mutable context
        chain_context = SkillContext(
            task_id=context.task_id,
            input_data=dict(context.input_data),
            memory_context=context.memory_context,
            agent_id=context.agent_id,
            session_id=context.session_id,
            timeout_seconds=context.timeout_seconds,
            metadata=dict(context.metadata),
        )
        
        for skill_name in skill_names:
            result = await self.execute(skill_name, chain_context)
            results.append(result)
            total_tokens += result.tokens_used
            
            if not result.success:
                success = False
                if stop_on_failure:
                    logger.warning(
                        f"Chain stopped due to failure in {skill_name}"
                    )
                    break
            else:
                # Propagate output to next skill's context
                if result.output:
                    chain_context.input_data[f"{skill_name}_output"] = result.output
        
        return ChainResult(
            results=results,
            success=success,
            total_tokens=total_tokens,
            started_at=started_at,
            completed_at=datetime.utcnow(),
        )
    
    async def execute_parallel(
        self,
        skill_names: List[str],
        context: SkillContext,
    ) -> ChainResult:
        """Execute skills in parallel.
        
        All skills receive the same context and execute concurrently.
        
        Args:
            skill_names: List of skill names to execute
            context: Execution context (shared, not modified)
            
        Returns:
            ChainResult with all results
        """
        started_at = datetime.utcnow()
        
        # Create tasks for parallel execution
        tasks = [
            self.execute(skill_name, context)
            for skill_name in skill_names
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results: List[SkillResult] = []
        total_tokens = 0
        success = True
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Convert exception to failed result
                processed_results.append(SkillResult(
                    skill_name=skill_names[i],
                    status=SkillStatus.FAILED,
                    error=str(result),
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                ))
                success = False
            else:
                processed_results.append(result)
                total_tokens += result.tokens_used
                if not result.success:
                    success = False
        
        return ChainResult(
            results=processed_results,
            success=success,
            total_tokens=total_tokens,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            metadata={"parallel": True},
        )
    
    async def execute_plan(self, plan: ExecutionPlan, context: SkillContext) -> ChainResult:
        """Execute a skill execution plan.
        
        Args:
            plan: Execution plan
            context: Execution context
            
        Returns:
            ChainResult with all results
        """
        if plan.parallel:
            return await self.execute_parallel(plan.skill_names, context)
        else:
            return await self.execute_chain(
                plan.skill_names,
                context,
                stop_on_failure=plan.stop_on_failure,
            )
    
    def _add_to_history(self, result: SkillResult) -> None:
        """Add result to execution history."""
        self._execution_history.append(result)
        
        # Trim history if needed
        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]
    
    def get_history(
        self,
        skill_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[SkillResult]:
        """Get execution history.
        
        Args:
            skill_name: Filter by skill name
            limit: Maximum results to return
            
        Returns:
            List of recent results
        """
        history = self._execution_history
        
        if skill_name:
            history = [r for r in history if r.skill_name == skill_name]
        
        return history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Dictionary with execution stats
        """
        if not self._execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "total_tokens": 0,
            }
        
        total = len(self._execution_history)
        successful = sum(
            1 for r in self._execution_history if r.success
        )
        total_tokens = sum(r.tokens_used for r in self._execution_history)
        
        return {
            "total_executions": total,
            "successful_executions": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "total_tokens": total_tokens,
            "average_tokens_per_execution": total_tokens / total if total > 0 else 0,
        }
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()
    
    def __repr__(self) -> str:
        return f"SkillExecutor(registry={self.registry}, history={len(self._execution_history)})"
