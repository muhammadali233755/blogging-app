from datetime import datetime
from typing import Optional, List
from pydantic import Field, constr
from schemas.base import ResponseBase, IDMixin, TimestampMixin
from schemas.user import UserResponse
from schemas.category import CategoryResponse

class PostBase(ResponseBase):
    """Base schema for post-related data."""
    title: constr(min_length=3, max_length=100) = Field(
        ..., 
        description="Post title",
        example="My First Blog Post"
    )
    content: constr(min_length=10) = Field(
        ..., 
        description="Post content",
        example="This is the content of my first blog post."
    )
    category_id: int = Field(
        ..., 
        description="Category ID",
        gt=0,
        example=1
    )

class PostCreate(PostBase):
    """Schema for creating a new post."""
    pass

class PostUpdate(ResponseBase):
    """Schema for updating an existing post."""
    title: Optional[constr(min_length=3, max_length=100)] = Field(
        None, 
        description="Updated post title",
        example="My Updated Blog Post"
    )
    content: Optional[constr(min_length=10)] = Field(
        None, 
        description="Updated post content",
        example="This is the updated content of my blog post."
    )
    category_id: Optional[int] = Field(
        None, 
        description="Updated category ID",
        gt=0,
        example=2
    )

class CommentSummary(ResponseBase, IDMixin):
    """Summary schema for comments in post responses."""
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    user_id: int = Field(..., description="Commenter ID")

class LikeSummary(ResponseBase, IDMixin):
    """Summary schema for likes in post responses."""
    user_id: int = Field(..., description="User ID who liked the post")

class PostResponse(PostBase, IDMixin, TimestampMixin):
    """Schema for post response data."""
    user_id: int = Field(..., description="Author ID")
    user: UserResponse = Field(..., description="Post author")
    category: CategoryResponse = Field(..., description="Post category")
    comment_count: Optional[int] = Field(0, description="Number of comments")
    like_count: Optional[int] = Field(0, description="Number of likes")
    view_count: Optional[int] = Field(0, description="Number of views")

class PostDetailResponse(PostResponse):
    """Schema for detailed post response including comments and likes."""
    comments: Optional[List[CommentSummary]] = Field([], description="Post comments")
    likes: Optional[List[LikeSummary]] = Field([], description="Post likes")
