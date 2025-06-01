import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Enum, ForeignKey, Index, Integer, 
    String, DateTime, Text, func
)
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database import Base


class RoleEnum(enum.Enum):
    """User role enumeration."""
    USER = "USER"
    ADMIN = "ADMIN"


class Category(Base):
    """Category model for blog posts."""
    __tablename__ = "categories"
    __table_args__ = (
        {'comment': 'Categories for blog posts'}
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        comment="Primary key"
    )
    name: Mapped[str] = mapped_column(
        String(30), 
        unique=True, 
        nullable=False,
        comment="Category name"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        back_populates="category",
        cascade="all, delete-orphan"
    )


class User(Base):
    """User model for blog authentication and authorization."""
    __tablename__ = "users"
    __table_args__ = (
        {'comment': 'Users for the blogging application'}
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        comment="Primary key"
    )
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
        comment="Unique username"
    )
    password: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Hashed password"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Account creation timestamp"
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum), 
        default=RoleEnum.USER,
        nullable=False,
        comment="User role (USER or ADMIN)"
    )

    # Relationships
    posts: Mapped[List["Post"]] = relationship(
        "Post", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    views: Mapped[List["View"]] = relationship(
        "View", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )


class Post(Base):
    """Blog post model."""
    __tablename__ = "posts"
    __table_args__ = (
        Index('ix_posts_user_id', 'user_id'),
        Index('ix_posts_category_id', 'category_id'),
        {'comment': 'Blog posts'}
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        comment="Primary key"
    )
    title: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        comment="Post title"
    )
    content: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="Post content"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Author ID"
    )
    category_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("categories.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Category ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="posts"
    )
    category: Mapped["Category"] = relationship(
        "Category", 
        back_populates="posts"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )
    views: Mapped[List["View"]] = relationship(
        "View", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )


class Comment(Base):
    """Comment model for blog posts."""
    __tablename__ = "comments"
    __table_args__ = (
        Index('ix_comments_user_id', 'user_id'),
        Index('ix_comments_post_id', 'post_id'),
        {'comment': 'Comments on blog posts'}
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        comment="Primary key"
    )
    content: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        comment="Comment content"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Commenter ID"
    )
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("posts.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Post ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="comments"
    )
    post: Mapped["Post"] = relationship(
        "Post", 
        back_populates="comments"
    )


class Like(Base):
    """Like model for blog posts."""
    __tablename__ = "likes"
    __table_args__ = (
        Index('ix_likes_user_id', 'user_id'),
        Index('ix_likes_post_id', 'post_id'),
        {'comment': 'Likes on blog posts'}
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        comment="Primary key"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="User ID"
    )
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("posts.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Post ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Like timestamp"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="likes"
    )
    post: Mapped["Post"] = relationship(
        "Post", 
        back_populates="likes"
    )


class View(Base):
    """View model for tracking post views."""
    __tablename__ = "views"
    __table_args__ = (
        Index('ix_views_user_id', 'user_id'),
        Index('ix_views_post_id', 'post_id'),
        {'comment': 'Post view tracking'}
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        comment="Primary key"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Viewer ID"
    )
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("posts.id", ondelete="CASCADE"), 
        nullable=False,
        comment="Post ID"
    )
    view_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="View timestamp"
    )
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="Viewer IP address"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="views"
    )
    post: Mapped["Post"] = relationship(
        "Post", 
        back_populates="views"
    )
