"""Pydantic schemas for Patient Progress tracking."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class DomainScoreSummary(BaseModel):
    domain: str
    avg_score: float
    sessions_count: int
    min_score: float
    max_score: float


class DailyActivitySummary(BaseModel):
    activity_date: str
    games_played: int
    total_duration_seconds: int
    avg_score: float
    symptoms_count: int
    routine_adherence_percentage: float


class PatientProgressSummary(BaseModel):
    patient_id: int
    patient_name: str
    stage: str
    baseline_score: float
    overall_current_score: float
    score_trend: str  # improving, stable, declining
    total_sessions_completed: int
    domain_breakdown: List[DomainScoreSummary]
    recent_activities: List[DailyActivitySummary]
