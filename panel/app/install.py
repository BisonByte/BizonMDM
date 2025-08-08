import os
import stat
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from ..app import limiter
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from passlib.hash import bcrypt
from .models import Admin, AuditLog

bp = Blueprint('install', __name__)

@bp.route('/install', methods=['POST'])
@limiter.limit("5/hour")
def install():
    data = request.get_json() or {}
    required = ['app_url', 'db_host', 'db_name', 'db_user', 'db_pass', 'admin_email', 'admin_pass']
    if not all(data.get(k) for k in required):
        return jsonify({'error': 'missing_fields'}), 400
    if len(data['admin_pass']) < 14:
        return jsonify({'error': 'weak_password'}), 400
    dsn = f"mysql+pymysql://{data['db_user']}:{data['db_pass']}@{data['db_host']}:3306/{data['db_name']}?charset=utf8mb4"
    try:
        engine = create_engine(dsn)
        with engine.connect() as conn:
            conn.execute('SELECT 1')
    except Exception as e:
        return jsonify({'error': 'db_connection_failed', 'details': str(e)}), 400

    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'config.ini')
    with open(config_path, 'w') as f:
        f.write('[app]\n')
        f.write(f'app_url = {data["app_url"]}\n')
        f.write('installed = 1\n')
        f.write('\n[database]\n')
        f.write(f'dsn = {dsn}\n')
    os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', os.path.join(os.path.dirname(__file__), 'migrations'))
    alembic_cfg.set_main_option('sqlalchemy.url', dsn)
    command.upgrade(alembic_cfg, 'head')

    Session = sessionmaker(bind=engine)
    session = Session()
    admin = Admin(email=data['admin_email'], password_hash=bcrypt.hash(data['admin_pass']))
    session.add(admin)
    log = AuditLog(user=data['admin_email'], action='install', target='system', ip=request.remote_addr, ua=request.headers.get('User-Agent'), result='success')
    session.add(log)
    session.commit()
    session.close()
    engine.dispose()

    return jsonify({'ok': True})
