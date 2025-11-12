"""
Authentication Models
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterRequest(BaseModel):
    """User registration request model"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class TokenResponse(BaseModel):
    """Token response model"""
    success: bool = True
    message: str
    data: dict
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }

class UserResponse(BaseModel):
    """User response model"""
    success: bool = True
    message: str
    data: dict
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "User retrieved successfully",
                "data": {
                    "email": "user@example.com",
                    "name": "John Doe",
                    "role": "user"
                }
            }
        }

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # Subject (user email)
    role: str = "user"
    name: str
    exp: Optional[int] = None
    iat: Optional[int] = None