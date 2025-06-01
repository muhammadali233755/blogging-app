from datetime import datetime
from pydantic import Field
from typing import Optional, List
from schemas.base import ResponseBase, IDMixin, TimestampMixin
from schemas.user import UserResponse

class LikeBase(ResponseBase):
    """Base schema for like-related data."""
    post_id: int = Field(
        ..., 
        description="ID of the liked post",
        gt=0,
        example=1
    )

class LikeCreate(LikeBase):
    """Schema for creating a new like."""
    pass

class LikeResponse(LikeBase, IDMixin):
    """Schema for like response data."""
    user_id: int = Field(..., description="ID of the user who liked")
    created_at: datetime = Field(..., description="Like timestamp")
    user: Optional[UserResponse] = Field(None, description="User who liked")

class PostLikesResponse(ResponseBase):
    """Schema for post likes summary."""
    post_id: int = Field(..., description="Post ID")
    like_count: int = Field(..., description="Number of likes")
    likes: List[LikeResponse] = Field(..., description="List of likes")



# from pydantic import BaseModel
# from datetime import datetime

# from schemas.post import PostResponse
# from schemas.user import UserResponse


# class LikeBase(BaseModel):
#     user_id :int
    
    
# class LikeCreate(LikeBase):
#     pass
    
    
    
# class LikeResponse(LikeBase):
    
#     id : int
#     user_id : int
#     created_at: datetime
#     user : UserResponse
#     post : PostResponse
    
    
# class Config:
#     from_attributes = True
    


# class LikeCountResponse(BaseModel):
#     post_id:int
#     count:int
    

# class LikeStatusResponse(BaseModel):
#     user_id : int
#     post_id : int
#     liked: bool