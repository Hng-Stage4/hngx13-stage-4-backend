from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class VersionBase(BaseModel):
    version_number: int
    subject: Optional[str] = None
    body: str
    changes: Optional[str] = None

class VersionCreate(VersionBase):
    template_id: str

class Version(VersionBase):
    id: int
    template_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class VersionResponse(BaseModel):
    success: bool
    data: Optional[Version] = None
    error: Optional[str] = None
    message: str
    meta: Optional[Dict] = None
