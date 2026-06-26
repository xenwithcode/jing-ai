"""Diagnosis endpoints - the main JING API."""

import time
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field

from src.core.orchestrator import get_orchestrator
from src.models.request import TechnicianRequest
from src.models.response import JingResponse
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class DiagnoseResponse(BaseModel):
    """Response from the diagnose endpoint."""

    success: bool
    data: Optional[JingResponse] = None
    error: Optional[str] = None
    duration_ms: float


class SimpleResponse(BaseModel):
    """Simplified response for quick demos."""

    success: bool
    diagnosis: Optional[str] = None
    part_number: Optional[str] = None
    tools: list[str] = Field(default_factory=list)
    estimated_cost: Optional[str] = None
    spoken_response: Optional[str] = None
    error: Optional[str] = None


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_problem(
    image: Optional[UploadFile] = File(None, description="Image of the problem"),
    voice_text: Optional[str] = Form(None, description="Voice or text description"),
    context: Optional[str] = Form(None, description="Additional context (JSON)"),
):
    """
    Diagnose a technical problem.

    This is the main JING endpoint. It accepts an image and/or voice description
    and returns a complete diagnostic with repair procedure, tools, parts, and
    voice response.

    **Input:**
    - `image`: Photo of the problem (JPEG, PNG, WebP)
    - `voice_text`: Text description of the problem
    - `context`: Additional context as JSON string

    **Output:**
    - Complete diagnosis with repair procedure
    - List of tools and parts needed
    - Voice response for hands-free operation
    - Execution metrics (time, cost)

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/diagnose" \\
      -F "image=@faucet.jpg" \\
      -F "voice_text=This Moen faucet is dripping"
    ```
    """
    start_time = time.time()

    # Validate input
    if not image and not voice_text:
        raise HTTPException(
            status_code=400,
            detail="At least one of 'image' or 'voice_text' must be provided"
        )

    try:
        # Save uploaded image if provided
        image_path = None
        if image:
            if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image type: {image.content_type}. "
                           "Supported: JPEG, PNG, WebP"
                )

            upload_dir = settings.UPLOAD_DIR
            upload_dir.mkdir(parents=True, exist_ok=True)

            timestamp = int(time.time() * 1000)
            filename = f"upload_{timestamp}_{image.filename}"
            image_path = upload_dir / filename

            with open(image_path, "wb") as f:
                content = await image.read()

                if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image too large. Max: {settings.MAX_UPLOAD_SIZE_MB}MB"
                    )

                f.write(content)

            logger.info(f"Saved uploaded image to: {image_path}")

        # Parse additional context
        additional_context = {}
        if context:
            try:
                import json
                additional_context = json.loads(context)
            except json.JSONDecodeError:
                logger.warning(f"Invalid context JSON: {context}")

        # Process with orchestrator
        orchestrator = get_orchestrator()

        result = await orchestrator.process(
            image_source=str(image_path) if image_path else None,
            voice_text=voice_text,
            additional_context=additional_context,
        )

        duration_ms = (time.time() - start_time) * 1000

        return DiagnoseResponse(
            success=True,
            data=result,
            error=None,
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error(f"Diagnosis failed: {e}", exc_info=True)
        duration_ms = (time.time() - start_time) * 1000

        return DiagnoseResponse(
            success=False,
            data=None,
            error=str(e),
            duration_ms=duration_ms,
        )


@router.post("/diagnose/simple", response_model=SimpleResponse)
async def diagnose_simple(
    image: Optional[UploadFile] = File(None),
    voice_text: Optional[str] = Form(None),
):
    """
    Simplified diagnosis endpoint.

    Returns only the essential information for quick demos or simple use cases.
    """
    if not image and not voice_text:
        raise HTTPException(
            status_code=400,
            detail="At least one of 'image' or 'voice_text' must be provided"
        )

    try:
        image_path = None
        if image:
            upload_dir = settings.UPLOAD_DIR
            upload_dir.mkdir(parents=True, exist_ok=True)

            timestamp = int(time.time() * 1000)
            filename = f"upload_{timestamp}_{image.filename}"
            image_path = upload_dir / filename

            with open(image_path, "wb") as f:
                f.write(await image.read())

        orchestrator = get_orchestrator()

        result = await orchestrator.process_simple(
            image_source=str(image_path) if image_path else None,
            voice_text=voice_text,
        )

        return SimpleResponse(
            success=True,
            diagnosis=result.get("diagnosis"),
            part_number=result.get("part_number"),
            tools=result.get("tools", []),
            estimated_cost=result.get("estimated_cost"),
            spoken_response=result.get("spoken_response"),
            error=None,
        )

    except Exception as e:
        logger.error(f"Simple diagnosis failed: {e}", exc_info=True)

        return SimpleResponse(
            success=False,
            diagnosis=None,
            part_number=None,
            tools=[],
            estimated_cost=None,
            spoken_response=None,
            error=str(e),
        )


@router.post("/diagnose/text")
async def diagnose_text_only(
    voice_text: str = Form(..., description="Text description of the problem"),
):
    """
    Text-only diagnosis endpoint.

    For cases where no image is available, just a text description.
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.process_simple(
            voice_text=voice_text,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Text diagnosis failed: {e}", exc_info=True)

        return {
            "success": False,
            "error": str(e),
        }
