# ============================================
# api-gateway/app/utils/response_formatter.py
# ============================================
from typing import Any, Optional
from app.schemas.response_schema import ApiResponse, PaginationMeta


def format_response(
    success: bool,
    data: Any = None,
    error: str = None,
    message: str = "",
    meta: PaginationMeta = None
) -> dict:
    """
    Format API response consistently
    """
    return ApiResponse(
        success=success,
        data=data,
        error=error,
        message=message,
        meta=meta
    ).dict()


def format_error_response(error: str, message: str = "Request failed") -> dict:
    """
    Format error response
    """
    return format_response(
        success=False,
        error=error,
        message=message
    )