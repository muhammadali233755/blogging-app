from pydantic import Field, constr
from typing import List, Optional
from schemas.base import ResponseBase, IDMixin, TimestampMixin
from schemas.post import PostResponse

class CategoryBase(ResponseBase):
    """Base schema for category-related data."""
    name: constr(min_length=2, max_length=30) = Field(
        ..., 
        description="Category name",
        example="Technology"
    )

class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass

class CategoryUpdate(ResponseBase):
    """Schema for updating an existing category."""
    name: Optional[constr(min_length=2, max_length=30)] = Field(
        None,
        description="Updated category name",
        example="Updated Technology"
    )

class CategoryResponse(CategoryBase, IDMixin, TimestampMixin):
    """Schema for category response data."""
    posts: Optional[List[PostResponse]] = Field(
        default=[],
        description="Posts in this category"
    )
