"""Models for technician requests."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field


class TechnicianRequest(BaseModel):
    """Request from a technician (image + voice/text)."""

    image_source: Optional[Union[str, Path]] = Field(
        None,
        description="Image URL or file path"
    )
    voice_text: Optional[str] = Field(
        None,
        description="Voice description or text description"
    )
    additional_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra context (location, time, history, etc.)"
    )

    def model_post_init(self, __context: Any) -> None:
        """Validate that at least one input is provided."""
        if not self.image_source and not self.voice_text:
            raise ValueError(
                "At least one of image_source or voice_text must be provided"
            )

    def has_image(self) -> bool:
        """Check if this request includes an image."""
        return self.image_source is not None

    def has_voice(self) -> bool:
        """Check if this request includes voice/text."""
        return self.voice_text is not None
