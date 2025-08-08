from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .base import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user = Column(String(255))
    action = Column(String(255))
    target = Column(String(255))
    ip = Column(String(45))
    ua = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    result = Column(String(50))
