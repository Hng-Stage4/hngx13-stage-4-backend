from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class EmailRequest(BaseModel):
    correlation_id: str
    to_email: str
    template_id: str
    variables: Dict[str, str]
    priority: Optional[str] = "normal"
    scheduled_at: Optional[datetime] = None

class EmailResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    message: str
    meta: Optional[Dict] = None
