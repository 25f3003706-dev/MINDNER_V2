"""Patient management API routes."""

import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import queries
from app.database.connection import get_db
from app.schemas.caregiver import LinkedPatientResponse
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.utils.response import success_response

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=List[PatientResponse], summary="List all patients")
def list_patients(conn: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves all registered dementia patients."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_ALL_PATIENTS)
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, summary="Create a new patient")
def create_patient(patient_in: PatientCreate, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Registers a new patient profile."""
    cursor = conn.cursor()
    cursor.execute(
        queries.INSERT_PATIENT,
        (
            patient_in.first_name,
            patient_in.last_name,
            patient_in.age,
            patient_in.gender,
            patient_in.stage,
            patient_in.baseline_score,
            patient_in.diagnosis_date,
            patient_in.notes,
        ),
    )
    new_id = cursor.lastrowid
    cursor.execute(queries.GET_PATIENT_BY_ID, (new_id,))
    return dict(cursor.fetchone())


@router.get("/{patient_id}", response_model=PatientResponse, summary="Get patient by ID")
def get_patient(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Fetches details for a specific patient."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")
    return dict(row)


@router.put("/{patient_id}", response_model=PatientResponse, summary="Update patient")
def update_patient(patient_id: int, patient_in: PatientUpdate, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Updates an existing patient profile."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
    current = cursor.fetchone()
    if not current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")

    updated = {
        "first_name": patient_in.first_name if patient_in.first_name is not None else current["first_name"],
        "last_name": patient_in.last_name if patient_in.last_name is not None else current["last_name"],
        "age": patient_in.age if patient_in.age is not None else current["age"],
        "gender": patient_in.gender if patient_in.gender is not None else current["gender"],
        "stage": patient_in.stage if patient_in.stage is not None else current["stage"],
        "baseline_score": patient_in.baseline_score if patient_in.baseline_score is not None else current["baseline_score"],
        "diagnosis_date": patient_in.diagnosis_date if patient_in.diagnosis_date is not None else current["diagnosis_date"],
        "notes": patient_in.notes if patient_in.notes is not None else current["notes"],
    }

    cursor.execute(
        queries.UPDATE_PATIENT,
        (
            updated["first_name"],
            updated["last_name"],
            updated["age"],
            updated["gender"],
            updated["stage"],
            updated["baseline_score"],
            updated["diagnosis_date"],
            updated["notes"],
            patient_id,
        ),
    )
    cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
    return dict(cursor.fetchone())


@router.delete("/{patient_id}", summary="Delete patient")
def delete_patient(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Removes a patient profile and associated records."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_PATIENT_BY_ID, (patient_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {patient_id} not found")

    cursor.execute(queries.DELETE_PATIENT, (patient_id,))
    return success_response(data={"patient_id": patient_id}, message="Patient deleted successfully")


@router.get("/{patient_id}/caregivers", summary="Get linked caregivers for a patient")
def get_linked_caregivers(patient_id: int, conn: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves all caregivers linked to this patient."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_PATIENT_CAREGIVERS, (patient_id,))
    return [dict(r) for r in cursor.fetchall()]
