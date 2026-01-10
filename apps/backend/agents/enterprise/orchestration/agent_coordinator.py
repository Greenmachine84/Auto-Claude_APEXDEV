"""Agent coordinator for orchestration.

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CoordinationResult:
    """Result of agent coordination."""

    success: bool = True
    agent_results: dict[str, Any] = field(default_factory=dict)
    failed_agents: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    coordination_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "agent_results": self.agent_results,
            "failed_agents": self.failed_agents,
            "execution_time": self.execution_time,
            "coordination_id": self.coordination_id,
        }


class AgentCoordinator:
    """Coordinates multiple agent executions.

    Handles parallel and sequential execution,
    dependency resolution, and failure handling.
    """

    def __init__(self):
        """Initialize coordinator."""
        self._coordination_count = 0

    async def coordinate_parallel(
        self,
        agents: dict[str, Any],  # agent_id -> agent
        context: dict[str, Any],
        timeout: float = 60.0,
    ) -> CoordinationResult:
        """Coordinate agents in parallel.

        Args:
            agents: Map of agent ID to agent
            context: Shared context for all agents
            timeout: Maximum execution time

        Returns:
            Coordination result
        """
        self._coordination_count += 1
        start_time = datetime.now()

        result = CoordinationResult(coordination_id=f"coord_{self._coordination_count}")

        # Create tasks for all agents
        tasks = {
            agent_id: asyncio.create_task(agent.execute(context))
            for agent_id, agent in agents.items()
        }

        try:
            # Wait for all tasks with timeout
            done, pending = await asyncio.wait(
                tasks.values(),
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED,
            )

            # Collect results
            for agent_id, task in tasks.items():
                if task in done:
                    try:
                        result.agent_results[agent_id] = task.result()
                    except Exception as e:
                        result.agent_results[agent_id] = {"error": str(e)}
                        result.failed_agents.append(agent_id)
                else:
                    # Task timed out
                    task.cancel()
                    result.agent_results[agent_id] = {"error": "timeout"}
                    result.failed_agents.append(agent_id)

        except Exception as e:
            result.success = False
            result.agent_results["error"] = str(e)

        result.success = len(result.failed_agents) == 0
        result.execution_time = (datetime.now() - start_time).total_seconds()

        return result

    async def coordinate_sequential(
        self,
        agents: list[tuple],  # [(agent_id, agent), ...]
        context: dict[str, Any],
        stop_on_failure: bool = True,
    ) -> CoordinationResult:
        """Coordinate agents sequentially.

        Args:
            agents: Ordered list of (agent_id, agent) tuples
            context: Initial context (modified by each agent)
            stop_on_failure: Whether to stop on first failure

        Returns:
            Coordination result
        """
        self._coordination_count += 1
        start_time = datetime.now()

        result = CoordinationResult(coordination_id=f"coord_{self._coordination_count}")

        current_context = context.copy()

        for agent_id, agent in agents:
            try:
                agent_result = await agent.execute(current_context)
                result.agent_results[agent_id] = agent_result

                # Update context with result
                current_context[f"{agent_id}_result"] = agent_result

            except Exception as e:
                result.agent_results[agent_id] = {"error": str(e)}
                result.failed_agents.append(agent_id)

                if stop_on_failure:
                    break

        result.success = len(result.failed_agents) == 0
        result.execution_time = (datetime.now() - start_time).total_seconds()

        return result

    async def coordinate_with_dependencies(
        self,
        agents: dict[str, Any],  # agent_id -> agent
        dependencies: dict[str, list[str]],  # agent_id -> [dependency_ids]
        context: dict[str, Any],
    ) -> CoordinationResult:
        """Coordinate agents with dependency resolution.

        Args:
            agents: Map of agent ID to agent
            dependencies: Map of agent ID to dependency IDs
            context: Shared context

        Returns:
            Coordination result
        """
        self._coordination_count += 1
        start_time = datetime.now()

        result = CoordinationResult(coordination_id=f"coord_{self._coordination_count}")

        # Build execution order
        execution_order = self._topological_sort(agents.keys(), dependencies)

        if not execution_order:
            result.success = False
            result.agent_results["error"] = "Circular dependency detected"
            return result

        current_context = context.copy()

        for agent_id in execution_order:
            agent = agents.get(agent_id)
            if not agent:
                continue

            try:
                agent_result = await agent.execute(current_context)
                result.agent_results[agent_id] = agent_result
                current_context[f"{agent_id}_result"] = agent_result
            except Exception as e:
                result.agent_results[agent_id] = {"error": str(e)}
                result.failed_agents.append(agent_id)

        result.success = len(result.failed_agents) == 0
        result.execution_time = (datetime.now() - start_time).total_seconds()

        return result

    def _topological_sort(
        self,
        nodes: Any,
        dependencies: dict[str, list[str]],
    ) -> list[str] | None:
        """Topological sort for dependency resolution."""
        result: list[str] = []
        visited: set[str] = set()
        temp_visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in temp_visited:
                return False  # Cycle detected
            if node in visited:
                return True

            temp_visited.add(node)

            for dep in dependencies.get(node, []):
                if not visit(dep):
                    return False

            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
            return True

        for node in nodes:
            if node not in visited:
                if not visit(node):
                    return None  # Cycle detected

        return result

    def select_agents(
        self,
        available_agents: dict[str, Any],
        required_capabilities: list[str],
    ) -> list[str]:
        """Select agents based on required capabilities.

        Args:
            available_agents: Map of agent ID to agent
            required_capabilities: List of required capability names

        Returns:
            List of agent IDs that match requirements
        """
        selected: list[str] = []

        for agent_id, agent in available_agents.items():
            agent_caps = {cap.value for cap in getattr(agent, "capabilities", [])}
            if any(cap in agent_caps for cap in required_capabilities):
                selected.append(agent_id)

        return selected
