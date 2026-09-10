"""Mindner Backend Application Entry Point.

FastAPI application with lifespan startup database initialization,
structured logging, CORS middleware, and modular v1 API routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api import api_router
from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.database.init_db import init_database

# Initialize structured logging
setup_logging(settings.LOG_LEVEL)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: handles startup and shutdown hooks."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.ENVIRONMENT}] environment...")
    
    # Initialize and inspect database tables
    try:
        init_database()
    except Exception as e:
        logger.error(f"Database initialization error on startup: {e}")

    logger.info(f"{settings.APP_NAME} initialized successfully. API Prefix: {settings.API_PREFIX}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_application() -> FastAPI:
    """Application factory for FastAPI instance."""
    app = FastAPI(
        title=f"{settings.APP_NAME} Caregiver Platform API",
        description="Backend API for AI-powered dementia assistance, cognitive assessment, and caregiver coordination.",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include centralized API routers under /api/v1
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Mount static frontend directory if available
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles

    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount("/frontend", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

        @app.get("/home.html", include_in_schema=False)
        def home_alias():
            """Serve the canonical home page at the short URL used by game redirects."""
            return FileResponse(frontend_dir / "home.html")

    # Root endpoint
    @app.get("/", tags=["Root"], summary="Root service status")
    def root_ping():
        return {
            "app": settings.APP_NAME,
            "version": "1.0.0",
            "status": "online",
            "frontend": "/frontend/home.html",
            "docs": f"{settings.API_PREFIX}/docs",
            "health": f"{settings.API_PREFIX}/health",
        }

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=(settings.ENVIRONMENT == "development"),
    )
