# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from schemas.comment import CommentCreate, CommentResponse, CommentUpdate
# from model import User,Post,Comment
# from main import db_dependency
# from auth import user_dependency





# router = APIRouter(
#     prefix="/comments",
#     tags=["comments"])





# @router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
# def create_comment(comment_data: CommentCreate,user: user_dependency,db: db_dependency):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    
   
#     post = db.query(Post).filter(Post.id == comment_data.post_id).first()
#     if not post:
#         raise HTTPException( status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
#     new_comment = Comment(content=comment_data.content,user_id=user["id"],post_id=comment_data.post_id)
#     db.add(new_comment)
#     db.commit()
#     db.refresh(new_comment)
#     return new_comment









# @router.get("/post/{post_id}", response_model=list[CommentResponse])
# def get_comments_for_post(post_id: int,db: db_dependency,skip: int = Query(0, ge=0, description="Pagination offset"),
#                           limit: int = Query(10, le=100, description="Items per page")):
   
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    
#     comments = (db.query(Comment)
#         .filter(Comment.post_id == post_id)
#         .order_by(Comment.created_at.desc())
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )
#     return comments










# @router.get("/user/{user_id}", response_model=list[CommentResponse])
# def get_comments_by_user(
#     user_id: int,
#     db: db_dependency,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, le=100)):
   
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
#     comments = (
#         db.query(Comment)
#         .filter(Comment.user_id == user_id)
#         .order_by(Comment.created_at.desc())
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )
#     return comments








# @router.patch("/{comment_id}", response_model=CommentResponse)
# def update_comment(comment_id: int,update_data: CommentUpdate,user: user_dependency,db: db_dependency):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    
#     comment = db.query(Comment).filter(Comment.id == comment_id).first()
#     if not comment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found")
    
    
#     if comment.user_id != user["id"]:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You can only update your own comments")
    
   
#     if update_data.content:
#         comment.content = update_data.content
    
#     db.commit()
#     db.refresh(comment)
#     return comment












# @router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_comment( comment_id: int, user: user_dependency, db: db_dependency):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication required")
    
#     comment = db.query(Comment).filter(Comment.id == comment_id).first()
#     if not comment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found")
    
   
#     if comment.user_id != user["id"] and user.get("role") != "admin":
#         raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
#     db.delete(comment)
#     db.commit()