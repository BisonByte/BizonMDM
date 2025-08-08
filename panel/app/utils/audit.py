from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import AuditLog
from .config_loader import load_config

def audit(user_id, action, target, result):
    """Persist a minimal audit log entry"""
    cfg = load_config()
    dsn = cfg.get('DSN')
    if not dsn:
        return
    engine = create_engine(dsn)
    Session = sessionmaker(bind=engine)
    session = Session()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    log = AuditLog(user=user_id, action=action, target=target, ip=ip, ua=ua, result=result)
    session.add(log)
    session.commit()
    session.close()
    engine.dispose()
