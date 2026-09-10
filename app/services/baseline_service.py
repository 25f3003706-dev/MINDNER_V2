"""Baseline Cognitive Service for managing baseline assessments and detecting deviations."""

import sqlite3
from typing import Dict, Optional, Tuple

from app.core.logging_config import get_logger
from app.database import queries

logger = get_logger("baseline_service")


class BaselineService:
    """Manages baseline cognitive calibration and detects significant cognitive shifts."""

    @classmethod
    def get_patient_baseline(cls, conn: sqlite3.Connection, patient_id: int) -> float:
        """Retrieves configured baseline score for a patient."""
        cursor = conn.cursor()
        cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            return 70.0
        return float(patient["baseline_score"] or 70.0)

    @classmethod
    def update_baseline(cls, conn: sqlite3.Connection, patient_id: int, new_baseline: float) -> bool:
        """Updates baseline score after clinical reassessment."""
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE patients
            SET baseline_score = ?, updated_at = datetime('now', 'utc')
            WHERE id = ?;
            """,
            (new_baseline, patient_id),
        )
        return cursor.rowcount > 0

    @classmethod
    def analyze_cognitive_trend(
        cls, conn: sqlite3.Connection, patient_id: int, window_sessions: int = 5
    ) -> Tuple[str, float, float]:
        """Analyzes recent session scores compared to baseline.

        Returns:
            (trend: "improving" | "stable" | "declining", current_average: float, baseline: float)
        """
        cursor = conn.cursor()
        cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
        patient = cursor.fetchone()
        baseline = float(patient["baseline_score"] or 70.0) if patient else 70.0

        cursor.execute(
            """
            SELECT score_value
            FROM cognitive_scores
            WHERE patient_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?;
            """,
            (patient_id, window_sessions),
        )
        rows = cursor.fetchall()
        if not rows:
            return "stable", baseline, baseline

        scores = [r["score_value"] for r in rows]
        avg_recent = sum(scores) / len(scores)

        diff = avg_recent - baseline
        if diff >= 5.0:
            trend = "improving"
        elif diff <= -10.0:
            trend = "declining"
        else:
            trend = "stable"

        return trend, round(avg_recent, 2), baseline
