"""Pydantic schemas for Adaptive Difficulty tuning."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AdaptiveDifficultyRequest(BaseModel):
    patient_id: int
    game_key: str
    current_level: int = Field(1, ge=1, le=100)
    recent_accuracies: List[float] = Field(default_factory=list)
    recent_reaction_times: List[float] = Field(default_factory=list)
    consecutive_failures: int = Field(0, ge=0)
    consecutive_successes: int = Field(0, ge=0)


class AdaptiveDifficultyResponse(BaseModel):
    patient_id: int
    game_key: str
    recommended_level: int
    adjustment_action: str = Field(..., description="increase, decrease, maintain, simplify")
    reasoning: str
    confidence: float = 0.9
    suggested_hints_enabled: bool = False
