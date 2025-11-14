from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeliveryStatusEnum(str, Enum):
    sent = "sent"
    failed = "failed"

class DeliveryStatus(BaseModel):
    notification_id: str
    status: DeliveryStatusEnum
    timestamp: datetime
    error: Optional[str] = None
