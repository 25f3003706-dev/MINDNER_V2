"""Health and diagnostic status endpoint."""

import sqlite3
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.database.connection import get_db, get_table_names

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check and database table discovery status")
def health_check(conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Returns application health, database status, and discovered SQLite tables."""
    try:
        tables = get_table_names()
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "database": {
                "status": "connected",
                "path": str(settings.DATABASE_PATH),
                "total_tables": len(tables),
                "discovered_tables": tables,
            },
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "database": {
                "status": "error",
                "error": str(e),
            },
        }
