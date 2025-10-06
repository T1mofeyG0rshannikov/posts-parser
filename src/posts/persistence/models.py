from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from posts.persistence.db.database import Model


class PostOrm(Model):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    description = Column(String)
    published = Column(Time)

    h1 = Column(String)
    image = Column(String)
    content = Column(Text)
    content2 = Column(Text)

    slug = Column(String)

    active = Column(Boolean)
    tags = relationship("PostTagOrm", back_populates="post")


class PostTagOrm(Model):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String)

    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship(PostOrm, back_populates="tags")


class UserOrm(Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hash_password = Column(String)
    is_superuser = Column(Boolean, default=False)

    def __str__(self) -> str:
        return self.username
