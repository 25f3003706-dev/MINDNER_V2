"""AI Assessments and Recommendations API routes."""

import sqlite3
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import queries
from app.database.connection import get_db
from app.schemas.recommendation import (
    AIAssessmentResponse,
    AIRecommendationCreate,
    AIRecommendationResponse,
)
from app.services.recommendation_service import RecommendationService
from app.utils.response import success_response

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations & Assessments"])


@router.post("/generate/{patient_id}", response_model=AIAssessmentResponse, status_code=status.HTTP_201_CREATED, summary="Generate AI assessment and recommendation")
def generate_ai_assessment(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> AIAssessmentResponse:
    """Synthesizes patient session history into a fresh clinical assessment and tailored recommendations."""
    try:
        return RecommendationService.generate_assessment(conn, patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/patient/{patient_id}", response_model=List[AIRecommendationResponse], summary="List patient AI recommendations")
def list_patient_recommendations(
    patient_id: int,
    status: Optional[str] = Query(None, description="Filter by status: active, completed, dismissed"),
    conn: sqlite3.Connection = Depends(get_db),
) -> List[AIRecommendationResponse]:
    """Retrieves list of active or past AI recommendations for the caregiver."""
    return RecommendationService.get_recommendations(conn, patient_id, status)


@router.patch("/{recommendation_id}/status", summary="Update recommendation status")
def update_recommendation_status(
    recommendation_id: int,
    status_value: str = Query(..., description="active, completed, dismissed"),
    conn: sqlite3.Connection = Depends(get_db),
) -> Dict[str, Any]:
    """Updates the action status of an AI recommendation."""
    cursor = conn.cursor()
    cursor.execute(queries.UPDATE_RECOMMENDATION_STATUS, (status_value, recommendation_id))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return success_response(
        data={"recommendation_id": recommendation_id, "status": status_value},
        message="Recommendation status updated successfully",
    )
