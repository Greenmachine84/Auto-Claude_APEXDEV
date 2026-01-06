"""Documentation Agent.

Documentation generation agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.
"""

from typing import ClassVar, Any

from ..types import AgentType, AgentResult, SuccessResult, ErrorResult, ErrorCode
from ..base import ExecutionContext
from .base_enterprise_agent import BaseEnterpriseAgent


class DocumentationAgent(BaseEnterpriseAgent):
    """Documentation generation agent.

    Responsibilities:
    - Code documentation
    - README generation
    - Architecture documentation
    - User guides
    """

    AGENT_TYPE: ClassVar[AgentType] = AgentType.DOCUMENTATION
    AGENT_CATEGORY: ClassVar[str] = "documentation"

    @classmethod
    def get_description(cls) -> str:
        return (
            "Documentation agent that generates code documentation, "
            "READMEs, architecture docs, and user guides."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        self._logger.info(f"Documentation executing: {context.task}")
        try:
            result = self._generate_docs(context)
            return SuccessResult(data=result, message="Documentation complete")
        except Exception as e:
            return ErrorResult(message=str(e), code=ErrorCode.EXECUTION_ERROR)

    def _generate_docs(self, context: ExecutionContext) -> dict[str, Any]:
        return {"status": "generated", "docs_created": [], "agent_id": self.id}
