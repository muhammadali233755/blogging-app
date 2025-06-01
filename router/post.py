from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional

from model import Category, Post, User
from schemas.post import PostCreate, PostResponse, PostUpdate, PostDetailResponse
from schemas.base import PaginationParams, PagedResponse, MessageResponse
from utils import db_dependency, user_dependency
from starlette import status

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post(
    "/", 
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog post"
)
async def create_post(
    post_data: PostCreate,
    db: db_dependency,
    user: user_dependency
):
    """
    Create a new blog post.
    
    Args:
        post_data: Post data including title, content, and category
        db: Database session
        user: Authenticated user
        
    Returns:
        The created post
        
    Raises:
        401: If user is not authenticated
        404: If category does not exist
        400: If post title already exists
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    category = db.query(Category).filter(Category.id == post_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
        
    try:
        new_post = Post(
            title=post_data.title,
            content=post_data.content,
            user_id=user["id"],
            category_id=post_data.category_id
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists"
        )

@router.get(
    "/",
    response_model=PagedResponse[PostResponse],
    summary="Get all blog posts with pagination"
)
async def get_all_posts(
    db: db_dependency,
    pagination: PaginationParams = Depends(),
    category_id: Optional[int] = Query(None, description="Filter by category ID")
):
    """
    Get all blog posts with pagination and optional filtering.
    
    Args:
        db: Database session
        pagination: Pagination parameters (skip and limit)
        category_id: Optional category ID to filter posts
        
    Returns:
        Paginated list of posts
    """
    query = db.query(Post)
    
    if category_id:
        query = query.filter(Post.category_id == category_id)
    
    total = query.count()
    posts = query.offset(pagination.skip).limit(pagination.limit).all()
    
    page = pagination.skip // pagination.limit + 1
    pages = (total + pagination.limit - 1) // pagination.limit
    
    return PagedResponse[PostResponse](
        items=posts,
        total=total,
        page=page,
        size=pagination.limit,
        pages=pages
    )

@router.get(
    "/{post_id}", 
    response_model=PostDetailResponse,
    summary="Get a specific blog post by ID"
)
async def get_post(
    post_id: int, 
    db: db_dependency
):
    """
    Get a specific blog post by ID.
    
    Args:
        post_id: The ID of the post to retrieve
        db: Database session
        
    Returns:
        The requested post
        
    Raises:
        404: If post does not exist
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post

@router.patch(
    "/{post_id}", 
    response_model=PostResponse,
    summary="Update an existing blog post"
)
async def update_post(
    post_id: int,
    update_data: PostUpdate,
    db: db_dependency,
    user: user_dependency
):
    """
    Update an existing blog post.
    
    Args:
        post_id: The ID of the post to update
        update_data: Updated post data
        db: Database session
        user: Authenticated user
        
    Returns:
        The updated post
        
    Raises:
        401: If user is not authenticated
        403: If user does not have permission to update the post
        404: If post or category does not exist
        400: If updated title already exists
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    if post.user_id != user["id"] and user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        if update_data.title is not None:
            post.title = update_data.title
            
        if update_data.content is not None:
            post.content = update_data.content
            
        if update_data.category_id is not None:
            category = db.query(Category).filter(Category.id == update_data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
            post.category_id = update_data.category_id
        
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this title already exists"
        )

@router.delete(
    "/{post_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog post"
)
async def delete_post(
    post_id: int,
    db: db_dependency,
    user: user_dependency
):
    """
    Delete a blog post.
    
    Args:
        post_id: The ID of the post to delete
        db: Database session
        user: Authenticated user
        
    Raises:
        401: If user is not authenticated
        403: If user does not have permission to delete the post
        404: If post does not exist
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.user_id != user["id"] and user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
        
    db.delete(post)
    db.commit()
