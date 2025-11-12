"""
Authentication Tests
"""
import pytest
from fastapi import status

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "name": "New User",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == user_data["email"]

def test_register_duplicate_user(client):
    """Test registering duplicate user"""
    user_data = {
        "email": "duplicate@example.com",
        "name": "Duplicate User",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
    # First registration
    client.post("/api/v1/auth/register", json=user_data)
    # Duplicate registration
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client):
    """Test successful login"""
    # Register user first
    register_data = {
        "email": "logintest@example.com",
        "name": "Login Test",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }
    client.post("/api/v1/auth/register", json=register_data)
    
    # Login
    login_data = {
        "email": "logintest@example.com",
        "password": "TestPass123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

def test_verify_token(client, auth_token):
    """Test token verification"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/api/v1/auth/verify", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "user_id" in response.json()