"""Pydantic schemas for Symptoms, Alerts, and Reminders."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------
# Symptoms
# ---------------------------------------------------------------------
class SymptomBase(BaseModel):
    patient_id: int
    caregiver_id: Optional[int] = None
    symptom_name: str = Field(..., min_length=2, max_length=150)
    severity: int = Field(1, ge=1, le=5)
    notes: Optional[str] = None
    logged_at: Optional[str] = None


class SymptomCreate(SymptomBase):
    pass


class SymptomResponse(SymptomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[str] = None


# ---------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------
class AlertBase(BaseModel):
    patient_id: int
    caregiver_id: Optional[int] = None
    alert_type: str = Field(..., description="cognitive_drop, missed_session, severe_symptom, wandering_risk, emergency")
    severity: str = Field("info", description="info, warning, critical")
    message: str = Field(..., min_length=3)
    is_read: bool = False


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resolved_at: Optional[str] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------
class ReminderBase(BaseModel):
    patient_id: int
    caregiver_id: Optional[int] = None
    title: str = Field(..., min_length=2, max_length=150)
    reminder_type: str = Field("medication", description="medication, game_time, hydration, appointment, meal")
    scheduled_time: str
    is_completed: bool = False
    recurring_frequency: str = "daily"


class ReminderCreate(ReminderBase):
    pass


class ReminderResponse(ReminderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[str] = None
