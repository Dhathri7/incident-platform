from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse