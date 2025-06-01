from datetime import datetime
from pydantic import Field, IPvAnyAddress
from schemas.base import ResponseBase, IDMixin, TimestampMixin
from typing import Optional

class ViewBase(ResponseBase):
    """Base schema for view-related data."""
    ip_address: IPvAnyAddress = Field(
        ..., 
        description="IP address of the viewer",
        example="192.168.1.1"
    )

class ViewCreate(ViewBase):
    """Schema for creating a new view."""
    post_id: int = Field(..., description="ID of the viewed post", gt=0)
    user_id: Optional[int] = Field(None, description="ID of the viewer (if authenticated)", gt=0)

class ViewResponse(ViewBase, IDMixin):
    """Schema for view response data."""
    view_at: datetime = Field(..., description="Timestamp of the view")
    post_id: int = Field(..., description="ID of the viewed post")
    user_id: Optional[int] = Field(None, description="ID of the viewer (if authenticated)")

