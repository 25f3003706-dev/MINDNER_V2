"""Alerts, Symptoms, and Reminders API routes."""

import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import queries
from app.database.connection import get_db
from app.schemas.alert import (
    AlertCreate,
    AlertResponse,
    ReminderCreate,
    ReminderResponse,
    SymptomCreate,
    SymptomResponse,
)
from app.services.alert_service import AlertService
from app.utils.response import success_response

router = APIRouter(prefix="/alerts", tags=["Alerts & Symptoms"])


# ---------------------------------------------------------------------
# Symptoms
# ---------------------------------------------------------------------
@router.post("/symptoms", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED, summary="Log a patient symptom")
def log_symptom(symptom_in: SymptomCreate, conn: sqlite3.Connection = Depends(get_db)) -> SymptomResponse:
    """Logs observed behavioral or physical symptom. Triggers alert automatically if severity >= 4."""
    return AlertService.log_symptom(conn, symptom_in)


@router.get("/symptoms/patient/{patient_id}", response_model=List[SymptomResponse], summary="Get patient symptom log")
def get_patient_symptoms(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves recorded symptoms for a patient."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_PATIENT_SYMPTOMS, (patient_id,))
    return [dict(r) for r in cursor.fetchall()]


# ---------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------
@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED, summary="Trigger a caregiver alert")
def create_alert(alert_in: AlertCreate, conn: sqlite3.Connection = Depends(get_db)) -> AlertResponse:
    """Dispatches a notification alert for caregiver attention."""
    return AlertService.create_alert(conn, alert_in)


@router.get("/patient/{patient_id}", response_model=List[AlertResponse], summary="Get alerts for a patient")
def get_patient_alerts(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> List[AlertResponse]:
    """Retrieves all notification and safety alerts for a patient."""
    return AlertService.get_patient_alerts(conn, patient_id)


@router.patch("/{alert_id}/read", summary="Mark alert as read/resolved")
def mark_alert_read(alert_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Marks an alert as acknowledged and resolved."""
    cursor = conn.cursor()
    cursor.execute(queries.MARK_ALERT_READ, (alert_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return success_response(data={"alert_id": alert_id}, message="Alert marked as resolved")


# ---------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------
@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED, summary="Create a scheduled reminder")
def create_reminder(reminder_in: ReminderCreate, conn: sqlite3.Connection = Depends(get_db)) -> ReminderResponse:
    """Schedules a daily or recurring reminder (medication, games, hydration, routine)."""
    return AlertService.create_reminder(conn, reminder_in)


@router.get("/reminders/patient/{patient_id}", response_model=List[ReminderResponse], summary="Get patient scheduled reminders")
def get_patient_reminders(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> List[ReminderResponse]:
    """Retrieves scheduled reminders for a patient."""
    return AlertService.get_patient_reminders(conn, patient_id)
