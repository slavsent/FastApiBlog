from sqlalchemy import Column, String, Integer, Text, ForeignKey, inspect, Boolean, DateTime, func, text
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from core.db import Base
from sqlalchemy.dialects.postgresql import UUID


class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(80), unique=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=False)


class UsersPosts(Base):
    __tablename__ = "users_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id))
    posts = Column(Text)
    dt_created = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    dt_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("Users", cascade="all, delete", backref="users")


class Likes(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey(UsersPosts.id))
    user_id = Column(UUID(as_uuid=True), ForeignKey(Users.id))
    likes_on = Column(Boolean)

    users = relationship("Users", cascade="all, delete", backref="children")
    posts_id = relationship("UsersPosts", cascade="all, delete", backref="users_posts_like")


class TokensTable(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires = Column(DateTime())
    user = Column(UUID(as_uuid=True), ForeignKey(Users.id))

    users_id = relationship("Users", cascade="all, delete", backref="users_token")
