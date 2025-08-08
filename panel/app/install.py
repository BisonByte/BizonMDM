import os
import stat
import re
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from ..app import limiter
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from passlib.hash import bcrypt
from .models import Admin
from ..utils.audit import audit

bp = Blueprint('install', __name__)

INSTALL_FLAG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.installed'))


@bp.before_request
def block_if_installed():
    if os.path.exists(INSTALL_FLAG):
        return jsonify({"error": "El instalador está deshabilitado."}), 403


def strong(pw: str) -> bool:
    return len(pw) >= 14 and re.search(r"[A-Z]", pw) and re.search(r"[a-z]", pw) and re.search(r"\d", pw)


@bp.route('/install', methods=['POST'])
@limiter.limit("5 per 10 seconds")
def install():
    data = request.get_json() or {}
    required = ['app_url', 'db_host', 'db_name', 'db_user', 'db_pass', 'admin_email', 'admin_pass']
    if not all(data.get(k) for k in required):
        return jsonify({'error': 'missing_fields'}), 400
    if not strong(data['admin_pass']):
        return jsonify({'error': 'Contraseña admin débil (mín 14, mayúscula, minúscula y número).'}), 400
    dsn = f"mysql+pymysql://{data['db_user']}:{data['db_pass']}@{data['db_host']}:3306/{data['db_name']}?charset=utf8mb4"
    try:
        engine = create_engine(dsn)
        with engine.connect() as conn:
            conn.execute('SELECT 1')
    except Exception:
        return jsonify({'error': 'No se pudo conectar a la base de datos. Revisa host/usuario/contraseña.'}), 400

    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'config.ini')
    try:
        with open(config_path, 'w') as f:
            f.write('[app]\n')
            f.write(f'app_url = {data["app_url"]}\n')
            f.write('installed = 1\n')
            f.write('\n[database]\n')
            f.write(f'dsn = {dsn}\n')
        os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        return jsonify({'error': 'No se puede escribir config. Ajusta permisos (600) y propietario.'}), 400

    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', os.path.join(os.path.dirname(__file__), 'migrations'))
    alembic_cfg.set_main_option('sqlalchemy.url', dsn)
    command.upgrade(alembic_cfg, 'head')

    Session = sessionmaker(bind=engine)
    session = Session()
    admin = Admin(email=data['admin_email'], password_hash=bcrypt.hash(data['admin_pass']))
    session.add(admin)
    session.commit()
    session.close()
    engine.dispose()

    # write installation flag
    with open(INSTALL_FLAG, 'w') as f:
        f.write('1\n')

    audit(data['admin_email'], 'install', 'system', 'success')

    return jsonify({'ok': True})
