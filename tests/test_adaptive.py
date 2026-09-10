"""Tests for Adaptive Difficulty logic."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_adaptive_difficulty_increase():
    payload = {
        "patient_id": 1,
        "game_key": "memory_match",
        "current_level": 2,
        "recent_accuracies": [90.0, 95.0, 92.0],
        "recent_reaction_times": [750.0, 720.0],
        "consecutive_failures": 0,
        "consecutive_successes": 3,
    }
    response = client.post("/api/v1/adaptive/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["adjustment_action"] == "increase"
    assert data["recommended_level"] == 3


def test_adaptive_difficulty_decrease():
    payload = {
        "patient_id": 1,
        "game_key": "memory_match",
        "current_level": 4,
        "recent_accuracies": [40.0, 45.0],
        "recent_reaction_times": [3200.0, 3500.0],
        "consecutive_failures": 2,
        "consecutive_successes": 0,
    }
    response = client.post("/api/v1/adaptive/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["adjustment_action"] == "decrease"
    assert data["recommended_level"] == 3
    assert data["suggested_hints_enabled"] is True
