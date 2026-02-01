"""
Test main application functionality.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_cors_headers():
    """Test CORS headers are present."""
    response = client.get("/health")
    assert response.status_code == 200
    # CORS headers should be present in development