"""Pydantic schemas for AI Assessments and Recommendations."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AIAssessmentBase(BaseModel):
    patient_id: int
    summary: str
    risk_level: str = Field("low", description="low, medium, high, critical")
    cognitive_trend: str = Field("stable", description="improving, stable, declining")
    confidence_score: float = Field(0.85, ge=0.0, le=1.0)
    raw_insights: Optional[str] = None


class AIAssessmentCreate(AIAssessmentBase):
    pass


class AIAssessmentResponse(AIAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_date: Optional[str] = None
    created_at: Optional[str] = None


class AIRecommendationBase(BaseModel):
    patient_id: int
    assessment_id: Optional[int] = None
    title: str
    description: str
    category: str = Field("game_adjustment", description="game_adjustment, routine, caregiver_action, medical_review")
    priority: str = Field("medium", description="low, medium, high")
    status: str = Field("active", description="active, completed, dismissed")


class AIRecommendationCreate(AIRecommendationBase):
    pass


class AIRecommendationResponse(AIRecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[str] = None
