from datetime import datetime
from typing import Optional
from pydantic import Field, constr
from schemas.base import ResponseBase, IDMixin, TimestampMixin

class UserBase(ResponseBase):
    """Base schema for user-related data."""
    username: constr(min_length=3, max_length=50) = Field(
        ..., 
        description="User's unique username", 
        example="johndoe"
    )

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: constr(min_length=8) = Field(
        ..., 
        description="User's password (min 8 characters)",
        example="securePassword123"
    )
    role_id: int = Field(2, description="User role ID (default: regular user)")

class UserUpdate(ResponseBase):
    """Schema for updating an existing user."""
    password: Optional[constr(min_length=8)] = Field(
        None, 
        description="User's new password (min 8 characters)",
        example="newSecurePassword456"
    )

class UserResponse(UserBase, IDMixin, TimestampMixin):
    """Schema for user response data."""
    role: str = Field(..., description="User's role name", example="USER")
