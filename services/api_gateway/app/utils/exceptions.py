"""
Custom Exception Classes
"""
from fastapi import HTTPException, status

class APIException(HTTPException):
    """Base API Exception"""
    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(status_code=status_code, detail=message)

class NotFoundError(APIException):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="not_found",
            message=message
        )

class ValidationError(APIException):
    """Validation error"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="validation_error",
            message=message
        )

class UnauthorizedError(APIException):
    """Unauthorized access"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="unauthorized",
            message=message
        )

class ForbiddenError(APIException):
    """Forbidden access"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="forbidden",
            message=message
        )

class InternalServerError(APIException):
    """Internal server error"""
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="internal_server_error",
            message=message
        )