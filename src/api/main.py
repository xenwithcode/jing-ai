"""
JING API - FastAPI Application

This is the main FastAPI application that exposes JING functionality
via REST endpoints.

Usage:
    uvicorn src.api.main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src import __version__, PROJECT_TAGLINE
from src.api.routes.health import router as health_router
from src.api.routes.diagnose import router as diagnose_router
from src.api.routes.history import router as history_router
from src.api.routes.budget import router as budget_router
from src.api.routes.signature import router as signature_router
from src.api.routes.artisan import router as artisan_router
from src.core.orchestrator import get_orchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("=" * 70)
    logger.info("JING API Starting Up")
    logger.info("=" * 70)

    orchestrator = get_orchestrator()
    status = orchestrator.get_status()

    logger.info(f"  Version: {__version__}")
    logger.info(f"  Tagline: {PROJECT_TAGLINE}")
    logger.info(f"  Budget: ${status['budget']['remaining']:.2f} remaining")
    logger.info(f"  Agents: {len(status['agents'])} available")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info("JING API Shutting Down")

    final_status = orchestrator.get_status()
    logger.info(f"  Total cost: ${final_status['budget']['used']:.4f}")
    logger.info(f"  Remaining: ${final_status['budget']['remaining']:.2f}")
    logger.info("=" * 70)


# Create FastAPI app
app = FastAPI(
    title="JING API",
    description=PROJECT_TAGLINE,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(diagnose_router, prefix="/api/v1", tags=["diagnose"])
app.include_router(history_router, prefix="/api/v1", tags=["history"])
app.include_router(budget_router, prefix="/api/v1", tags=["budget"])
app.include_router(signature_router, prefix="/api/v1", tags=["signature"])
app.include_router(artisan_router, prefix="/api/v1", tags=["artisan"])


# Serve frontend static files
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    logger.info(f"  Frontend: serving from {frontend_dist}")
else:
    logger.warning(f"  Frontend dist not found at {frontend_dist}")

    @app.get("/")
    async def root():
        return {
            "name": "JING",
            "tagline": PROJECT_TAGLINE,
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1/diagnose",
            "note": "Frontend not built. Run: cd frontend && npm run build",
        }


if __name__ == "__main__":
    import uvicorn
    from src.utils.config import settings

    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
