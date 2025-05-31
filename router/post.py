from fastapi import APIRouter, HTTPException
from main import user_dependency,db_dependency
from model import Category, Post
from schemas.post import PostCreate,PostResponse,PostUpdate
from starlette import status



router = APIRouter(
    prefix="/posts",
    tags=["posts"])


@router.post("/")
def CreatePost(db:db_dependency,user:user_dependency,post_data:PostCreate):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = "Authentication Required")
    category = db.query(Category).filter(Category.id == post_data.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
    create_post=Post(title=post_data.title,content=post_data.content,user_id=user["id"],category_id=post_data.category_id)
    db.add(create_post)
    db.commit()
    db.refresh(create_post)
    return create_post




@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: db_dependency):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    return post




@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: int,update_data: PostUpdate,user: user_dependency,db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    if post.user_id != user["id"] and user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Insufficient permissions")
    
    
    if update_data.title:
        post.title = update_data.title
    if update_data.content:
        post.content = update_data.content
    if update_data.category_id:
        category = db.query(Category).filter(Category.id == update_data.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
        post.category_id = update_data.category_id
    
    db.commit()
    db.refresh(post)
    return post






@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int,user: user_dependency,db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    
  
    if post.user_id != user["id"] and user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Insufficient permissions")
    db.delete(post)
    db.commit()