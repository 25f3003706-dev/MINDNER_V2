"""Tests for Caregiver endpoints and patient linkage."""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_caregivers():
    response = client.get("/api/v1/caregivers")
    assert response.status_code == 200
    caregivers = response.json()
    assert isinstance(caregivers, list)
    assert len(caregivers) >= 1


def test_create_and_link_caregiver():
    unique_id = uuid.uuid4().hex[:8]
    email = f"test.caregiver.{unique_id}@testmindner.org"
    new_caregiver = {
        "first_name": "Anna",
        "last_name": "Smith",
        "email": email,
        "phone": "+1-555-9876",
        "relation": "Primary Nurse",
    }
    create_res = client.post("/api/v1/caregivers", json=new_caregiver)
    assert create_res.status_code == 201
    caregiver_id = create_res.json()["id"]

    # Link to patient 1
    link_payload = {
        "patient_id": 1,
        "caregiver_id": caregiver_id,
        "relationship_type": "Primary Nurse",
        "is_primary": True,
    }
    link_res = client.post("/api/v1/caregivers/link-patient", json=link_payload)
    assert link_res.status_code == 200
    assert link_res.json()["success"] is True

    # Check assigned patients
    patients_res = client.get(f"/api/v1/caregivers/{caregiver_id}/patients")
    assert patients_res.status_code == 200
    assert len(patients_res.json()) >= 1
