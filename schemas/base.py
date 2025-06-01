from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, validator, EmailStr, constr

# Type variable for generic models
T = TypeVar('T')

class TimestampMixin(BaseModel):
    """Base mixin for models with created_at and updated_at timestamps."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class IDMixin(BaseModel):
    """Base mixin for models with ID field."""
    id: int = Field(..., description="Unique identifier", gt=0)

class PaginationParams(BaseModel):
    """Parameters for pagination."""
    skip: int = Field(0, description="Number of items to skip", ge=0)
    limit: int = Field(10, description="Maximum number of items to return", ge=1, le=100)

class PagedResponse(BaseModel, Generic[T]):
    """Generic paged response wrapper."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ResponseBase(BaseModel):
    """Base model for all response schemas."""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    details: Optional[Dict[str, Any]] = None

