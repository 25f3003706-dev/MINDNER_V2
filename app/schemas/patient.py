"""Pydantic schemas for Patients."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, max_length=50)
    stage: str = Field("Mild", description="Stage of impairment: Mild, Moderate, Severe, Early, Undiagnosed")
    baseline_score: float = Field(70.0, ge=0.0, le=100.0)
    diagnosis_date: Optional[str] = None
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    stage: Optional[str] = None
    baseline_score: Optional[float] = None
    diagnosis_date: Optional[str] = None
    notes: Optional[str] = None


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PatientSummary(BaseModel):
    id: int
    full_name: str
    stage: str
    baseline_score: float
    total_sessions_played: int = 0
    recent_average_score: Optional[float] = None
