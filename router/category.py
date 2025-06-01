from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from typing import List

from model import Category
from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from schemas.base import PaginationParams, PagedResponse
from utils import db_dependency, user_dependency

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    db: db_dependency,
    user: user_dependency
):
    if not user or user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    new_category = Category(name=category_data.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get(
    "/",
    response_model=PagedResponse[CategoryResponse]
)
async def get_all_categories(
    db: db_dependency,
    pagination: PaginationParams = Depends()
):
    query = db.query(Category)
    total = query.count()
    
    categories = query.offset(pagination.skip).limit(pagination.limit).all()
    
    page = pagination.skip // pagination.limit + 1
    pages = (total + pagination.limit - 1) // pagination.limit
    
    return PagedResponse[CategoryResponse](
        items=categories,
        total=total,
        page=page,
        size=pagination.limit,
        pages=pages
    )

@router.get(
    "/{category_id}/posts",
    response_model=CategoryResponse
)
async def get_category_posts(
    category_id: int,
    db: db_dependency
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.patch(
    "/{category_id}",
    response_model=CategoryResponse
)
async def update_category(
    category_id: int,
    update_data: CategoryUpdate,
    db: db_dependency,
    user: user_dependency
):
    if not user or user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if update_data.name is not None:
        existing_category = db.query(Category).filter(
            Category.name == update_data.name,
            Category.id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
        
        category.name = update_data.name
        db.commit()
        db.refresh(category)
    
    return category

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    db: db_dependency,
    user: user_dependency
):
    if not user or user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db.delete(category)
    db.commit()
