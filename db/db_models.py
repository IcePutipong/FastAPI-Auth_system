from sqlalchemy import Column, Integer, String, Date, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    employment_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)

    emails = relationship("Email", back_populates ="user")

class Email(Base):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True, index=True)
    employment_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

    user = relationship("User", back_populates="emails")

