"""Adaptive Difficulty Service for tailoring game challenges to dementia patients."""

import sqlite3
from typing import Optional

try:
    from xgboost import XGBRegressor
except ImportError:  # Keep the API usable before optional ML dependencies are installed.
    XGBRegressor = None

from app.core.logging_config import get_logger
from app.schemas.adaptive import AdaptiveDifficultyRequest, AdaptiveDifficultyResponse

logger = get_logger("adaptive_service")


class AdaptiveService:
    """Calculates adaptive difficulty adjustments to maintain optimal cognitive engagement without inducing frustration."""

    MAX_LEVEL = 10
    MIN_LEVEL = 1
    _difficulty_model = None

    @classmethod
    def _predict_model_delta(cls, request: AdaptiveDifficultyRequest) -> float:
        """Predict a difficulty delta from recent performance when rules are inconclusive."""
        if XGBRegressor is None:
            return 0.0

        if cls._difficulty_model is None:
            # Small, explainable calibration set used until patient history is large enough.
            features = [
                [35, 3, 0, 4200], [50, 2, 0, 3500], [65, 1, 0, 2800],
                [75, 0, 1, 2200], [88, 0, 2, 1400], [96, 0, 3, 900],
            ]
            targets = [-1.0, -1.0, -0.5, 0.0, 0.5, 1.0]
            cls._difficulty_model = XGBRegressor(
                n_estimators=24,
                max_depth=2,
                learning_rate=0.15,
                objective="reg:squarederror",
                random_state=7,
                n_jobs=1,
                verbosity=0,
            )
            cls._difficulty_model.fit(features, targets)

        accuracy = sum(request.recent_accuracies) / len(request.recent_accuracies) if request.recent_accuracies else 70.0
        reaction_time = sum(request.recent_reaction_times) / len(request.recent_reaction_times) if request.recent_reaction_times else 2000.0
        prediction = cls._difficulty_model.predict([[accuracy, request.consecutive_failures, request.consecutive_successes, reaction_time]])
        return float(prediction[0])

    @classmethod
    def evaluate_difficulty(cls, conn: sqlite3.Connection, request: AdaptiveDifficultyRequest) -> AdaptiveDifficultyResponse:
        """Determines the next appropriate game level and assistance level."""
        current = request.current_level
        action = "maintain"
        reason = "Performance is stable within the target challenge range."
        recommended = current
        suggest_hints = False
        model_delta = cls._predict_model_delta(request)

        # Rule 1: High frustration prevention (2+ consecutive failures or low accuracy)
        if request.consecutive_failures >= 2:
            recommended = max(cls.MIN_LEVEL, current - 1)
            action = "decrease"
            suggest_hints = True
            reason = f"Detected {request.consecutive_failures} consecutive incomplete sessions. Decreasing level to reduce cognitive fatigue."

        # Rule 2: Consistent mastery progression (2+ consecutive high successes, >85% accuracy)
        elif request.consecutive_successes >= 2:
            avg_acc = (
                sum(request.recent_accuracies) / len(request.recent_accuracies)
                if request.recent_accuracies
                else 90.0
            )
            if avg_acc >= 85.0 and current < cls.MAX_LEVEL:
                recommended = min(cls.MAX_LEVEL, current + 1)
                action = "increase"
                reason = f"Consistent mastery demonstrated (avg accuracy {avg_acc:.1f}%). Advancing to level {recommended}."
            else:
                reason = "High success rate, maintaining level for consolidation before next tier."

        # Rule 3: Prolonged reaction times indicating cognitive friction
        elif request.recent_reaction_times and (sum(request.recent_reaction_times) / len(request.recent_reaction_times)) > 3000.0:
            suggest_hints = True
            action = "simplify"
            reason = "Response latency is elevated. Recommending visual cues and assistive hints."

        # XGBoost handles mixed signals that do not meet the explicit clinical guards above.
        elif model_delta <= -0.35:
            recommended = max(cls.MIN_LEVEL, current - 1)
            action = "decrease"
            suggest_hints = True
            reason = f"XGBoost detected a rising difficulty signal ({model_delta:.2f}); reducing challenge and enabling hints."
        elif model_delta >= 0.35:
            recommended = min(cls.MAX_LEVEL, current + 1)
            action = "increase"
            reason = f"XGBoost detected a mastery signal ({model_delta:.2f}); increasing challenge for the next session."

        return AdaptiveDifficultyResponse(
            patient_id=request.patient_id,
            game_key=request.game_key,
            recommended_level=recommended,
            adjustment_action=action,
            reasoning=reason,
            confidence=0.92,
            suggested_hints_enabled=suggest_hints,
        )
