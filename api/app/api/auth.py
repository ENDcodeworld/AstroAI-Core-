"""
Authentication API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: dict


class RegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str
    name: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    - **email**: User email
    - **password**: User password
    """
    # TODO: Implement actual authentication
    
    # Mock successful login
    return LoginResponse(
        access_token="mock_jwt_token_here",
        expires_in=1800,  # 30 minutes
        user={
            "id": "user_123",
            "email": request.email,
            "name": "Test User",
            "plan": "free"
        }
    )


@router.post("/register")
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    - **email**: User email
    - **password**: User password
    - **name**: User name
    """
    # TODO: Implement registration
    
    return {
        "message": "Registration successful. Please check your email to verify.",
        "user_id": "user_123"
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    """
    # TODO: Implement token refresh
    
    return {
        "access_token": "new_mock_jwt_token",
        "expires_in": 1800
    }
