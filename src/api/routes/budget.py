"""Budget and financial endpoints powered by JING-STEWARD."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core.orchestrator import get_orchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class PartItem(BaseModel):
    item: str
    quantity: int = 1
    unit_price: float = 0.0
    total: Optional[float] = None


class BudgetRequest(BaseModel):
    diagnosis: str = Field(..., description="Description of the problem")
    parts: Optional[List[PartItem]] = Field(None, description="List of parts")
    tools: Optional[List[str]] = Field(None, description="List of tools")
    estimated_hours: Optional[float] = Field(None, description="Estimated labor hours")
    trade: str = Field("general", description="Type of trade")
    client_name: Optional[str] = Field(None, description="Client name")
    urgency: str = Field("normal", description="Job urgency")


class FinancialSummaryRequest(BaseModel):
    budget: Dict[str, Any] = Field(..., description="Original budget")
    actual_parts_cost: float = Field(..., description="Actual parts cost")
    actual_hours: float = Field(..., description="Actual hours worked")
    amount_charged: float = Field(..., description="Final amount charged")
    client_name: str = Field("Client", description="Client name")
    job_title: Optional[str] = Field(None, description="Job title")
    extra_costs: Optional[List[Dict[str, Any]]] = Field(None, description="Extra costs")


class BudgetResponse(BaseModel):
    success: bool
    budget: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FinancialSummaryResponse(BaseModel):
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/budget/generate", response_model=BudgetResponse)
async def generate_budget(request: BudgetRequest):
    """
    Generate a professional budget for a job.
    
    Uses JING-STEWARD to calculate fair pricing with:
    - Transparent cost breakdown
    - Appropriate profit margins
    - Payment terms
    - Warranty information
    """
    try:
        orchestrator = get_orchestrator()
        
        parts = None
        if request.parts:
            parts = []
            for part in request.parts:
                part_dict = {
                    "item": part.item,
                    "quantity": part.quantity,
                    "unit_price": part.unit_price,
                    "total": part.total or (part.unit_price * part.quantity),
                }
                parts.append(part_dict)
        
        budget = await orchestrator.generate_budget(
            diagnosis=request.diagnosis,
            parts=parts,
            tools=request.tools,
            estimated_hours=request.estimated_hours,
            trade=request.trade,
            client_name=request.client_name,
            urgency=request.urgency,
        )
        
        return BudgetResponse(success=True, budget=budget, error=None)
    
    except Exception as e:
        logger.error(f"Budget generation failed: {e}", exc_info=True)
        return BudgetResponse(success=False, budget=None, error=str(e))


@router.post("/budget/summary", response_model=FinancialSummaryResponse)
async def generate_financial_summary(request: FinancialSummaryRequest):
    """
    Generate a financial summary after job completion.
    
    Uses JING-STEWARD to analyze:
    - Profitability
    - Performance metrics
    - Insights and recommendations
    - Chart data for visualization
    """
    try:
        orchestrator = get_orchestrator()
        
        summary = await orchestrator.generate_financial_summary(
            budget=request.budget,
            actual_parts_cost=request.actual_parts_cost,
            actual_hours=request.actual_hours,
            amount_charged=request.amount_charged,
            client_name=request.client_name,
            job_title=request.job_title,
            extra_costs=request.extra_costs,
        )
        
        return FinancialSummaryResponse(success=True, summary=summary, error=None)
    
    except Exception as e:
        logger.error(f"Financial summary generation failed: {e}", exc_info=True)
        return FinancialSummaryResponse(success=False, summary=None, error=str(e))
