"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.core.orchestrator import get_orchestrator
from src.services.qwen_client import get_qwen_client

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    budget: dict
    agents: dict
    qwen_api: bool


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns the status of the JING system, including:
    - Overall status
    - Budget information
    - Agent availability
    - Qwen API connectivity
    """
    orchestrator = get_orchestrator()
    qwen_client = get_qwen_client()

    status = orchestrator.get_status()

    # Check Qwen API
    qwen_healthy = await qwen_client.health_check()

    return HealthResponse(
        status="operational" if qwen_healthy else "degraded",
        version=status["models"]["qwen-max"],
        budget=status["budget"],
        agents=status["agents"],
        qwen_api=qwen_healthy,
    )


@router.get("/status")
async def detailed_status():
    """
    Detailed status endpoint.

    Returns comprehensive information about the JING system.
    """
    orchestrator = get_orchestrator()
    return orchestrator.get_status()
