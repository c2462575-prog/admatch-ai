"""User-related Pydantic models for API request/response."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(advertiser|creator)$")
    display_name: str = Field(..., min_length=1, max_length=100)
    referral_code: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    display_name: str
    plan: str = "free"
    matches_used_this_month: int = 0


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
