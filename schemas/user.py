from datetime import datetime
from pydantic import BaseModel




class UserCreate(BaseModel):
    username: str
    password: str
    role_id: int = 2 


class UserResponse(BaseModel):
    id: int
    username: str
    role: str  
    created_at: datetime


    class Config:
        from_attributes = True  
        
class UserUpdate(BaseModel):
    password:str   | None = None