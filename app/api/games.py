"""Cognitive Games catalogue and details API routes."""

import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import queries
from app.database.connection import get_db
from app.schemas.game import CognitiveGameCreate, CognitiveGameResponse

router = APIRouter(prefix="/games", tags=["Cognitive Games"])


@router.get("", response_model=List[CognitiveGameResponse], summary="List all active cognitive games")
def list_games(conn: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves list of cognitive games available for therapy sessions."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_ALL_GAMES)
    return [dict(r) for r in cursor.fetchall()]


@router.get("/{game_key}", response_model=CognitiveGameResponse, summary="Get game details by key")
def get_game(game_key: str, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Fetches specifications and configuration for a game key."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_GAME_BY_KEY, (game_key,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game '{game_key}' not found")
    return dict(row)


@router.post("", response_model=CognitiveGameResponse, status_code=status.HTTP_201_CREATED, summary="Register a cognitive game")
def create_game(game_in: CognitiveGameCreate, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Registers a new cognitive game module into the catalogue."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            queries.INSERT_GAME,
            (
                game_in.game_key,
                game_in.name,
                game_in.category,
                game_in.description,
                game_in.max_level,
                int(game_in.is_active),
            ),
        )
        new_id = cursor.lastrowid
        cursor.execute(queries.GET_GAME_BY_ID, (new_id,))
        return dict(cursor.fetchone())
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game with key '{game_in.game_key}' already exists.",
        )
