"""Pydantic schemas for Game Attempts and trial details."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class GameAttemptBase(BaseModel):
    session_id: Optional[int] = None
    patient_id: int
    game_id: int
    level: int = 1
    round_number: int = 1
    target_item: Optional[str] = None
    chosen_item: Optional[str] = None
    is_correct: bool
    response_time_ms: float = Field(0.0, ge=0.0)
    extra_metadata: Optional[Dict[str, Any]] = None


class GameAttemptCreate(GameAttemptBase):
    pass


class GameAttemptResponse(GameAttemptBase):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    timestamp: Optional[str] = None
