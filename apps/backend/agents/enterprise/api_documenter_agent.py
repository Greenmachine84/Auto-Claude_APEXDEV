"""API Documenter Agent.

API documentation generation agent.
Follows PHASE1_AGENT_SYSTEM_ARCHITECTURE.md specification.
"""

from typing import ClassVar, Any

from ..types import AgentResult, SuccessResult, ErrorResult, ErrorCode
from .types import EnterpriseAgentType
from ..base import ExecutionContext
from .base_enterprise_agent import BaseEnterpriseAgent


class APIDocumenterAgent(BaseEnterpriseAgent):
    """API documentation agent.

    Responsibilities:
    - OpenAPI/Swagger generation
    - API reference docs
    - Endpoint documentation
    - Example generation
    """

    AGENT_TYPE: ClassVar[EnterpriseAgentType] = EnterpriseAgentType.DOCUMENTATION
    AGENT_CATEGORY: ClassVar[str] = "documentation"

    @classmethod
    def get_description(cls) -> str:
        return (
            "API documenter agent that generates OpenAPI specs, "
            "API references, and endpoint documentation with examples."
        )

    def execute(self, context: ExecutionContext) -> AgentResult:
        self._logger.info(f"APIDocumenter executing: {context.task}")
        try:
            result = self._document_api(context)
            return SuccessResult(data=result, message="API documentation complete")
        except Exception as e:
            return ErrorResult(message=str(e), code=ErrorCode.EXECUTION_ERROR)

    def _document_api(self, context: ExecutionContext) -> dict[str, Any]:
        return {"status": "documented", "endpoints": [], "agent_id": self.id}
