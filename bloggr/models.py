from __future__ import annotations
from . import db
from flask_security.core import UserMixin, RoleMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, Text, UniqueConstraint


# Roles-Users Core/Association table (Many To Many)
roles_users = db.Table(
    "roles_users", 
    db.Column("role_id", Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    db.Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
)


# Creates a "Role" table with three columns.
class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)           # type: ignore
    name: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)           # type: ignore
    description: Mapped[str | None] = mapped_column(db.String(255))           # type: ignore
    users: Mapped[List[User]] = relationship(secondary=roles_users, back_populates="roles")


# Creates a "User" table with five columns.
class User(db.Model, UserMixin):            
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)           # type: ignore
    username: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)           # type: ignore
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)           # type: ignore
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)           # type: ignore
    active: Mapped[bool] = mapped_column(default=True)           # type: ignore
    fs_uniquifier: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)           # type: ignore
    confirmed_at: Mapped[datetime | None] = mapped_column(db.DateTime, nullable=True)           # type: ignore
    roles: Mapped[List[Role]] = relationship(secondary=roles_users, back_populates="users")           # type: ignore
    posts: Mapped[List[Post]] = relationship(backref="author", lazy=True)
    comments: Mapped[List[Comment]] = relationship(back_populates="user", lazy=True)
    votes: Mapped[List[Vote]] = relationship(back_populates="user", lazy=True)


# Creates a "Post" table with five columns.
class Post(db.Model):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(50), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(db.Date, nullable=False)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    comments: Mapped[List[Comment]] = relationship(back_populates="post", cascade="all, delete-orphan", lazy=True)
    votes: Mapped[List[Vote]] = relationship(back_populates="post", cascade="all, delete-orphan", lazy=True)

    @property
    def like_count(self) -> int:
        return sum(1 for vote in self.votes if vote.is_like)

    @property
    def dislike_count(self) -> int:
        return sum(1 for vote in self.votes if not vote.is_like)


# Creates a "Comment" table for viewer comments on posts.
class Comment(db.Model):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("post.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    post: Mapped[Post] = relationship(back_populates="comments")
    user: Mapped[User] = relationship(back_populates="comments")


# Creates a "Vote" table for likes and dislikes (one vote per user per post).
class Vote(db.Model):
    __tablename__ = "vote"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_vote_post_user"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("post.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    is_like: Mapped[bool] = mapped_column(db.Boolean, nullable=False)
    post: Mapped[Post] = relationship(back_populates="votes")
    user: Mapped[User] = relationship(back_populates="votes")