"""Patient Progress and Cognitive Trajectory API routes."""

import sqlite3
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from app.database.connection import get_db
from app.schemas.progress import PatientProgressSummary
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/patient/{patient_id}", response_model=PatientProgressSummary, summary="Get comprehensive patient progress report")
def get_progress(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Retrieves end-to-end cognitive progress, baseline deviations, and domain breakdown."""
    summary = AnalyticsService.get_patient_progress(conn, patient_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")
    return summary.model_dump()
