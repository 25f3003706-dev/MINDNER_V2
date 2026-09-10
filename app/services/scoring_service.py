"""Cognitive Scoring Service for evaluating dementia patient performance."""

import sqlite3
from typing import Dict, Optional

from app.core.logging_config import get_logger
from app.database import queries
from app.schemas.scoring import ScoreCalculationRequest, ScoreCalculationResult

logger = get_logger("scoring_service")


class ScoringService:
    """Calculates cognitive performance metrics across cognitive domains."""

    DOMAIN_MAPPING = {
        "memory_match": "memory",
        "object_recognition": "recognition",
        "shape_recognition": "problem_solving",
        "daily_life_recall": "routine",
        "image_recognition": "attention",
    }

    @classmethod
    def calculate_score(cls, conn: sqlite3.Connection, request: ScoreCalculationRequest) -> ScoreCalculationResult:
        """Calculates normalized cognitive score (0-100) combining accuracy, speed, and difficulty."""
        # 1. Base Accuracy
        accuracy = (request.correct_rounds / max(request.total_rounds, 1)) * 100.0

        # 2. Reaction Speed factor (target: ~800ms - 1500ms for dementia support)
        # Slower responses get slight attenuation, very fast accurate responses get bonus
        reaction_score = max(0.0, 100.0 - (max(0.0, request.avg_reaction_time_ms - 800.0) / 30.0))
        reaction_score = min(100.0, reaction_score)

        # 3. Mistake penalty
        penalty = min(20.0, request.mistake_count * 3.0)

        # 4. Level difficulty weight (Levels 1-10)
        level_multiplier = 1.0 + (request.level - 1) * 0.05

        # Weighted calculation: 70% accuracy, 30% speed - penalty
        raw_score = (accuracy * 0.70 + reaction_score * 0.30) - penalty
        final_score = round(max(0.0, min(100.0, raw_score * level_multiplier)), 2)

        # Domain
        domain = cls.DOMAIN_MAPPING.get(request.game_key, "general")

        # Baseline comparison
        cursor = conn.cursor()
        cursor.execute(queries.GET_PATIENT_BY_ID, (request.patient_id,))
        patient = cursor.fetchone()
        baseline = float(patient["baseline_score"]) if patient and patient["baseline_score"] else 70.0
        deviation = round(final_score - baseline, 2)

        # Performance Tier
        if final_score >= 85:
            tier = "High"
        elif final_score >= 65:
            tier = "Standard"
        elif final_score >= 45:
            tier = "Moderate"
        else:
            tier = "Requires Support"

        return ScoreCalculationResult(
            score=final_score,
            accuracy_percentage=round(accuracy, 2),
            domain=domain,
            baseline_deviation=deviation,
            performance_tier=tier,
            details={
                "accuracy_component": round(accuracy * 0.70, 2),
                "speed_component": round(reaction_score * 0.30, 2),
                "penalty": round(penalty, 2),
                "level_multiplier": round(level_multiplier, 2),
                "baseline": baseline,
            },
        )

    @classmethod
    def record_score(
        cls,
        conn: sqlite3.Connection,
        patient_id: int,
        session_id: Optional[int],
        domain: str,
        score_value: float,
        baseline_deviation: float,
        details: Optional[str] = None,
    ) -> int:
        """Persists a calculated score into the cognitive_scores table."""
        cursor = conn.cursor()
        cursor.execute(
            queries.INSERT_COGNITIVE_SCORE,
            (patient_id, session_id, domain, score_value, baseline_deviation, details),
        )
        return cursor.lastrowid
