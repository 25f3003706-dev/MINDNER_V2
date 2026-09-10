"""Caregiver management API routes."""

import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import queries
from app.database.connection import get_db
from app.schemas.caregiver import (
    CaregiverCreate,
    CaregiverResponse,
    CaregiverUpdate,
    PatientCaregiverLinkCreate,
)
from app.utils.response import success_response

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])


@router.get("", response_model=List[CaregiverResponse], summary="List all caregivers")
def list_caregivers(conn: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves all registered caregivers."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_ALL_CAREGIVERS)
    return [dict(r) for r in cursor.fetchall()]


@router.post("", response_model=CaregiverResponse, status_code=status.HTTP_201_CREATED, summary="Create caregiver")
def create_caregiver(caregiver_in: CaregiverCreate, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Registers a new caregiver."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            queries.INSERT_CAREGIVER,
            (
                caregiver_in.first_name,
                caregiver_in.last_name,
                caregiver_in.email,
                caregiver_in.phone,
                caregiver_in.relation,
            ),
        )
        new_id = cursor.lastrowid
        cursor.execute(queries.GET_CAREGIVER_BY_ID, (new_id,))
        return dict(cursor.fetchone())
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Caregiver with email {caregiver_in.email} already exists.",
        )


@router.get("/{caregiver_id}", response_model=CaregiverResponse, summary="Get caregiver by ID")
def get_caregiver(caregiver_id: int, conn: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Fetches details for a specific caregiver."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_CAREGIVER_BY_ID, (caregiver_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Caregiver {caregiver_id} not found")
    return dict(row)


@router.post("/link-patient", summary="Link caregiver to patient")
def link_patient_caregiver(
    link: PatientCaregiverLinkCreate, conn: sqlite3.Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Establishes or updates a relationship between a caregiver and a patient."""
    cursor = conn.cursor()
    # Check patient exists
    cursor.execute(queries.GET_PATIENT_BY_ID, (link.patient_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Check caregiver exists
    cursor.execute(queries.GET_CAREGIVER_BY_ID, (link.caregiver_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver not found")

    cursor.execute(
        queries.LINK_PATIENT_CAREGIVER,
        (link.patient_id, link.caregiver_id, link.relationship_type, int(link.is_primary)),
    )
    return success_response(
        data={"patient_id": link.patient_id, "caregiver_id": link.caregiver_id},
        message="Patient and caregiver linked successfully",
    )


@router.get("/{caregiver_id}/patients", summary="Get patients assigned to a caregiver")
def get_assigned_patients(caregiver_id: int, conn: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves all patients supervised by this caregiver."""
    cursor = conn.cursor()
    cursor.execute(queries.GET_CAREGIVER_PATIENTS, (caregiver_id,))
    return [dict(r) for r in cursor.fetchall()]
