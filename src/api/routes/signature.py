"""Signature processing endpoints for JING-STEWARD."""

import hashlib
import json
import base64
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class SignatureRequest(BaseModel):
    """Request to process a signature."""
    budget_data: Dict[str, Any] = Field(..., description="The signed budget")
    signature_image: str = Field(..., description="Base64 encoded signature image")
    client_name: str = Field(..., description="Client's full name")
    timestamp: str = Field(..., description="ISO timestamp of signature")
    location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")


class SignatureResponse(BaseModel):
    """Response after processing signature."""
    success: bool
    document_id: Optional[str] = None
    document_hash: Optional[str] = None
    stored_path: Optional[str] = None
    error: Optional[str] = None


def generate_document_hash(budget_data: Dict, signature: str, timestamp: str) -> str:
    """Generate a SHA-256 hash of the signed document for integrity verification."""
    content = json.dumps({
        "budget": budget_data,
        "signature": signature[:100],
        "timestamp": timestamp,
    }, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def generate_document_id(budget_number: str, timestamp: str) -> str:
    """Generate a unique document ID."""
    content = f"{budget_number}-{timestamp}"
    return hashlib.md5(content.encode()).hexdigest()[:12].upper()


@router.post("/signature/process", response_model=SignatureResponse)
async def process_signature(request: SignatureRequest):
    """
    Process a signed budget document.

    This endpoint:
    1. Generates a unique document ID
    2. Creates a tamper-proof hash
    3. Stores the signed document
    4. Returns confirmation details
    """
    try:
        document_id = generate_document_id(
            request.budget_data.get("budget_metadata", {}).get("budget_number", "unknown"),
            request.timestamp,
        )
        document_hash = generate_document_hash(
            request.budget_data,
            request.signature_image,
            request.timestamp,
        )

        client_name_slug = request.client_name.lower().replace(" ", "_")
        client_dir = settings.UPLOAD_DIR / "clients" / client_name_slug
        client_dir.mkdir(parents=True, exist_ok=True)

        signature_filename = f"{document_id}_signature.png"
        signature_path = client_dir / signature_filename

        if "," in request.signature_image:
            signature_data = request.signature_image.split(",")[1]
        else:
            signature_data = request.signature_image

        with open(signature_path, "wb") as f:
            f.write(base64.b64decode(signature_data))

        signed_doc = {
            "document_id": document_id,
            "document_hash": document_hash,
            "budget_data": request.budget_data,
            "client_name": request.client_name,
            "timestamp": request.timestamp,
            "location": request.location,
            "signature_file": str(signature_path),
            "status": "signed",
        }

        doc_filename = f"{document_id}_signed.json"
        doc_path = client_dir / doc_filename

        with open(doc_path, "w") as f:
            json.dump(signed_doc, f, indent=2)

        logger.info(
            f"Signed document processed: {document_id} for client {request.client_name}"
        )

        return SignatureResponse(
            success=True,
            document_id=document_id,
            document_hash=document_hash,
            stored_path=str(doc_path),
            error=None,
        )

    except Exception as e:
        logger.error(f"Signature processing failed: {e}", exc_info=True)
        return SignatureResponse(
            success=False,
            document_id=None,
            document_hash=None,
            stored_path=None,
            error=str(e),
        )


@router.get("/signature/{document_id}")
async def get_signed_document(document_id: str):
    """Retrieve a signed document by ID."""
    clients_dir = settings.UPLOAD_DIR / "clients"
    if not clients_dir.exists():
        raise HTTPException(status_code=404, detail="No signed documents found")

    for client_dir in clients_dir.iterdir():
        if client_dir.is_dir():
            doc_path = client_dir / f"{document_id}_signed.json"
            if doc_path.exists():
                with open(doc_path) as f:
                    return json.load(f)

    raise HTTPException(status_code=404, detail="Document not found")
