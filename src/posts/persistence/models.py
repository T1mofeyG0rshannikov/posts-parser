from datetime import datetime

import pytz
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from posts.persistence.db.database import Model


class PostOrm(Model):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    description = Column(String)

    published = Column(Date)

    h1 = Column(String)
    image = Column(String)
    content = Column(Text)
    content2 = Column(Text)

    slug = Column(String)

    active = Column(Boolean)
    tags = relationship("PostTagOrm", back_populates="post")


class TagOrm(Model):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True)

    posts = relationship("PostTagOrm", back_populates="tag")


class PostTagOrm(Model):
    __tablename__ = "posttags"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship(PostOrm, back_populates="tags")

    tag_id = Column(Integer, ForeignKey("tags.id"))
    tag = relationship(TagOrm, back_populates="posts")


class UserOrm(Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hash_password = Column(String)
    is_superuser = Column(Boolean, default=False)

    def __str__(self) -> str:
        return self.username


class ErrorLogOrm(Model):
    __tablename__ = "errorlog"

    id = Column(Integer, index=True, primary_key=True)
    title = Column(String)
    message = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(pytz.timezone("Europe/Moscow")))
