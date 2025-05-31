# from pydantic import BaseModel
# from datetime import datetime
# from schemas.user import UserResponse
# from schemas.post import PostResponse

# class CommentBase(BaseModel):
#     content: str
#     post_id: int

# class CommentCreate(CommentBase):
#     pass

# class CommentUpdate(BaseModel):
#     content: str | None = None

# class CommentResponse(CommentBase):
#     id: int
#     user_id: int
#     created_at: datetime
#     user: UserResponse
#     post: PostResponse

#     class Config:
#         from_attributes = True