from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class EmailMessage(BaseModel):
    correlation_id: str
    to_email: str
    template_id: str
    variables: Dict[str, str]
    language: Optional[str] = "en"
    priority: Optional[str] = "normal"  # normal, high, low
    scheduled_at: Optional[datetime] = None
    retry_count: int = 0
