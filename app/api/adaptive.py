"""Adaptive Difficulty API routes."""

import sqlite3
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.database.connection import get_db
from app.schemas.adaptive import AdaptiveDifficultyRequest, AdaptiveDifficultyResponse
from app.services.adaptive_service import AdaptiveService

router = APIRouter(prefix="/adaptive", tags=["Adaptive Difficulty"])


@router.post("/evaluate", response_model=AdaptiveDifficultyResponse, summary="Evaluate and recommend next difficulty level")
def evaluate_adaptive_difficulty(
    request: AdaptiveDifficultyRequest, conn: sqlite3.Connection = Depends(get_db)
) -> AdaptiveDifficultyResponse:
    """Calculates personalized challenge level to sustain engagement without causing agitation or distress."""
    return AdaptiveService.evaluate_difficulty(conn, request)
