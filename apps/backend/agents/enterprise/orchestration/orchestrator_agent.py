"""Orchestrator Agent for coordinating enterprise agents.

World-Class Standards:
- Multi-agent coordination
- Pipeline management
- Result aggregation
- LLM-agnostic design

Phase 7 Implementation: Enterprise Agents Architecture
Reference: PHASE7_ENTERPRISE_AGENTS_ARCHITECTURE.md
"""
from typing import Any, ClassVar, Dict, List, Optional
import asyncio
import json

from ..base_enterprise_agent import BaseEnterpriseAgent, LLMRouter
from ..config import AgentCapability, EnterpriseAgentConfig
from ..types import EnterpriseAgentType, PipelineResult
from .agent_coordinator import AgentCoordinator, CoordinationResult
from .result_aggregator import ResultAggregator
from .pipeline_manager import PipelineManager, Pipeline


class OrchestratorAgent(BaseEnterpriseAgent):
    """Agent for orchestrating multiple enterprise agents.
    
    Provides orchestration capabilities:
    - Coordinate agent execution
    - Manage execution pipelines
    - Aggregate results
    - Handle failures and retries
    
    Attributes:
        coordinator: Agent coordination utility
        aggregator: Result aggregation utility
        pipeline_manager: Pipeline execution manager
    """
    
    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.ORCHESTRATOR
    AGENT_CATEGORY: ClassVar[str] = "orchestration"
    
    DEFAULT_SYSTEM_PROMPT: ClassVar[str] = """You are an expert system orchestrator with deep knowledge of:
1. Multi-agent coordination patterns
2. Pipeline design and execution
3. Error handling and recovery
4. Result synthesis and aggregation
5. Workflow optimization

Coordinate agents efficiently to achieve complex goals.
Handle failures gracefully with appropriate fallbacks.
Synthesize results into coherent outputs."""
    
    def __init__(
        self,
        config: EnterpriseAgentConfig,
        llm_router: Optional[LLMRouter] = None,
    ):
        """Initialize the orchestrator agent."""
        super().__init__(config, llm_router)
        
        # Add orchestration capability
        self.add_capability(AgentCapability.COLLABORATION)
        
        # Initialize components
        self.coordinator = AgentCoordinator()
        self.aggregator = ResultAggregator()
        self.pipeline_manager = PipelineManager()
        
        # Registered agents
        self._agents: Dict[str, BaseEnterpriseAgent] = {}
    
    @classmethod
    def get_description(cls) -> str:
        """Get agent description."""
        return (
            "Orchestrator that coordinates multiple enterprise agents, "
            "manages execution pipelines, and aggregates results. "
            "Provides fault-tolerant multi-agent workflows."
        )
    
    def register_agent(
        self,
        agent_id: str,
        agent: BaseEnterpriseAgent,
    ) -> None:
        """Register an agent for orchestration.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance to register
        """
        self._agents[agent_id] = agent
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        self._agents.pop(agent_id, None)
    
    def get_agent(self, agent_id: str) -> Optional[BaseEnterpriseAgent]:
        """Get a registered agent by ID."""
        return self._agents.get(agent_id)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration based on context.
        
        Args:
            context: Must contain 'task' or 'pipeline'
            
        Returns:
            Orchestration results
        """
        if "pipeline" in context:
            return await self.run_pipeline(
                pipeline_id=context["pipeline"],
                context=context.get("pipeline_context", {}),
            )
        
        if "agents" in context and "task" in context:
            return await self.coordinate_agents(
                agent_ids=context["agents"],
                task=context["task"],
            )
        
        return {
            "status": "error",
            "message": "Context must contain 'pipeline' or ('agents' and 'task')",
        }
    
    async def coordinate_agents(
        self,
        agent_ids: List[str],
        task: Dict[str, Any],
        parallel: bool = True,
    ) -> Dict[str, Any]:
        """Coordinate multiple agents on a task.
        
        Args:
            agent_ids: IDs of agents to coordinate
            task: Task context for agents
            parallel: Whether to run agents in parallel
            
        Returns:
            Coordination results
        """
        agents = [self._agents[aid] for aid in agent_ids if aid in self._agents]
        
        if not agents:
            return {
                "status": "error",
                "message": "No valid agents found",
            }
        
        if parallel:
            results = await asyncio.gather(
                *[agent.execute(task) for agent in agents],
                return_exceptions=True,
            )
        else:
            results = []
            for agent in agents:
                try:
                    result = await agent.execute(task)
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        
        # Aggregate results
        aggregated = self.aggregator.aggregate([
            {"agent_id": aid, "result": r}
            for aid, r in zip(agent_ids, results)
        ])
        
        return {
            "status": "success",
            "agent_count": len(agents),
            "results": aggregated.to_dict(),
        }
    
    async def run_pipeline(
        self,
        pipeline_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run a registered pipeline.
        
        Args:
            pipeline_id: ID of pipeline to run
            context: Initial context for pipeline
            
        Returns:
            Pipeline execution results
        """
        pipeline = self.pipeline_manager.get_pipeline(pipeline_id)
        
        if not pipeline:
            return {
                "status": "error",
                "message": f"Pipeline '{pipeline_id}' not found",
            }
        
        result = await self.pipeline_manager.execute(
            pipeline=pipeline,
            context=context,
            agents=self._agents,
        )
        
        return {
            "status": "success" if result.success else "failed",
            "pipeline_id": pipeline_id,
            "stages_completed": result.stages_completed,
            "stage_results": result.stage_results,
            "final_output": result.final_output,
            "errors": result.errors,
        }
    
    async def create_dynamic_pipeline(
        self,
        goal: str,
    ) -> Pipeline:
        """Create a pipeline dynamically based on goal.
        
        Args:
            goal: High-level goal description
            
        Returns:
            Generated pipeline
        """
        available_agents = list(self._agents.keys())
        
        prompt = f"""Create an execution pipeline for this goal.

Goal: {goal}

Available Agents: {available_agents}

Provide pipeline in JSON format:
{{
  "pipeline_id": "unique_id",
  "name": "Pipeline name",
  "description": "What this pipeline does",
  "stages": [
    {{
      "stage_id": "stage_1",
      "name": "Stage name",
      "agent_id": "agent to use",
      "action": "method to call",
      "depends_on": [],
      "retry_count": 3,
      "timeout": 60
    }}
  ]
}}

Design an efficient pipeline with proper dependencies.
"""
        
        response = await self.complete(prompt)
        
        try:
            data = json.loads(response)
            pipeline = self.pipeline_manager.create_pipeline(
                pipeline_id=data.get("pipeline_id", f"dynamic_{goal[:20]}"),
                name=data.get("name", "Dynamic Pipeline"),
                description=data.get("description", goal),
                stages=data.get("stages", []),
            )
            return pipeline
        except json.JSONDecodeError:
            # Create a simple sequential pipeline
            return self.pipeline_manager.create_pipeline(
                pipeline_id=f"dynamic_{goal[:20]}",
                name="Dynamic Pipeline",
                description=goal,
                stages=[{
                    "stage_id": "stage_1",
                    "name": "Execute",
                    "agent_id": available_agents[0] if available_agents else "default",
                    "action": "execute",
                    "depends_on": [],
                }],
            )
    
    async def synthesize_results(
        self,
        results: List[Dict[str, Any]],
    ) -> str:
        """Synthesize multiple agent results into coherent output.
        
        Args:
            results: Results from multiple agents
            
        Returns:
            Synthesized output
        """
        prompt = f"""Synthesize these agent results into a coherent summary.

Results:
{json.dumps(results, indent=2, default=str)}

Provide a clear, actionable synthesis that:
1. Highlights key findings from each agent
2. Identifies patterns and correlations
3. Resolves any conflicts
4. Provides prioritized recommendations
"""
        
        return await self.complete(prompt)
    
    def get_agent_capabilities(
        self,
    ) -> Dict[str, List[str]]:
        """Get capabilities of all registered agents.
        
        Returns:
            Map of agent ID to capabilities
        """
        return {
            agent_id: [cap.value for cap in agent.capabilities]
            for agent_id, agent in self._agents.items()
        }
