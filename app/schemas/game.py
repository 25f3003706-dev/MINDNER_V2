"""Pydantic schemas for Cognitive Games."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CognitiveGameBase(BaseModel):
    game_key: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., description="Domain: memory, recognition, problem_solving, routine, attention")
    description: Optional[str] = None
    max_level: int = Field(10, ge=1, le=100)
    is_active: bool = True


class CognitiveGameCreate(CognitiveGameBase):
    pass


class CognitiveGameResponse(CognitiveGameBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[str] = None
