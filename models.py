from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date
import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    request_count = Column(Integer, default=0)
    last_request_date = Column(Date, nullable=True)
    language = Column(String, default="english")

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
