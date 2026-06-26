"""Models for execution plans created by JING-MASTER."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    """A single task in the execution plan."""

    task_id: str = Field(..., description="Unique task identifier (T1, T2, etc.)")
    agent: Literal[
        "JING-EYE", "JING-SCRIBE", "JING-KIT", "JING-VOICE", "JING-STEWARD", "JING-REFEREE"
    ] = Field(..., description="Which agent handles this task")
    objective: str = Field(..., description="Clear, specific goal for this task")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="What data this task needs")
    depends_on: List[str] = Field(
        default_factory=list, description="Task IDs that must complete first"
    )
    priority: Literal["critical", "high", "normal", "low"] = Field(..., description="Task priority")
    success_criteria: str = Field(..., description="How we know this task succeeded")
    fallback: Optional[str] = Field(None, description="What to do if this task fails")


class ExecutionStrategy(BaseModel):
    """Strategy for executing the plan."""

    parallel_groups: List[List[str]] = Field(
        ..., description="Tasks in the same inner list run in parallel"
    )
    critical_path: List[str] = Field(..., description="The longest chain of dependent tasks")


class Consolidation(BaseModel):
    """How to consolidate results."""

    final_agent: str = Field(
        default="JING-VOICE", description="Which agent produces the final output"
    )
    output_format: str = Field(..., description="How to present the final response")
    key_info_to_include: List[str] = Field(..., description="Critical information to include")


class RequestAnalysis(BaseModel):
    """Analysis of the technician's request."""

    surface_request: str = Field(..., description="What the technician literally said/showed")
    actual_need: str = Field(..., description="What they ACTUALLY need")
    urgency: Literal["critical", "high", "normal", "low"] = Field(
        ..., description="How urgent is this request"
    )
    missing_context: List[str] = Field(
        default_factory=list, description="Information we need but don't have"
    )


class ExecutionPlan(BaseModel):
    """Complete execution plan from JING-MASTER."""

    request_analysis: RequestAnalysis
    tasks: List[Task] = Field(..., min_length=1, description="List of tasks to execute")
    execution_strategy: ExecutionStrategy
    consolidation: Consolidation

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_tasks_by_agent(self, agent: str) -> List[Task]:
        """Get all tasks for a specific agent."""
        return [t for t in self.tasks if t.agent == agent]

    def get_wave(self, wave_index: int) -> List[Task]:
        """Get all tasks in a specific execution wave."""
        if wave_index >= len(self.execution_strategy.parallel_groups):
            return []

        task_ids = self.execution_strategy.parallel_groups[wave_index]
        return [t for t in self.tasks if t.task_id in task_ids]
