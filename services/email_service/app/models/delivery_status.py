from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeliveryStatus(BaseModel):
    correlation_id: str
    status: str  # sent, failed, bounced, delivered
    provider: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    retry_count: int = 0
