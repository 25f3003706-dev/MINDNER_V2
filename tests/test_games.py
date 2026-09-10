"""Tests for Cognitive Games endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_games():
    response = client.get("/api/v1/games")
    assert response.status_code == 200
    games = response.json()
    assert isinstance(games, list)
    assert len(games) >= 5
    game_keys = [g["game_key"] for g in games]
    assert "memory_match" in game_keys
    assert "object_recognition" in game_keys


def test_get_game_by_key():
    response = client.get("/api/v1/games/memory_match")
    assert response.status_code == 200
    data = response.json()
    assert data["game_key"] == "memory_match"
    assert data["category"] == "memory"
    assert data["max_level"] == 10
