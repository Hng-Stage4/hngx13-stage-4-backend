from pydantic import BaseModel
from typing import Optional

class StatusResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    message: str
    meta: Optional[Dict] = None
