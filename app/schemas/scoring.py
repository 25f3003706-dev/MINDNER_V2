"""Pydantic schemas for Cognitive Scoring."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CognitiveScoreBase(BaseModel):
    patient_id: int
    session_id: Optional[int] = None
    domain: str = Field("general", description="memory, attention, problem_solving, recognition, routine")
    score_value: float = Field(..., ge=0.0, le=100.0)
    baseline_deviation: float = 0.0
    calculation_details: Optional[str] = None


class CognitiveScoreCreate(CognitiveScoreBase):
    pass


class CognitiveScoreResponse(CognitiveScoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recorded_at: Optional[str] = None


class ScoreCalculationRequest(BaseModel):
    patient_id: int
    game_key: str
    level: int = Field(1, ge=1)
    duration_seconds: int = Field(..., ge=0)
    total_rounds: int = Field(..., ge=1)
    correct_rounds: int = Field(..., ge=0)
    avg_reaction_time_ms: float = Field(..., ge=0.0)
    mistake_count: int = Field(0, ge=0)


class ScoreCalculationResult(BaseModel):
    score: float
    accuracy_percentage: float
    domain: str
    baseline_deviation: float
    performance_tier: str
    details: Dict[str, float]
