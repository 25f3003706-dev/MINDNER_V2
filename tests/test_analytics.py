"""Tests for Analytics and real-time score calculation endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_platform_overview():
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    assert "total_caregivers" in data
    assert "total_sessions" in data


def test_patient_domains():
    response = client.get("/api/v1/analytics/patient/1/domains")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_calculate_score():
    payload = {
        "patient_id": 1,
        "game_key": "memory_match",
        "level": 2,
        "duration_seconds": 90,
        "total_rounds": 10,
        "correct_rounds": 9,
        "avg_reaction_time_ms": 750.0,
        "mistake_count": 1,
    }
    response = client.post("/api/v1/analytics/calculate-score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert data["domain"] == "memory"
    assert data["accuracy_percentage"] == 90.0
    assert data["performance_tier"] in ["High", "Standard", "Moderate", "Requires Support"]
