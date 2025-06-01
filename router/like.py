from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from typing import List

from model import Like, Post
from schemas.like import LikeResponse, PostLikesResponse
from schemas.base import PaginationParams, PagedResponse
from utils import db_dependency, user_dependency

router = APIRouter(
    prefix="/likes",
    tags=["likes"]
)

@router.post(
    "/posts/{post_id}",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Like a post"
)
async def create_like(
    post_id: int,
    db: db_dependency,
    user: user_dependency
):
    """
    Like a specific post.
    
    Args:
        post_id: ID of the post to like
        db: Database session
        user: Authenticated user
        
    Returns:
        The created like
        
    Raises:
        401: If user is not authenticated
        404: If post does not exist
        400: If post is already liked by the user
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
    
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == user["id"]
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    new_like = Like(post_id=post_id, user_id=user["id"])
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like

@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike a post"
)
async def remove_like(
    post_id: int,
    db: db_dependency,
    user: user_dependency
):
    """
    Remove a like from a post.
    
    Args:
        post_id: ID of the post to unlike
        db: Database session
        user: Authenticated user
        
    Raises:
        401: If user is not authenticated
        404: If post does not exist or is not liked by the user
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == user["id"]
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    db.delete(like)
    db.commit()

@router.get(
    "/posts/{post_id}",
    response_model=PostLikesResponse,
    summary="Get likes for a post"
)
async def get_post_likes(
    post_id: int,
    db: db_dependency,
    pagination: PaginationParams = Depends()
):
    """
    Get all likes for a specific post with pagination.
    
    Args:
        post_id: ID of the post
        db: Database session
        pagination: Pagination parameters
        
    Returns:
        List of likes for the post and total count
        
    Raises:
        404: If post does not exist
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    query = db.query(Like).filter(Like.post_id == post_id)
    total = query.count()
    
    likes = query.offset(pagination.skip).limit(pagination.limit).all()
    
    return PostLikesResponse(
        post_id=post_id,
        like_count=total,
        likes=likes
    )

@router.get(
    "/users/{user_id}",
    response_model=PagedResponse[LikeResponse],
    summary="Get likes by user"
)
async def get_user_likes(
    user_id: int,
    db: db_dependency,
    pagination: PaginationParams = Depends()
):
    """
    Get all posts liked by a specific user with pagination.
    
    Args:
        user_id: ID of the user
        db: Database session
        pagination: Pagination parameters
        
    Returns:
        Paginated list of likes by the user
    """
    query = db.query(Like).filter(Like.user_id == user_id)
    total = query.count()
    
    likes = query.offset(pagination.skip).limit(pagination.limit).all()
    
    page = pagination.skip // pagination.limit + 1
    pages = (total + pagination.limit - 1) // pagination.limit
    
    return PagedResponse[LikeResponse](
        items=likes,
        total=total,
        page=page,
        size=pagination.limit,
        pages=pages
    )
