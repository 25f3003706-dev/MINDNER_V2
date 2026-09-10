"""Tests for Patient Progress tracking."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_patient_progress():
    response = client.get("/api/v1/progress/patient/1")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == 1
    assert "patient_name" in data
    assert "stage" in data
    assert "overall_current_score" in data
    assert "domain_breakdown" in data
    assert isinstance(data["domain_breakdown"], list)
