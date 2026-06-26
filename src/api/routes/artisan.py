"""Artisan Dashboard endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from src.services.memory import memory_service
from src.agents.steward import StewardAgent

router = APIRouter()


class StatusUpdate(BaseModel):
    status: str


class SeedRequest(BaseModel):
    trade: str = "plumber"


@router.get("/artisan/dashboard")
async def get_dashboard(trade: Optional[str] = Query(None)):
    """Get aggregate dashboard statistics for the artisan."""
    stats = memory_service.get_dashboard_stats(trade=trade)
    return {"success": True, "data": stats}


@router.get("/artisan/jobs")
async def get_jobs(
    trade: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """Get all jobs, optionally filtered by trade and/or status."""
    jobs = memory_service.get_all_jobs(trade=trade, status=status)
    stats = memory_service.get_dashboard_stats(trade=trade)
    return {
        "success": True,
        "data": {
            "jobs": jobs,
            "total": len(jobs),
            "stats": stats,
        },
    }


@router.patch("/artisan/jobs/{job_id}/status")
async def update_job_status(job_id: str, body: StatusUpdate):
    """Update the status of a job."""
    valid = {"pending", "in-progress", "completed"}
    if body.status not in valid:
        raise HTTPException(
            status_code=400, detail=f"Status must be one of: {', '.join(sorted(valid))}"
        )

    job = memory_service.update_job_status(job_id, body.status)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"success": True, "data": job}


@router.get("/artisan/steward-suggestion")
async def get_steward_suggestion(trade: Optional[str] = Query(None)):
    """Get a financial suggestion from the JING-STEWARD agent based on dashboard data."""
    stats = memory_service.get_dashboard_stats(trade=trade)
    jobs = memory_service.get_all_jobs(trade=trade)

    steward = StewardAgent()

    context = f"Artisan dashboard overview:\n"
    context += f"- Total jobs: {stats['total_jobs']}\n"
    context += f"- Completed: {stats['completed_jobs']}\n"
    context += f"- In progress: {stats['in_progress_jobs']}\n"
    context += f"- Pending: {stats['pending_jobs']}\n"
    context += f"- Total revenue: ${stats['total_revenue']}\n"
    context += f"- Total profit: ${stats['total_profit']}\n"
    context += f"- Average profit per job: ${stats['average_profit']}\n"
    context += f"- Average grade: {stats['average_grade']}\n"

    if jobs:
        grades = [j.get("grade", "C") for j in jobs if j.get("status") == "completed"]
        context += f"- Recent grades: {', '.join(grades[-10:])}\n"

    try:
        prompt = f"""Based on this artisan's business data, provide ONE actionable financial suggestion to improve their business. Be specific and practical.

{context}

Respond in English with this JSON format:
{{"suggestion": "the suggestion text", "reason": "why this helps", "action": "concrete next step", "potential_impact": "expected outcome"}}"""
        result = await steward.call_qwen_json(
            model=steward.model,
            user_message=prompt,
            system="You are a financial advisor expert for tradespeople. Respond ONLY with JSON.",
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {
            "success": True,
            "data": {
                "suggestion": "Consider increasing your hourly rate for high-demand jobs.",
                "reason": "Your current margins suggest you could charge more without losing clients.",
                "action": "Review your last 5 quotes and adjust the rate by 10-15%.",
                "potential_impact": "You could increase your monthly net profit by up to 20%.",
            },
        }


@router.post("/artisan/seed-demo")
async def seed_demo_data(body: SeedRequest):
    """Seed demo job data for a specific trade (hackathon demo use)."""
    count = memory_service.seed_demo_data(body.trade)
    if count == 0:
        return {
            "success": True,
            "message": f"Demo data already exists for {body.trade}",
            "seeded": 0,
        }
    return {
        "success": True,
        "message": f"Seeded {count} demo jobs for {body.trade}",
        "seeded": count,
    }
