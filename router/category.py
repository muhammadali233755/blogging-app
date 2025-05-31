from utills import db_dependency,user_dependency
from fastapi import APIRouter, HTTPException,status
from model import Category as CategoryModel

from pydantic import BaseModel
from schemas.post import PostResponse



class CategoryCreate(BaseModel):
    name:str
    
    
    
class CategoryResponse(BaseModel):
    id : int
    name: str
    post : list[PostResponse] = []
    
    
    


router = APIRouter(prefix="/categories", tags=["categories"])



@router.post("/",response_model=CategoryResponse,status_code=status.HTTP_201_CREATED)
def create_category(data_category:CategoryCreate,db:db_dependency,user:user_dependency):
    if  not user or user.get("role") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail = ("Admin previliges required"))
    existing_category = db.query(CategoryModel),filter(CategoryModel.name == data_category.name)
    if existing_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Category already exists")


    new_category = CategoryModel(name=data_category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category






router.get('/',response_model= list[CategoryResponse])
def get_all_category(db:db_dependency):
    category = db.query(CategoryModel).all()
    return category






router.get("/category_id/posts",response_model=list[CategoryResponse])
def get_post_by_category(category_id:int,db:db_dependency):
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Category not found")
    return category.posts





router.delete('/category_id',status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id:int,db:db_dependency,user:user_dependency):
    if not user or user.get("role") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail = "Admin previliges required")
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Category not found")
    db.delete(category)
    db.commit()
    
    
    
    

        