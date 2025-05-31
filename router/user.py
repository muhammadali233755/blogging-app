# from fastapi import APIRouter, HTTPException
# from main import user_dependency,db_dependency
# from schemas.user import UserResponse, UserUpdate
# from model import User
# from auth import bcrypt_context





# router = APIRouter(
#     prefix="/users",
#     tags=["users"])



# @router.get("/me",response_model=UserResponse)
# def get_current_user(user:user_dependency,db:db_dependency):
#     if not user:
#         raise HTTPException(status_code=401,detail = "Unauthorized")
#     db_user = db.query(User).filter(User.id == user["id"]).first()
#     return db_user
    
    
    
    
    
# @router.patch("/me",response_model=UserResponse)
# def UpdateUser(db:db_dependency,user:user_dependency,update_data:UserUpdate):
#     if not user:
#         raise HTTPException(status_code=401,detail = "Unauthorized")
#     db_user = db.query(User).filter(User.id == user["id"]).first()
#     if update_data.password:db_user.password = bcrypt_context.hash(update_data.password)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
    
    
    
    
    
# router.delete("/me",status_code=204)
# def delete_current_user(db:db_dependency,user:user_dependency):
#     if not user:
#         raise HTTPException(status_code=401,detail = "Unauthorized")
#     db_user = db.query(User).filter(User.id == user["id"]).first()
#     db.delete(db_user)
#     db.commit() 