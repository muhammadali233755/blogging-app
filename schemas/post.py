from pydantic import BaseModel
from datetime import datetime
from schemas.user import UserResponse
from schemas.category import CategoryResponse

class PostBase(BaseModel):
    title: str
    content: str
    category_id: int

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None

class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    category: CategoryResponse

    class Config:
        from_attributes = True