"""
Pytest Configuration and Fixtures
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.auth.jwt_handler import create_access_token

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
async def async_client():
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_token():
    """Create a valid auth token for testing"""
    token = create_access_token(
        data={"sub": "test@example.com", "role": "user", "name": "Test User"}
    )
    return token

@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def mock_notification_request():
    """Mock notification request data"""
    return {
        "notification_type": "email",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "template_code": "welcome_email",
        "variables": {"name": "Test User", "link": "https://example.com"},
        "request_id": "test-req-001",
        "priority": 5
    }