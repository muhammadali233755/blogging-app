import enum
from  database import Base
from sqlalchemy import Enum, Integer,String,DateTime,ForeignKey,func,Text
from sqlalchemy.orm import mapped_column,Mapped,relationship
from  datetime import datetime





class Category(Base):
    __tablename__ = "categorys"


    id :Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(30),unique=True)
    
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")
    
    
    

class Comment(Base):
    __tablename__ = "comments"



    id :Mapped[int] = mapped_column(primary_key=True)
    content:Mapped[str] = mapped_column(String(150))
    user_id :Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    post_id :Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    created_at :Mapped[datetime]= mapped_column(DateTime,default=func.now())
    
    
    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    

class Like(Base):

    __tablename__ = "likes"


    id :Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int]  = mapped_column(ForeignKey("users.id"))
    post_id :Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    created_at:Mapped[datetime]  = mapped_column(DateTime,default=func.now())
    
    
    user: Mapped["User"] = relationship("User", back_populates="likes")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")
    
    
class Post(Base):
    __tablename__ = "posts"


    id :Mapped[int] = mapped_column(primary_key=True)
    title :Mapped[str] = mapped_column(String(50),unique=True)
    content :Mapped[str] = mapped_column(Text)
    user_id :Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id :Mapped[int] = mapped_column(ForeignKey("categorys.id"))
    created_at:Mapped[datetime]  = mapped_column(DateTime,default=func.now())
    updated_at:Mapped[datetime]  = mapped_column(DateTime,default=func.now(),onupdate=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="posts")
    category: Mapped["Category"] = relationship("Category", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post")
    views: Mapped[list["View"]] = relationship("View", back_populates="post")
    
    
class RoleEnum(enum.Enum):
    USER="USER"
    ADMIN="ADMIN"

class User(Base):
    __tablename__ = "users"
    id :Mapped[int] = mapped_column(primary_key=True)
    username :Mapped[str] = mapped_column(String(50),unique=True)
    password :Mapped[str] = mapped_column(String(100))
    created_at:Mapped[datetime]  = mapped_column(DateTime,default=func.now())
    
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), 
        default=RoleEnum.USER,
        nullable=False
    )
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user")
    views: Mapped[list["View"]] = relationship("View", back_populates="user")
   
    
class View(Base):
    __tablename__ = "views"


    id :Mapped[int] = mapped_column(primary_key=True)
    user_id :Mapped[int]= mapped_column(ForeignKey("users.id"))
    post_id:Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    view_at:Mapped[datetime] = mapped_column(DateTime,default=func.now())
    ip_address:Mapped[str] = mapped_column(String)
    
    
    user: Mapped["User"] = relationship("User", back_populates="views")
    post: Mapped["Post"] = relationship("Post", back_populates="views")