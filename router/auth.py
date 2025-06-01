from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from starlette import status

from model import User, RoleEnum
from schemas.user import UserCreate, UserResponse
from utils import db_dependency
from database import SessionLocal
from config import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "user": "Regular user access",
        "admin": "Administrator access"
    }
)

class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload model."""
    username: str
    user_id: int
    role: str
    scopes: list[str] = []
    exp: datetime

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Create a new JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user by username and password."""
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not bcrypt_context.verify(password, user.password):
            return None
        return user
    except Exception as e:
        # Log the error here if you have logging configured
        return None

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register_user(user_data: UserCreate, db: db_dependency):
    """Register a new user."""
    try:
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        hashed_password = bcrypt_context.hash(user_data.password)
        user = User(
            username=user_data.username,
            password=hashed_password,
            role=RoleEnum.USER
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post(
    "/token",
    response_model=Token,
    summary="Login to get access token"
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """Get access token using username and password."""
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "role": user.role.value,
                "scopes": form_data.scopes
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_access_token(
            data={
                "sub": user.username,
                "id": user.id,
                "role": user.role.value,
                "refresh": True
            },
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token"
)
async def refresh_token(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    """Get new access token using refresh token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username = payload.get("sub")
        user_id = payload.get("id")
        role = payload.get("role")
        
        if not all([username, user_id, role]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify user still exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(
            data={
                "sub": username,
                "id": user_id,
                "role": role
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_access_token(
            data={
                "sub": username,
                "id": user_id,
                "role": role,
                "refresh": True
            },
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency
) -> User:
    """Get current user from token."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        role = payload.get("role")
        token_scopes = payload.get("scopes", [])
        
        if not all([username, user_id, role]):
            raise credentials_exception
            
        token_data = TokenData(
            username=username,
            user_id=user_id,
            role=role,
            scopes=token_scopes,
            exp=payload.get("exp")
        )
        
        # Verify user still exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise credentials_exception
            
    except (JWTError, ValidationError):
        raise credentials_exception
        
    # Verify required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
            
    return user

# Create a dependency for getting the current user
user_dependency = Annotated[User, Depends(get_current_user)]

# Create a dependency specifically for admin users
def get_admin_user(user: user_dependency) -> User:
    """Verify that the current user has admin role."""
    if user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return user

admin_dependency = Annotated[User, Depends(get_admin_user)]
