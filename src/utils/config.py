"""
Configuration management for JING.

Uses pydantic-settings to load and validate environment variables from .env file.
Provides type-safe access to all configuration values.

Usage:
    >>> from src.utils.config import settings
    >>> print(settings.ENVIRONMENT)
    >>> print(settings.QWEN_MAX_MODEL)
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    JING configuration settings.

    All settings can be overridden via environment variables or .env file.
    Pydantic will validate types and required fields automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ═══════════════════════════════════════════════════════════════
    # APPLICATION
    # ═══════════════════════════════════════════════════════════════

    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    DEBUG: bool = Field(default=True, description="Enable debug mode")

    # ═══════════════════════════════════════════════════════════════
    # QWEN CLOUD
    # ═══════════════════════════════════════════════════════════════

    QWEN_API_KEY: str = Field(..., description="Qwen Cloud API key")

    QWEN_BASE_URL: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="Qwen Cloud API base URL",
    )

    QWEN_MAX_MODEL: str = Field(default="qwen-max", description="Model for JING-MASTER (planner)")

    QWEN_VL_MODEL: str = Field(default="qwen-vl-max", description="Model for JING-EYE (vision)")

    QWEN_PLUS_MODEL: str = Field(
        default="qwen-plus", description="Model for JING-SCRIBE and JING-KIT"
    )

    QWEN_AUDIO_MODEL: str = Field(default="qwen-audio-turbo", description="Model for JING-VOICE")

    # ═══════════════════════════════════════════════════════════════
    # API SERVER
    # ═══════════════════════════════════════════════════════════════

    API_HOST: str = Field(default="0.0.0.0", description="API server host")

    API_PORT: int = Field(default=8000, description="API server port", ge=1, le=65535)

    API_WORKERS: int = Field(default=1, description="Number of API worker processes", ge=1)

    # ═══════════════════════════════════════════════════════════════
    # VECTOR DATABASE (for RAG - manuals)
    # ═══════════════════════════════════════════════════════════════

    VECTOR_DB_URL: str = Field(
        default="http://localhost:6333", description="Vector database URL (Qdrant)"
    )

    VECTOR_DB_COLLECTION: str = Field(
        default="jing_manuals", description="Vector DB collection name for manuals"
    )

    VECTOR_DB_ENABLED: bool = Field(default=False, description="Enable vector DB for manual search")

    # ═══════════════════════════════════════════════════════════════
    # AGENT CONFIGURATION
    # ═══════════════════════════════════════════════════════════════

    MAX_CONCURRENT_AGENTS: int = Field(
        default=5, description="Maximum number of agents running concurrently", ge=1, le=20
    )

    AGENT_TIMEOUT_SECONDS: int = Field(
        default=60, description="Timeout for agent execution", ge=10, le=300
    )

    AGENT_MAX_RETRIES: int = Field(
        default=3, description="Maximum retries for failed agent calls", ge=0, le=10
    )

    # ═══════════════════════════════════════════════════════════════
    # FILE STORAGE
    # ═══════════════════════════════════════════════════════════════

    UPLOAD_DIR: Path = Field(
        default=Path("data/uploads"), description="Directory for uploaded images/audio"
    )

    MANUALS_DIR: Path = Field(
        default=Path("data/manuals"), description="Directory for technical manuals (PDFs)"
    )

    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10, description="Maximum upload file size in MB", ge=1, le=100
    )

    # ═══════════════════════════════════════════════════════════════
    # VALIDATORS
    # ═══════════════════════════════════════════════════════════════

    @field_validator("QWEN_API_KEY")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Ensure API key is not empty and has minimum length."""
        if not v or len(v.strip()) < 10:
            raise ValueError("QWEN_API_KEY must be at least 10 characters")
        return v.strip()

    @field_validator("UPLOAD_DIR", "MANUALS_DIR")
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Ensure directories exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures we only load settings once per process.
    This is important for performance in async applications.
    """
    return Settings()


# Global settings instance (import this everywhere)
settings = get_settings()


def print_config() -> None:
    """Print current configuration (for debugging)."""
    print("\n" + "=" * 60)
    print("JING Configuration")
    print("=" * 60)
    for key, value in settings.model_dump().items():
        if "API_KEY" in key:
            value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        print(f"{key:<30} {value}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_config()
