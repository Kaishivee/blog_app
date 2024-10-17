from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)
    slug = Column(String, unique=True, index=True)

    posts = relationship("Post", backref='users')


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    slug = Column(String, unique=True, index=True)

    user_id = Column(Integer, ForeignKey('users.id'))
