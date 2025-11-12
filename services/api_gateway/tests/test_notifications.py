"""
Notification Tests
"""
import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_create_notification(async_client, auth_headers, mock_notification_request):
    """Test creating a notification"""
    with patch('app.queue.producer.publish_notification', new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = True
        
        response = await async_client.post(
            "/api/v1/notifications/",
            json=mock_notification_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["success"] is True
        assert "notification_id" in data["data"]
        mock_publish.assert_called_once()

@pytest.mark.asyncio
async def test_create_notification_without_auth(async_client, mock_notification_request):
    """Test creating notification without authentication"""
    response = await async_client.post(
        "/api/v1/notifications/",
        json=mock_notification_request
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_notification_invalid_type(client, auth_headers):
    """Test creating notification with invalid type"""
    invalid_data = {
        "notification_type": "invalid_type",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "template_code": "test",
        "variables": {}

}
    response = client.post(
        "/api/v1/notifications/",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_bulk_notifications(async_client, auth_headers, mock_notification_request):
    """Test creating bulk notifications"""
    with patch('app.queue.producer.publish_notification', new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = True
        
        bulk_requests = [mock_notification_request for _ in range(5)]
        
        response = await async_client.post(
            "/api/v1/notifications/bulk",
            json=bulk_requests,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 5

@pytest.mark.asyncio
async def test_bulk_notifications_limit(async_client, auth_headers, mock_notification_request):
    """Test bulk notifications exceeding limit"""
    bulk_requests = [mock_notification_request for _ in range(101)]
    
    response = await async_client.post(
        "/api/v1/notifications/bulk",
        json=bulk_requests,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_notification_status(client, auth_headers):
    """Test getting notification status"""
    notification_id = "test-notif-001"
    response = client.get(
        f"/api/v1/notifications/{notification_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True