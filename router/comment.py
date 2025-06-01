from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from typing import List

from model import Comment, Post, User
from schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from schemas.base import PaginationParams, PagedResponse
from utils import db_dependency, user_dependency

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new comment"
)
async def create_comment(
    comment_data: CommentCreate,
    db: db_dependency,
    user: user_dependency
):
    """
    Create a new comment on a post.
    
    Args:
        comment_data: Comment content and post ID
        db: Database session
        user: Authenticated user
        
    Returns:
        The created comment
        
    Raises:
        401: If user is not authenticated
        404: If post does not exist
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    new_comment = Comment(
        content=comment_data.content,
        user_id=user["id"],
        post_id=comment_data.post_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get(
    "/posts/{post_id}",
    response_model=PagedResponse[CommentResponse],
    summary="Get comments for a post"
)
async def get_post_comments(
    post_id: int,
    db: db_dependency,
    pagination: PaginationParams = Depends()
):
    """
    Get all comments for a specific post with pagination.
    
    Args:
        post_id: ID of the post
        db: Database session
        pagination: Pagination parameters
        
    Returns:
        Paginated list of comments
        
    Raises:
        404: If post does not exist
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    query = db.query(Comment).filter(Comment.post_id == post_id)\
        .order_by(Comment.created_at.desc())
    
    total = query.count()
    comments = query.offset(pagination.skip).limit(pagination.limit).all()
    
    page = pagination.skip // pagination.limit + 1
    pages = (total + pagination.limit - 1) // pagination.limit
    
    return PagedResponse[CommentResponse](
        items=comments,
        total=total,
        page=page,
        size=pagination.limit,
        pages=pages
    )

@router.get(
    "/users/{user_id}",
    response_model=PagedResponse[CommentResponse],
    summary="Get comments by user"
)
async def get_user_comments(
    user_id: int,
    db: db_dependency,
    pagination: PaginationParams = Depends()
):
    """
    Get all comments by a specific user with pagination.
    
    Args:
        user_id: ID of the user
        db: Database session
        pagination: Pagination parameters
        
    Returns:
        Paginated list of comments
        
    Raises:
        404: If user does not exist
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = db.query(Comment).filter(Comment.user_id == user_id)\
        .order_by(Comment.created_at.desc())
    
    total = query.count()
    comments = query.offset(pagination.skip).limit(pagination.limit).all()
    
    page = pagination.skip // pagination.limit + 1
    pages = (total + pagination.limit - 1) // pagination.limit
    
    return PagedResponse[CommentResponse](
        items=comments,
        total=total,
        page=page,
        size=pagination.limit,
        pages=pages
    )

@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment"
)
async def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    db: db_dependency,
    user: user_dependency
):
    """
    Update an existing comment.
    
    Args:
        comment_id: ID of the comment to update
        update_data: Updated comment content
        db: Database session
        user: Authenticated user
        
    Returns:
        The updated comment
        
    Raises:
        401: If user is not authenticated
        403: If user is not the comment author
        404: If comment does not exist
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.user_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )
    
    if update_data.content is not None:
        comment.content = update_data.content
    
    db.commit()
    db.refresh(comment)
    return comment

@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment"
)
async def delete_comment(
    comment_id: int,
    db: db_dependency,
    user: user_dependency
):
    """
    Delete a comment.
    
    Args:
        comment_id: ID of the comment to delete
        db: Database session
        user: Authenticated user
        
    Raises:
        401: If user is not authenticated
        403: If user is not the comment author or admin
        404: If comment does not exist
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.user_id != user["id"] and user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    db.delete(comment)
    db.commit()
