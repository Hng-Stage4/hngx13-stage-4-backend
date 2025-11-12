"""
Standard API Response Models
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response format"""

    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None
    meta: Optional[PaginationMeta] = None

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "error": None,
                "message": "Operation successful",
                "meta": {
                    "total": 100,
                    "limit": 10,
                    "page": 1,
                    "total_pages": 10,
                    "has_next": True,
                    "has_previous": False,
                },
            }
        }


class ErrorResponse(BaseModel):
    """Error response format"""

    success: bool = False
    message: str
    error: str
    data: Optional[Any] = None

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "An error occurred",
                "error": "invalid_request",
                "data": None,
            }
        }
