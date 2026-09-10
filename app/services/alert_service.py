"""Alert and Symptom Management Service for caregivers."""

import sqlite3
from typing import List, Optional

from app.core.logging_config import get_logger
from app.database import queries
from app.schemas.alert import AlertCreate, AlertResponse, ReminderCreate, ReminderResponse, SymptomCreate, SymptomResponse

logger = get_logger("alert_service")


class AlertService:
    """Handles logging of symptoms, triggering safety alerts, and reminder workflows."""

    @classmethod
    def log_symptom(cls, conn: sqlite3.Connection, symptom: SymptomCreate) -> SymptomResponse:
        """Logs a patient symptom and generates automatic caregiver alerts for severe symptoms."""
        cursor = conn.cursor()
        cursor.execute(
            queries.INSERT_SYMPTOM,
            (
                symptom.patient_id,
                symptom.caregiver_id,
                symptom.symptom_name,
                symptom.severity,
                symptom.notes,
                symptom.logged_at,
            ),
        )
        symptom_id = cursor.lastrowid

        # Automatic critical alert trigger for severe symptoms (severity >= 4)
        if symptom.severity >= 4:
            alert_msg = f"High severity symptom logged ({symptom.symptom_name}, Severity: {symptom.severity}/5). Caregiver attention required."
            cursor.execute(
                queries.INSERT_ALERT,
                (symptom.patient_id, symptom.caregiver_id, "severe_symptom", "critical", alert_msg, 0),
            )
            logger.warning(f"Critical alert triggered for patient {symptom.patient_id}: {alert_msg}")

        return SymptomResponse(
            id=symptom_id,
            patient_id=symptom.patient_id,
            caregiver_id=symptom.caregiver_id,
            symptom_name=symptom.symptom_name,
            severity=symptom.severity,
            notes=symptom.notes,
            logged_at=symptom.logged_at,
        )

    @classmethod
    def create_alert(cls, conn: sqlite3.Connection, alert: AlertCreate) -> AlertResponse:
        """Creates a direct caregiver notification alert."""
        cursor = conn.cursor()
        cursor.execute(
            queries.INSERT_ALERT,
            (alert.patient_id, alert.caregiver_id, alert.alert_type, alert.severity, alert.message, int(alert.is_read)),
        )
        alert_id = cursor.lastrowid
        return AlertResponse(
            id=alert_id,
            patient_id=alert.patient_id,
            caregiver_id=alert.caregiver_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            is_read=alert.is_read,
        )

    @classmethod
    def get_patient_alerts(cls, conn: sqlite3.Connection, patient_id: int) -> List[AlertResponse]:
        """Fetches alerts associated with a patient."""
        cursor = conn.cursor()
        cursor.execute(queries.GET_PATIENT_ALERTS, (patient_id,))
        rows = cursor.fetchall()
        return [
            AlertResponse(
                id=row["id"],
                patient_id=row["patient_id"],
                caregiver_id=row["caregiver_id"],
                alert_type=row["alert_type"],
                severity=row["severity"],
                message=row["message"],
                is_read=bool(row["is_read"]),
                resolved_at=row["resolved_at"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    @classmethod
    def create_reminder(cls, conn: sqlite3.Connection, reminder: ReminderCreate) -> ReminderResponse:
        """Creates a scheduled reminder for medication, games, or hydration."""
        cursor = conn.cursor()
        cursor.execute(
            queries.INSERT_REMINDER,
            (
                reminder.patient_id,
                reminder.caregiver_id,
                reminder.title,
                reminder.reminder_type,
                reminder.scheduled_time,
                int(reminder.is_completed),
                reminder.recurring_frequency,
            ),
        )
        reminder_id = cursor.lastrowid
        return ReminderResponse(
            id=reminder_id,
            patient_id=reminder.patient_id,
            caregiver_id=reminder.caregiver_id,
            title=reminder.title,
            reminder_type=reminder.reminder_type,
            scheduled_time=reminder.scheduled_time,
            is_completed=reminder.is_completed,
            recurring_frequency=reminder.recurring_frequency,
        )

    @classmethod
    def get_patient_reminders(cls, conn: sqlite3.Connection, patient_id: int) -> List[ReminderResponse]:
        """Fetches scheduled reminders for a patient."""
        cursor = conn.cursor()
        cursor.execute(queries.GET_PATIENT_REMINDERS, (patient_id,))
        rows = cursor.fetchall()
        return [
            ReminderResponse(
                id=row["id"],
                patient_id=row["patient_id"],
                caregiver_id=row["caregiver_id"],
                title=row["title"],
                reminder_type=row["reminder_type"],
                scheduled_time=row["scheduled_time"],
                is_completed=bool(row["is_completed"]),
                recurring_frequency=row["recurring_frequency"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
