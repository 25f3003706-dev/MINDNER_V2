"""Game Sessions API routes."""

import sqlite3
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import queries
from app.database.connection import get_db
from app.schemas.session import GameSessionCreate, GameSessionResponse
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/sessions", tags=["Game Sessions"])


@router.post("", response_model=GameSessionResponse, status_code=status.HTTP_201_CREATED, summary="Record a completed game session")
def create_session(session_in: GameSessionCreate, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Records a patient's game session attempt and automatically updates cognitive domain scores."""
    cursor = conn.cursor()

    # Validate patient
    cursor.execute(queries.GET_PATIENT_BY_ID, (session_in.patient_id,))
    patient = cursor.fetchone()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Validate game
    cursor.execute(queries.GET_GAME_BY_ID, (session_in.game_id,))
    game = cursor.fetchone()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    cursor.execute(
        queries.INSERT_GAME_SESSION,
        (
            session_in.patient_id,
            session_in.game_id,
            session_in.level,
            session_in.duration_seconds,
            session_in.status,
            session_in.score,
            session_in.accuracy_percentage,
            session_in.reaction_time_ms,
            session_in.device_info,
            session_in.session_timestamp,
        ),
    )
    session_id = cursor.lastrowid

    # Automatically record cognitive domain score
    domain = ScoringService.DOMAIN_MAPPING.get(game["game_key"], "general")
    baseline = float(patient["baseline_score"] or 70.0)
    deviation = round(session_in.score - baseline, 2)
    ScoringService.record_score(
        conn=conn,
        patient_id=session_in.patient_id,
        session_id=session_id,
        domain=domain,
        score_value=session_in.score,
        baseline_deviation=deviation,
        details=f"Session {session_id} - {game['name']} Level {session_in.level}",
    )

    return {
        "id": session_id,
        "patient_id": session_in.patient_id,
        "game_id": session_in.game_id,
        "game_name": game["name"],
        "game_key": game["game_key"],
        "category": game["category"],
        "level": session_in.level,
        "duration_seconds": session_in.duration_seconds,
        "status": session_in.status,
        "score": session_in.score,
        "accuracy_percentage": session_in.accuracy_percentage,
        "reaction_time_ms": session_in.reaction_time_ms,
        "device_info": session_in.device_info,
        "session_timestamp": session_in.session_timestamp,
    }


@router.get("/patient/{patient_id}", response_model=List[GameSessionResponse], summary="Get patient session history")
def get_patient_sessions(
    patient_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conn: sqlite3.Connection = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Retrieves paginated game session history for a specific patient."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_PATIENT_SESSIONS, (patient_id, limit, offset))
    return [dict(r) for r in cursor.fetchall()]
