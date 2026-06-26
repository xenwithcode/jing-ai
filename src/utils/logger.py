"""
Logging configuration for JING.

Uses loguru for powerful, flexible logging with:
- Colored output in development
- JSON format in production
- File rotation
- Context-aware logging (module, function, line)
- Async-friendly

Usage:
    >>> from src.utils.logger import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("JING is starting...")
    >>> logger.debug("Debug info", extra_data={"key": "value"})
    >>> logger.error("Something went wrong", exc_info=True)
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from src.utils.config import settings


def setup_logger() -> None:
    """
    Configure loguru with appropriate settings based on environment.

    Development:
    - Colored console output
    - Human-readable format
    - DEBUG level

    Production:
    - JSON format (parseable by log aggregators)
    - File rotation
    - INFO level or higher
    """

    # Remove default logger
    logger.remove()

    # ═══════════════════════════════════════════════════════════════
    # CONSOLE OUTPUT
    # ═══════════════════════════════════════════════════════════════

    if settings.ENVIRONMENT == "production":
        # JSON format for production (parseable by Datadog, ELK, etc.)
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level=settings.LOG_LEVEL,
            serialize=True,  # JSON output
            colorize=False,
        )
    else:
        # Human-readable format for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        logger.add(
            sys.stderr,
            format=log_format,
            level=settings.LOG_LEVEL,
            colorize=True,
            backtrace=True,  # Show full traceback
            diagnose=True,   # Show variable values in traceback
        )

    # ═══════════════════════════════════════════════════════════════
    # FILE OUTPUT (optional, for debugging)
    # ═══════════════════════════════════════════════════════════════

    if settings.DEBUG:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Main log file (all levels)
        logger.add(
            log_dir / "jing.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",      # Rotate at 10 MB
            retention="7 days",    # Keep logs for 7 days
            compression="zip",     # Compress old logs
            enqueue=True,          # Thread-safe
            backtrace=True,
            diagnose=True,
        )

        # Error log file (ERROR and above only)
        logger.add(
            log_dir / "jing_error.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Logger instance bound to the given name

    Usage:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process")
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_request(request_id: str, method: str, path: str, status_code: int, duration_ms: float) -> None:
    """
    Log HTTP request in a structured way.

    Args:
        request_id: Unique request identifier
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
    """
    logger.bind(
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
    ).info(f"{method} {path} - {status_code} ({duration_ms:.2f}ms)")


def log_agent_execution(agent_name: str, task_id: str, status: str, duration_ms: float) -> None:
    """
    Log agent execution in a structured way.

    Args:
        agent_name: Name of the agent (e.g., "JING-EYE")
        task_id: Task identifier
        status: Execution status (success, failed, timeout)
        duration_ms: Execution duration in milliseconds
    """
    logger.bind(
        agent_name=agent_name,
        task_id=task_id,
        status=status,
        duration_ms=duration_ms,
    ).info(f"Agent {agent_name} executed task {task_id}: {status} ({duration_ms:.2f}ms)")


def log_api_call(model: str, tokens_in: int, tokens_out: int, cost_usd: float, duration_ms: float) -> None:
    """
    Log Qwen API call with cost tracking.

    Args:
        model: Model name (e.g., "qwen-max")
        tokens_in: Input tokens
        tokens_out: Output tokens
        cost_usd: Cost in USD
        duration_ms: API call duration in milliseconds
    """
    logger.bind(
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost_usd,
        duration_ms=duration_ms,
    ).info(f"API call to {model}: {tokens_in} in / {tokens_out} out tokens, ${cost_usd:.4f} ({duration_ms:.2f}ms)")


# Initialize logger on module import
setup_logger()


if __name__ == "__main__":
    # Test logging
    test_logger = get_logger(__name__)

    test_logger.debug("This is a debug message")
    test_logger.info("JING is starting up...")
    test_logger.warning("This is a warning")
    test_logger.error("This is an error")

    # Test structured logging
    log_request(
        request_id="req_123",
        method="POST",
        path="/api/v1/diagnose",
        status_code=200,
        duration_ms=1234.56,
    )

    log_agent_execution(
        agent_name="JING-EYE",
        task_id="T1",
        status="success",
        duration_ms=567.89,
    )

    log_api_call(
        model="qwen-vl-max",
        tokens_in=1500,
        tokens_out=300,
        cost_usd=0.0234,
        duration_ms=2345.67,
    )

    # Test exception logging
    try:
        1 / 0
    except ZeroDivisionError:
        test_logger.error("Division by zero occurred", exc_info=True)
