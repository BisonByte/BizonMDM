import datetime
from flask import Blueprint, request, jsonify, current_app
from passlib.hash import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt
from ..models import Admin, AuditLog
from ..utils.config_loader import load_config
from ..app import limiter

bp = Blueprint('auth', __name__)

@bp.route('/auth/login', methods=['POST'])
@limiter.limit('10/hour')
def login():
    data = request.get_json() or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'missing_fields'}), 400
    cfg = load_config()
    engine = create_engine(cfg['DSN'])
    Session = sessionmaker(bind=engine)
    session = Session()
    admin = session.query(Admin).filter_by(email=data['email']).first()
    success = False
    if admin and bcrypt.verify(data['password'], admin.password_hash):
        payload = {
            'sub': admin.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, current_app.secret_key, algorithm='HS256')
        success = True
        response = jsonify({'token': token})
    else:
        response = jsonify({'error': 'invalid_credentials'}), 401
    log = AuditLog(
        user=data.get('email'),
        action='login',
        target='self',
        ip=request.remote_addr,
        ua=request.headers.get('User-Agent'),
        result='success' if success else 'failure'
    )
    session.add(log)
    session.commit()
    session.close()
    engine.dispose()
    return response

@bp.route('/auth/refresh', methods=['POST'])
def refresh():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'missing_token'}), 401
    token = token.replace('Bearer ', '')
    try:
        payload = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'expired_token'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'invalid_token'}), 401
    new_payload = {
        'sub': payload['sub'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    new_token = jwt.encode(new_payload, current_app.secret_key, algorithm='HS256')
    return jsonify({'token': new_token})
