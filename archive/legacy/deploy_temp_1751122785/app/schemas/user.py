from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user data."""
    
    email: EmailStr
    username: str
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user data in the database."""
    
    id: int
    hashed_password: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class User(UserBase):
    """Schema for user data returned to clients."""
    
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""
    
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""
    
    sub: Optional[int] = None
    exp: Optional[datetime] = None
