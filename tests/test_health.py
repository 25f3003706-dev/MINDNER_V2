"""Tests for Health check endpoint and table discovery."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_ping():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "health" in data


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "connected"
    assert data["database"]["total_tables"] >= 13
    assert "patients" in data["database"]["discovered_tables"]
    assert "caregivers" in data["database"]["discovered_tables"]
    assert "cognitive_games" in data["database"]["discovered_tables"]
