from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    subject: Optional[str] = None
    body: str
    language: str = "en"

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    language: Optional[str] = None

class Template(TemplateBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TemplateRenderRequest(BaseModel):
    variables: Dict[str, Any]
    language: Optional[str] = "en"

class TemplateRenderResponse(BaseModel):
    subject: Optional[str] = None
    body: str

class TemplateResponse(BaseModel):
    success: bool
    data: Optional[Template] = None
    error: Optional[str] = None
    message: str
    meta: Optional[Dict] = None
