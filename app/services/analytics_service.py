"""Analytics Service for aggregating patient cognitive performance and trends."""

import sqlite3
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger
from app.database import queries
from app.schemas.progress import DailyActivitySummary, DomainScoreSummary, PatientProgressSummary

logger = get_logger("analytics_service")


class AnalyticsService:
    """Provides high-level analytics aggregation across cognitive domains and activities."""

    @classmethod
    def get_domain_summary(cls, conn: sqlite3.Connection, patient_id: int) -> List[DomainScoreSummary]:
        """Calculates domain score statistics for a patient."""
        cursor = conn.cursor()
        cursor.execute(queries.GET_DOMAIN_AVERAGES_BY_PATIENT, (patient_id,))
        rows = cursor.fetchall()
        return [
            DomainScoreSummary(
                domain=row["domain"],
                avg_score=round(row["avg_score"], 2),
                sessions_count=row["score_count"],
                min_score=round(row["min_score"], 2),
                max_score=round(row["max_score"], 2),
            )
            for row in rows
        ]

    @classmethod
    def get_daily_activity_summaries(
        cls, conn: sqlite3.Connection, patient_id: int, limit: int = 14
    ) -> List[DailyActivitySummary]:
        """Retrieves recent daily activity tracking metrics."""
        cursor = conn.cursor()
        cursor.execute(queries.GET_DAILY_ACTIVITIES, (patient_id, limit))
        rows = cursor.fetchall()
        return [
            DailyActivitySummary(
                activity_date=row["activity_date"],
                games_played=row["games_played"],
                total_duration_seconds=row["total_duration_seconds"],
                avg_score=round(row["avg_score"], 2),
                symptoms_count=row["symptoms_count"],
                routine_adherence_percentage=round(row["routine_adherence_percentage"], 2),
            )
            for row in rows
        ]

    @classmethod
    def get_patient_progress(cls, conn: sqlite3.Connection, patient_id: int) -> Optional[PatientProgressSummary]:
        """Assembles a comprehensive progress overview for a patient."""
        cursor = conn.cursor()
        cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            return None

        # Total sessions
        cursor.execute("SELECT COUNT(*) as total FROM game_sessions WHERE patient_id = ?", (patient_id,))
        total_sessions = cursor.fetchone()["total"]

        # Domain breakdown
        domain_breakdown = cls.get_domain_summary(conn, patient_id)

        # Recent activities
        recent_activities = cls.get_daily_activity_summaries(conn, patient_id, limit=7)

        # Overall current score & trend
        cursor.execute(
            """
            SELECT score_value
            FROM cognitive_scores
            WHERE patient_id = ?
            ORDER BY recorded_at DESC
            LIMIT 5;
            """,
            (patient_id,),
        )
        recent_scores = [r["score_value"] for r in cursor.fetchall()]
        baseline = float(patient["baseline_score"] or 70.0)
        
        if recent_scores:
            overall_current = sum(recent_scores) / len(recent_scores)
            diff = overall_current - baseline
            trend = "improving" if diff >= 5 else ("declining" if diff <= -10 else "stable")
        else:
            overall_current = baseline
            trend = "stable"

        return PatientProgressSummary(
            patient_id=patient["id"],
            patient_name=f"{patient['first_name']} {patient['last_name']}",
            stage=patient["stage"],
            baseline_score=baseline,
            overall_current_score=round(overall_current, 2),
            score_trend=trend,
            total_sessions_completed=total_sessions,
            domain_breakdown=domain_breakdown,
            recent_activities=recent_activities,
        )

    @classmethod
    def get_overview_statistics(cls, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Provides high-level platform health metrics for caregivers."""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        total_patients = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM caregivers")
        total_caregivers = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM game_sessions")
        total_sessions = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE is_read = 0")
        active_alerts = cursor.fetchone()["count"]

        cursor.execute("SELECT AVG(score_value) as avg_score FROM cognitive_scores")
        row = cursor.fetchone()
        platform_avg_score = round(row["avg_score"], 2) if row["avg_score"] else 0.0

        return {
            "total_patients": total_patients,
            "total_caregivers": total_caregivers,
            "total_sessions": total_sessions,
            "active_alerts": active_alerts,
            "platform_average_cognitive_score": platform_avg_score,
        }
