"""Cognitive Analytics API routes."""

import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.connection import get_db
from app.schemas.progress import DailyActivitySummary, DomainScoreSummary
from app.schemas.scoring import ScoreCalculationRequest, ScoreCalculationResult
from app.services.analytics_service import AnalyticsService
from app.services.baseline_service import BaselineService
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", summary="Get platform-wide analytics overview")
def get_platform_overview(conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Retrieves high-level platform summary statistics for caregivers and physicians."""
    return AnalyticsService.get_overview_statistics(conn)


@router.get("/patient/{patient_id}/domains", response_model=List[DomainScoreSummary], summary="Get patient cognitive domain breakdown")
def get_patient_domains(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> List[DomainScoreSummary]:
    """Retrieves aggregated score metrics for each cognitive domain (memory, recognition, problem solving, etc.)."""
    return AnalyticsService.get_domain_summary(conn, patient_id)


@router.get("/patient/{patient_id}/trends", summary="Get patient cognitive score trajectory")
def get_patient_trends(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Evaluates short and medium-term cognitive trajectories against baseline."""
    trend, avg_score, baseline = BaselineService.analyze_cognitive_trend(conn, patient_id)
    return {
        "patient_id": patient_id,
        "trend": trend,
        "current_window_average": avg_score,
        "baseline_score": baseline,
        "baseline_deviation": round(avg_score - baseline, 2),
    }


@router.get("/patient/{patient_id}/activity", response_model=List[DailyActivitySummary], summary="Get daily activity history")
def get_patient_daily_activity(
    patient_id: int,
    limit: int = Query(14, ge=1, le=60),
    conn: sqlite3.Connection = Depends(get_db),
) -> List[DailyActivitySummary]:
    """Retrieves recent daily activity tracking metrics."""
    return AnalyticsService.get_daily_activity_summaries(conn, patient_id, limit)


@router.post("/calculate-score", response_model=ScoreCalculationResult, summary="Calculate cognitive score for an attempt")
def calculate_cognitive_score(
    request: ScoreCalculationRequest, conn: sqlite3.Connection = Depends(get_db)
) -> ScoreCalculationResult:
    """Executes multi-factor cognitive score calculation combining accuracy, reaction time, level, and penalties."""
    return ScoringService.calculate_score(conn, request)
