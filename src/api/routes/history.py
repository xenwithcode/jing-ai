"""History endpoints backed by persistent memory."""

from fastapi import APIRouter, HTTPException
from src.services.memory import memory_service

router = APIRouter()


@router.get("/history")
async def get_history(limit: int = 20, client_name: str | None = None):
    """
    Get history of past diagnoses and jobs.
    """
    from pathlib import Path
    import json

    jobs_file = Path("data/memory/jobs.json")
    if not jobs_file.exists():
        return {"history": []}

    try:
        jobs = json.loads(jobs_file.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {"history": []}

    if client_name:
        jobs = [j for j in jobs if j.get("client_name", "").lower() == client_name.lower()]

    jobs.sort(key=lambda j: j.get("date", ""), reverse=True)

    return {
        "history": jobs[:limit],
        "total": len(jobs),
    }


@router.get("/history/{request_id}")
async def get_request(request_id: str):
    """
    Get a specific past request by ID.
    """
    from pathlib import Path
    import json

    jobs_file = Path("data/memory/jobs.json")
    if not jobs_file.exists():
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")

    try:
        jobs = json.loads(jobs_file.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")

    for job in jobs:
        if job.get("job_id") == request_id:
            return {"data": job}

    raise HTTPException(status_code=404, detail=f"Request {request_id} not found")


@router.get("/clients")
async def get_clients():
    """Get all known clients with their history."""
    from pathlib import Path
    import json

    clients_file = Path("data/memory/clients.json")
    if not clients_file.exists():
        return {"clients": []}

    try:
        clients = json.loads(clients_file.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {"clients": []}

    return {"clients": clients}


@router.get("/clients/{client_name}")
async def get_client_detail(client_name: str):
    """Get detailed history for a specific client."""
    history = memory_service.get_client_history(client_name)
    if not history["exists"]:
        raise HTTPException(status_code=404, detail=f"Client {client_name} not found")
    return history
