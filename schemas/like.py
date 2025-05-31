

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