"""
Health Check Tests
"""
import pytest
from fastapi import status

def test_basic_health_check(client):
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api_gateway"

def test_detailed_health_check(client):
    """Test detailed health check"""
    response = client.get("/health/detailed")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "dependencies" in data

def test_readiness_probe(client):
    """Test Kubernetes readiness probe"""
    response = client.get("/ready")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
    data = response.json()
    assert "ready" in data

def test_liveness_probe(client):
    """Test Kubernetes liveness probe"""
    response = client.get("/live")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["alive"] is True

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "version" in data