# ============================================
# api-gateway/app/schemas/response_schema.py
# ============================================
from typing import Generic, TypeVar, Optional

# Type variable must be defined before any fallback GenericModel that uses it
T = TypeVar("T")

# Use GenericModel for proper support of generic pydantic models in type
# checkers and FastAPI. This requires pydantic to be installed in the
# analysis environment.
try:
    # pydantic v1
    from pydantic.generics import GenericModel
except Exception:
    # pydantic v2+ exposes GenericModel directly from pydantic; if neither
    # import is available during static analysis, we fall back to a tiny
    # shim so the code remains importable for editors.
    from pydantic import BaseModel as _BaseModel

    class GenericModel(_BaseModel, Generic[T]):
        pass

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total: int
    limit: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ApiResponse(GenericModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: str
    meta: Optional[PaginationMeta] = None
