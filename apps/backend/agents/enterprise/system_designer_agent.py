"""System Designer Agent.

Detailed system design agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.
"""

from typing import ClassVar, Any

from ..types import AgentResult, SuccessResult, ErrorResult, ErrorCode
from .types import EnterpriseAgentType
from ..base import AgentConfig, ExecutionContext
from .base_enterprise_agent import BaseEnterpriseAgent


class SystemDesignerAgent(BaseEnterpriseAgent):
    """Detailed system design agent.

    Responsibilities:
    - Component design
    - Interface definitions
    - Data flow design
    - Integration planning
    """

    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.PROJECT_ANALYSIS
    AGENT_CATEGORY: ClassVar[str] = "architecture"

    @classmethod
    def get_description(cls) -> str:
        return (
            "System designer agent that creates detailed component designs, "
            "defines interfaces, and plans data flows and integrations."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        self._logger.info(f"SystemDesigner executing: {context.task}")
        try:
            design = self._create_design(context)
            return SuccessResult(data=design, message="System design complete")
        except Exception as e:
            return ErrorResult(message=str(e), code=ErrorCode.EXECUTION_ERROR)

    def _create_design(self, context: ExecutionContext) -> dict[str, Any]:
        return {"status": "designed", "agent_id": self.id}
