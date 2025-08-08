from datetime import datetime
from sqlalchemy import Column, String, DateTime
from .base import Base

class JWTBlacklist(Base):
    __tablename__ = 'jwt_blacklist'
    jti = Column(String(64), primary_key=True)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reason = Column(String(64))
