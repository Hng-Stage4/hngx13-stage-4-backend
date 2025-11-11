# ============================================
# api-gateway/app/schemas/response_schema.py
# ============================================
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class PaginationMeta(BaseModel):
    total: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: str
    meta: Optional[PaginationMeta] = None