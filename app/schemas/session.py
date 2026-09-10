"""Pydantic schemas for Game Sessions."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GameSessionBase(BaseModel):
    patient_id: int
    game_id: int
    level: int = Field(1, ge=1)
    duration_seconds: int = Field(0, ge=0)
    status: str = Field("completed", description="completed, failed, abandoned")
    score: float = Field(0.0, ge=0.0)
    accuracy_percentage: float = Field(0.0, ge=0.0, le=100.0)
    reaction_time_ms: Optional[float] = None
    device_info: Optional[str] = None
    session_timestamp: Optional[str] = None


class GameSessionCreate(GameSessionBase):
    pass


class GameSessionResponse(GameSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_name: Optional[str] = None
    game_key: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
