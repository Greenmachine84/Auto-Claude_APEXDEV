"""System Designer Agent.

Detailed system design agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.
"""

from typing import Any, ClassVar

from ..base import ExecutionContext
from ..types import AgentResult, ErrorCode, ErrorResult, SuccessResult
from .base_enterprise_agent import BaseEnterpriseAgent
from .types import EnterpriseAgentType


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
