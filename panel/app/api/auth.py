import secrets
import time
from flask import Blueprint, request, jsonify, current_app
from passlib.hash import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt
from ..models import Admin, JWTBlacklist
from ..utils.config_loader import load_config
from ..utils.audit import audit
from ..app import limiter

bp = Blueprint('auth', __name__)

def issue_tokens(sub, secret):
    jti_access = secrets.token_hex(16)
    jti_refresh = secrets.token_hex(16)
    now = int(time.time())
    access = jwt.encode({
        'sub': sub,
        'exp': now + 1800,
        'type': 'access',
        'jti': jti_access
    }, secret, algorithm='HS256')
    refresh = jwt.encode({
        'sub': sub,
        'exp': now + 2592000,
        'type': 'refresh',
        'jti': jti_refresh
    }, secret, algorithm='HS256')
    return access, refresh


def revoke_jti(session, jti, reason="rotated"):
    if not session.query(JWTBlacklist).filter_by(jti=jti).first():
        session.add(JWTBlacklist(jti=jti, reason=reason))
        session.commit()


@bp.route('/auth/login', methods=['POST'])
@limiter.limit('5 per 10 seconds')
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
        access, refresh = issue_tokens(admin.email, current_app.secret_key)
        success = True
        response = jsonify({'access': access, 'refresh': refresh})
    else:
        response = jsonify({'error': 'invalid_credentials'}), 401
    audit(data.get('email'), 'login', 'self', 'success' if success else 'failure')
    session.close()
    engine.dispose()
    return response

@bp.route('/auth/refresh', methods=['POST'])
@limiter.limit('5 per 10 seconds')
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
    if payload.get('type') != 'refresh':
        return jsonify({'error': 'invalid_token'}), 401
    cfg = load_config()
    engine = create_engine(cfg['DSN'])
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(JWTBlacklist).filter_by(jti=payload.get('jti')).first():
        session.close()
        engine.dispose()
        return jsonify({'error': 'invalid_token'}), 401
    access, refresh_token = issue_tokens(payload['sub'], current_app.secret_key)
    revoke_jti(session, payload.get('jti'))
    session.close()
    engine.dispose()
    return jsonify({'access': access, 'refresh': refresh_token})


@bp.route('/auth/logout', methods=['POST'])
@limiter.limit('5 per 10 seconds')
def logout():
    auth = request.headers.get('Authorization', '')
    refresh = request.headers.get('X-Refresh-Token')
    cfg = load_config()
    engine = create_engine(cfg['DSN'])
    Session = sessionmaker(bind=engine)
    session = Session()
    user = None
    for token in [auth.replace('Bearer ', '') if auth.startswith('Bearer ') else None, refresh]:
        if not token:
            continue
        try:
            payload = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            continue
        revoke_jti(session, payload.get('jti'), reason='logout')
        user = payload.get('sub')
    session.close()
    engine.dispose()
    audit(user, 'logout', 'self', 'success')
    return jsonify({'ok': True})
