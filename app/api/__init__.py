"""API router registration module.

Aggregates all domain routers into a centralized router under /api/v1.
"""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.patients import router as patients_router
from app.api.caregivers import router as caregivers_router
from app.api.games import router as games_router
from app.api.sessions import router as sessions_router
from app.api.progress import router as progress_router
from app.api.analytics import router as analytics_router
from app.api.adaptive import router as adaptive_router
from app.api.recommendations import router as recommendations_router
from app.api.alerts import router as alerts_router
from app.api.sync import router as sync_router

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health_router)
api_router.include_router(patients_router)
api_router.include_router(caregivers_router)
api_router.include_router(games_router)
api_router.include_router(sessions_router)
api_router.include_router(progress_router)
api_router.include_router(analytics_router)
api_router.include_router(adaptive_router)
api_router.include_router(recommendations_router)
api_router.include_router(alerts_router)
api_router.include_router(sync_router)

__all__ = ["api_router"]
