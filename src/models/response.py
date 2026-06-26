"""Models for JING responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.models.plan import ExecutionPlan


class ExecutionSummary(BaseModel):
    """Summary of execution metrics."""

    total_duration_ms: float = Field(..., description="Total time in milliseconds")
    planning_duration_ms: float = Field(..., description="Planning phase time")
    execution_duration_ms: float = Field(..., description="Execution phase time")
    total_cost_usd: float = Field(..., description="Total cost in USD")
    remaining_budget_usd: float = Field(..., description="Remaining budget")
    total_tasks: int = Field(..., description="Total number of tasks")
    successful_tasks: int = Field(..., description="Successfully completed tasks")
    failed_tasks: int = Field(..., description="Failed tasks")


class ConsolidatedResponse(BaseModel):
    """Unified response for the technician."""

    diagnosis: str = Field(..., description="Brief diagnosis of the problem")
    severity: str = Field(..., description="Problem severity")
    procedure_summary: str = Field(..., description="1-2 sentence procedure summary")
    key_tools: List[str] = Field(
        default_factory=list,
        description="2-3 most important tools"
    )
    part_number: Optional[str] = Field(None, description="Critical part number")
    manual_reference: Optional[str] = Field(None, description="Manual page/section")
    safety_warnings: List[str] = Field(
        default_factory=list,
        description="Any safety warnings"
    )
    estimated_cost: str = Field(..., description="Total estimated cost")
    estimated_time: str = Field(..., description="Estimated repair time")


class AgentResult(BaseModel):
    """Result from a single agent."""

    status: str = Field(..., description="success or failed")
    data: Optional[Dict[str, Any]] = Field(None, description="Agent's output data")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration_ms: Optional[float] = Field(None, description="Execution time")


class JingResponse(BaseModel):
    """Complete response from JING system."""

    execution_summary: ExecutionSummary
    plan: ExecutionPlan
    consolidated_response: ConsolidatedResponse
    agent_results: Dict[str, AgentResult] = Field(
        default_factory=dict,
        description="Results from each agent"
    )
    voice_response: Optional[Dict[str, Any]] = Field(
        None,
        description="Voice response data"
    )
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Any errors that occurred"
    )

    def is_success(self) -> bool:
        """Check if the request was successful."""
        return self.execution_summary.failed_tasks == 0

    def get_spoken_text(self) -> Optional[str]:
        """Get the spoken response text if available."""
        if self.voice_response and self.voice_response.get("status") == "success":
            data = self.voice_response.get("data", {})
            return data.get("spoken_response")
        return None
