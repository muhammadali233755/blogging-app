from pydantic import BaseModel
from schemas.post import PostResponse



class CategoryCreate(BaseModel):
    name:str
    
    
    
class CategoryResponse(BaseModel):
    id : int
    name: str
    post : list[PostResponse] = []
    
    
    
    
class Config:
    from_attributes = True
