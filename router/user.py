from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from typing import List

from model import User
from schemas.user import UserResponse, UserUpdate
from utils import db_dependency, user_dependency
from router.auth import bcrypt_context

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information"
)
async def get_current_user(
    user: user_dependency,
    db: db_dependency
):
    """
    Get the current authenticated user's information.
    
    Args:
        user: Current authenticated user
        db: Database session
        
    Returns:
        Current user's information
        
    Raises:
        401: If user is not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    db_user = db.query(User).filter(User.id == user["id"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return db_user

@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user"
)
async def update_current_user(
    update_data: UserUpdate,
    db: db_dependency,
    user: user_dependency
):
    """
    Update the current authenticated user's information.
    
    Args:
        update_data: Updated user data
        db: Database session
        user: Current authenticated user
        
    Returns:
        Updated user information
        
    Raises:
        401: If user is not authenticated
        404: If user not found
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    db_user = db.query(User).filter(User.id == user["id"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if update_data.password:
        hashed_password = bcrypt_context.hash(update_data.password)
        db_user.password = hashed_password
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed"
        )

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user"
)
async def delete_current_user(
    db: db_dependency,
    user: user_dependency
):
    """
    Delete the current authenticated user's account.
    
    Args:
        db: Database session
        user: Current authenticated user
        
    Raises:
        401: If user is not authenticated
        404: If user not found
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    db_user = db.query(User).filter(User.id == user["id"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        db.delete(db_user)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
async def get_user(
    user_id: int,
    db: db_dependency
):
    """
    Get a user's public information by their ID.
    
    Args:
        user_id: ID of the user to retrieve
        db: Database session
        
    Returns:
        User information
        
    Raises:
        404: If user not found
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return db_user
