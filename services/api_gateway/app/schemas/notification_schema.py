# ============================================
# api-gateway/app/schemas/notification_schema.py
# ============================================
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict
from enum import Enum
from datetime import datetime


class NotificationType(str, Enum):
    email = "email"
    push = "push"


class NotificationStatus(str, Enum):
    delivered = "delivered"
    pending = "pending"
    failed = "failed"


class UserData(BaseModel):
    name: str
    link: HttpUrl
    meta: Optional[Dict] = None


class NotificationRequest(BaseModel):
    notification_type: NotificationType
    user_id: str
    template_code: str
    variables: UserData
    request_id: str
    priority: int = Field(default=1, ge=1, le=10)
    metadata: Optional[Dict] = None


class NotificationResponse(BaseModel):
    notification_id: str
    status: NotificationStatus
    message: str


class StatusUpdateRequest(BaseModel):
    notification_id: str
    status: NotificationStatus
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
