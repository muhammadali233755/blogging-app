from datetime import datetime
from pydantic import Field, constr
from typing import Optional

from schemas.base import ResponseBase, IDMixin, TimestampMixin
from schemas.user import UserResponse

class CommentBase(ResponseBase):
    """Base schema for comment-related data."""
    content: constr(min_length=1, max_length=500) = Field(
        ..., 
        description="Comment content",
        example="This is a great post!"
    )
    post_id: int = Field(
        ..., 
        description="ID of the post being commented on",
        gt=0,
        example=1
    )

class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    pass

class CommentUpdate(ResponseBase):
    """Schema for updating an existing comment."""
    content: Optional[constr(min_length=1, max_length=500)] = Field(
        None, 
        description="Updated comment content",
        example="Updated comment text"
    )

class CommentResponse(CommentBase, IDMixin, TimestampMixin):
    """Schema for comment response data."""
    user_id: int = Field(..., description="ID of the comment author")
    user: Optional[UserResponse] = Field(None, description="Comment author")
