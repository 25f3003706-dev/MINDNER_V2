"""Tests for Patient CRUD endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_patients():
    response = client.get("/api/v1/patients")
    assert response.status_code == 200
    patients = response.json()
    assert isinstance(patients, list)
    assert len(patients) >= 1


def test_create_get_and_update_patient():
    new_patient = {
        "first_name": "Clara",
        "last_name": "Barton",
        "age": 79,
        "gender": "Female",
        "stage": "Mild",
        "baseline_score": 76.0,
        "notes": "Test patient profile",
    }
    # Create
    create_res = client.post("/api/v1/patients", json=new_patient)
    assert create_res.status_code == 201
    created = create_res.json()
    patient_id = created["id"]
    assert created["first_name"] == "Clara"

    # Get
    get_res = client.get(f"/api/v1/patients/{patient_id}")
    assert get_res.status_code == 200
    assert get_res.json()["last_name"] == "Barton"

    # Update
    update_res = client.put(f"/api/v1/patients/{patient_id}", json={"notes": "Updated note"})
    assert update_res.status_code == 200
    assert update_res.json()["notes"] == "Updated note"

    # Cleanup
    del_res = client.delete(f"/api/v1/patients/{patient_id}")
    assert del_res.status_code == 200
