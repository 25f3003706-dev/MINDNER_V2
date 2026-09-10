"""Offline Synchronization and device batching API routes."""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.database import queries
from app.database.connection import get_db
from app.schemas.session import GameSessionCreate
from app.services.scoring_service import ScoringService
from app.utils.response import success_response

router = APIRouter(prefix="/sync", tags=["Offline Sync"])


class BatchSyncRequest(BaseModel):
    device_id: str
    sessions: List[GameSessionCreate] = Field(default_factory=list)
    client_timestamp: Optional[str] = None


@router.post("/batch", status_code=status.HTTP_200_OK, summary="Sync offline game sessions from client devices")
def sync_batch_sessions(
    batch: BatchSyncRequest, conn: sqlite3.Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Ingests batched game sessions recorded while tablet/browser was offline."""
    cursor = conn.cursor()
    synced_count = 0
    errors = []

    for session_in in batch.sessions:
        try:
            # Check game
            cursor.execute(queries.GET_GAME_BY_ID, (session_in.game_id,))
            game = cursor.fetchone()
            if not game:
                errors.append(f"Invalid game_id {session_in.game_id}")
                continue

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
                    session_in.device_info or batch.device_id,
                    session_in.session_timestamp,
                ),
            )
            session_id = cursor.lastrowid
            domain = ScoringService.DOMAIN_MAPPING.get(game["game_key"], "general")

            cursor.execute(queries.GET_PATIENT_BY_ID, (session_in.patient_id,))
            patient = cursor.fetchone()
            baseline = float(patient["baseline_score"] or 70.0) if patient else 70.0
            deviation = round(session_in.score - baseline, 2)

            ScoringService.record_score(
                conn=conn,
                patient_id=session_in.patient_id,
                session_id=session_id,
                domain=domain,
                score_value=session_in.score,
                baseline_deviation=deviation,
                details=f"Sync from device {batch.device_id}",
            )
            synced_count += 1
        except Exception as e:
            errors.append(str(e))

    # Log sync event
    sync_status = "success" if not errors else ("partial" if synced_count > 0 else "failure")
    details = json.dumps({"errors": errors, "total_submitted": len(batch.sessions)})
    cursor.execute(
        queries.INSERT_SYNC_LOG,
        (batch.device_id, synced_count, "batch_sessions", sync_status, details),
    )

    return success_response(
        data={
            "device_id": batch.device_id,
            "records_synced": synced_count,
            "errors": errors,
            "status": sync_status,
        },
        message=f"Synced {synced_count} records successfully",
    )


@router.get("/logs", summary="Get recent device synchronization logs")
def get_sync_logs(
    limit: int = 20, conn: sqlite3.Connection = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Retrieves sync operation audit trail."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_SYNC_LOGS, (limit,))
    return [dict(r) for r in cursor.fetchall()]
