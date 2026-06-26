"""Models for JING-SCRIBE procedure results."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ManualFound(BaseModel):
    """Information about the manual found."""

    found: bool = Field(..., description="Whether a manual was found")
    title: Optional[str] = Field(None, description="Manual name")
    manufacturer: Optional[str] = Field(None, description="Manufacturer")
    model_coverage: Optional[str] = Field(None, description="Which models this manual covers")
    source: Literal["official_manual", "certified_database", "internal_knowledge", "web_search"]
    url: Optional[str] = Field(None, description="URL if available online")
    confidence: Literal["high", "medium", "low"]


class RelevantSection(BaseModel):
    """Relevant section of the manual."""

    section_name: Optional[str] = Field(None, description="Section name")
    page_reference: Optional[str] = Field(None, description="Page number or section")
    summary: Optional[str] = Field(None, description="Brief summary")


class RepairStep(BaseModel):
    """A single step in the repair procedure."""

    step_number: int
    action: str = Field(..., description="What to do")
    details: Optional[str] = Field(None, description="Specific details")
    warnings: List[str] = Field(default_factory=list)
    tools_needed: List[str] = Field(default_factory=list)


class TechnicalSpecifications(BaseModel):
    """Technical specifications from the manual."""

    torque_values: Optional[List[str]] = None
    clearances: Optional[List[str]] = None
    pressures: Optional[List[str]] = None
    electrical_specs: Optional[List[str]] = None
    other_specs: Optional[List[str]] = None


class SpecialTool(BaseModel):
    """Special tool required for the repair."""

    tool_name: str
    part_number: Optional[str] = None
    purpose: str = Field(..., description="Why this tool is needed")
    alternative: Optional[str] = Field(None, description="Alternative if not available")


class ScribeProcedure(BaseModel):
    """Complete procedure from JING-SCRIBE."""

    manual_found: ManualFound
    relevant_section: Optional[RelevantSection] = None
    repair_procedure: List[RepairStep] = Field(..., min_length=1)
    technical_specifications: TechnicalSpecifications = Field(
        default_factory=TechnicalSpecifications
    )
    special_tools: List[SpecialTool] = Field(default_factory=list)
    safety_warnings: List[Dict[str, Any]] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    estimated_time: str = Field(..., description="Typical time for this repair")
    difficulty_level: Literal["beginner", "intermediate", "advanced"]
    knowledge_disclosure: str = Field(
        ...,
        description="Transparent disclosure about source of information"
    )
