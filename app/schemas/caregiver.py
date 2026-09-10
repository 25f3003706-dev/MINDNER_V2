"""Pydantic schemas for Caregivers and Patient-Caregiver relationships."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CaregiverBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    relation: Optional[str] = Field(None, max_length=100)


class CaregiverCreate(CaregiverBase):
    pass


class CaregiverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    relation: Optional[str] = None


class CaregiverResponse(CaregiverBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PatientCaregiverLinkCreate(BaseModel):
    patient_id: int
    caregiver_id: int
    relationship_type: str = "Primary Caregiver"
    is_primary: bool = True


class LinkedPatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    stage: str
    relationship_type: str
    is_primary: bool
