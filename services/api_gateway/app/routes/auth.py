"""
Authentication Routes
Handles login, registration, and token verification
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from app.auth.jwt_handler import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password
)
from app.auth.models import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.config import get_settings

router = APIRouter()
security = HTTPBearer()
settings = get_settings()

# In-memory user store (Replace with database in production)
fake_users_db = {}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Register a new user
    """
    # Check if user exists
    if user_data.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Store user
    fake_users_db[user_data.email] = {
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hashed_password,
        "active": True,
        "role": "user"
    }
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "email": user_data.email,
            "name": user_data.name,
            "role": "user"
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Login and get access token
    """
    # Get user from database
    user = fake_users_db.get(credentials.email)
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": credentials.email,
            "role": user["role"],
            "name": user["name"]
        },
        expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    }

@router.post("/verify")
async def verify_auth(authorization: Optional[str] = Header(None)):
    """
    Verify JWT token (used by Traefik ForwardAuth)
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization header"
        )
    
    # Extract token
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = verify_token(token)
        return {
            "user_id": payload.get("sub"),
            "role": payload.get("role", "user"),
            "name": payload.get("name", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current user information
    """
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "User retrieved successfully",
        "data": {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user (token blacklisting can be added here)
    """
    # In production, add token to blacklist in Redis
    return {
        "success": True,
        "message": "Logged out successfully",
        "data": None
    }