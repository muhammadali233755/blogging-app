
# from main import db_dependency,user_dependency



# from fastapi import APIRouter, HTTPException,status

# from model import Like, Post


# router = APIRouter()


# @router.post("/posts/{post_id}",status_code=status.HTTP_201_CREATED)
# def create_like(post_id:int,db:db_dependency,user:user_dependency):
#     if not user:
#         raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = "Authentication required")
#     post = db.query(Post).filter(Post.id == post_id).first()
#     if not post:
#         raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Post not exist")
#     existing_like =  db.query(Like).filter(Like.post_id==post_id,Like.user_id==user["id"]).first()
#     if existing_like:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post already liked")
#     new_like = Like(post_id=post_id,user_id=user["id"])
#     db.add(new_like)
#     db.commit()
#     return {"message":{" Post Liked Successfull"}}
    
    
    