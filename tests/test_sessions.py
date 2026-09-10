"""Tests for Game Sessions recording and retrieval."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_sessions():
    session_payload = {
        "patient_id": 1,
        "game_id": 1,
        "level": 3,
        "duration_seconds": 115,
        "status": "completed",
        "score": 89.0,
        "accuracy_percentage": 92.0,
        "reaction_time_ms": 780.0,
        "device_info": "Tablet Browser Test",
    }
    response = client.post("/api/v1/sessions", json=session_payload)
    assert response.status_code == 201
    created = response.json()
    assert created["score"] == 89.0
    assert created["patient_id"] == 1

    # Fetch patient sessions
    list_res = client.get("/api/v1/sessions/patient/1")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert len(sessions) >= 1
