"""Models for JING-EYE analysis results."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ObjectIdentification(BaseModel):
    """Identification of the object in the image."""

    object: str = Field(..., description="What is this object?")
    brand: Optional[str] = Field(None, description="Brand name if visible")
    model: Optional[str] = Field(None, description="Model number if visible")
    type: str = Field(..., description="Category (faucet, thermostat, etc.)")
    condition: Literal["new", "good", "worn", "damaged", "corroded"] = Field(
        ..., description="Approximate condition"
    )


class ProblemDetected(BaseModel):
    """Details about the detected problem."""

    description: str = Field(..., description="What is visibly wrong?")
    location: str = Field(..., description="Specific part/component")
    type: Literal["leak", "crack", "corrosion", "misalignment", "burn_mark", "wear", "other"] = Field(
        ..., description="Type of problem"
    )
    severity_visible: Literal["minor", "moderate", "severe"] = Field(
        ..., description="Severity of visible damage"
    )


class SafetyWarning(BaseModel):
    """Safety warning from visual analysis."""

    warning: str = Field(..., description="What is the hazard?")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Hazard severity"
    )
    action_required: str = Field(..., description="What should technician do?")


class Confidence(BaseModel):
    """Confidence level of the analysis."""

    level: Literal["high", "medium", "low"] = Field(..., description="Confidence level")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(..., description="Why this confidence level?")


class EyeAnalysis(BaseModel):
    """Complete analysis from JING-EYE."""

    object_identification: ObjectIdentification
    problem_detected: ProblemDetected
    overall_severity: Literal["minor", "moderate", "critical"]
    probable_cause: str = Field(..., description="Most likely cause")
    alternative_causes: List[str] = Field(
        default_factory=list,
        description="Other possible causes"
    )
    safety_warnings: List[SafetyWarning] = Field(default_factory=list)
    confidence: Confidence
    limitations: List[str] = Field(
        default_factory=list,
        description="What can't be determined from this image"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Immediate actions for the technician"
    )
