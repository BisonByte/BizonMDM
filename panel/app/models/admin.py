from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .base import Base

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
