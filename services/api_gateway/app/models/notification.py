"""
Notification Models
"""

from pydantic import BaseModel, UUID4, Field, HttpUrl
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class NotificationType(str, Enum):
    """Notification type enum"""

    email = "email"
    push = "push"
    sms = "sms"  # For future extension


class NotificationStatus(str, Enum):
    """Notification status enum"""

    queued = "queued"
    processing = "processing"
    delivered = "delivered"
    failed = "failed"
    pending = "pending"


class NotificationRequest(BaseModel):
    """Notification request model"""

    notification_type: NotificationType
    user_id: UUID4
    template_code: str = Field(..., min_length=1, max_length=100)
    variables: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=10)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "notification_type": "email",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "template_code": "welcome_email",
                "variables": {"name": "John Doe", "link": "https://example.com/verify"},
                "request_id": "req-12345",
                "priority": 5,
                "metadata": {"campaign_id": "camp-001"},
            }
        }


class NotificationResponse(BaseModel):
    """Notification response model"""

    success: bool
    message: str
    data: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Notification queued successfully",
                "data": {
                    "notification_id": "notif-12345",
                    "status": "queued",
                    "notification_type": "email",
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                },
            }
        }


class NotificationListResponse(BaseModel):
    """Notification list response model"""

    success: bool
    message: str
    data: list
    meta: Dict[str, Any]


class NotificationStatusUpdate(BaseModel):
    """Status update model"""

    notification_id: str
    status: NotificationStatus
    timestamp: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "notification_id": "notif-12345",
                "status": "delivered",
                "timestamp": "2024-11-11T10:30:00Z",
                "error": None,
            }
        }


class UserData(BaseModel):
    """User data for notifications"""

    name: str
    link: HttpUrl
    meta: Optional[Dict[str, Any]] = None
