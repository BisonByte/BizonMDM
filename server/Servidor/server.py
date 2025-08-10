"""Servidor REST utilizado por la aplicación BizonMDM.

Ahora almacena la información en una base de datos SQLite en lugar de
mantener todo en memoria. Permite opcionalmente proteger los endpoints
mediante un token firmado mediante JWT.
"""

from flask import Flask, request, jsonify, send_file
import os
import json
import base64
import io
import qrcode
import logging
import hmac
import hashlib
import urllib.request
import time
from functools import wraps

from models import (
    Device,
    LogEntry,
    Command,
    SessionLocal,
    init_db,
    Admin,
    User,
    Client,
    Store,
)
from sqlalchemy import text

app = Flask(__name__)


# Configuración ---------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, '.env')
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as fh:
        for line in fh:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k, v)

JWT_SECRET = os.getenv("JWT_SECRET")
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")
FCM_URL = "https://fcm.googleapis.com/fcm/send"
logging.basicConfig(filename="server.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def encode_jwt(
    sub: str,
    secret: str,
    role: str,
    client_id: str | None = None,
    store_id: int | None = None,
    expires_in: int = 3600,
) -> str:
    """Genera un token JWT con soporte de rol, client_id, store_id y expiración."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": sub, "role": role, "exp": now + int(expires_in)}
    if client_id is not None:
        payload["client_id"] = client_id
    if store_id is not None:
        payload["store_id"] = store_id
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt(token: str, secret: str) -> dict:
    """Decodifica un token JWT y devuelve su payload."""
    header_b64, payload_b64, signature_b64 = token.split(".")
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = _b64url_decode(signature_b64)
    expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid signature")
    payload = json.loads(_b64url_decode(payload_b64))
    # Validaciones básicas del payload
    if not isinstance(payload, dict):
        raise ValueError("Invalid payload")
    for field in ("sub", "role", "exp"):
        if field not in payload:
            raise ValueError("Missing claim")
    if int(payload["exp"]) < int(time.time()):
        raise ValueError("Token expired")
    if payload["role"] == "client":
        if not payload.get("client_id") or not payload.get("store_id"):
            raise ValueError("Missing client_id or store_id")
    if payload["role"] == "user" and not payload.get("store_id"):
        raise ValueError("Missing store_id")
    return payload


def require_auth(request) -> dict | None:
    """Valida el encabezado Authorization mediante JWT si está configurado.

    Devuelve el payload con los campos ``role`` y ``client_id`` si el token es
    válido. Si la autenticación no está habilitada, retorna un diccionario vacío.
    En caso de fallo devuelve ``None``.
    """
    if not JWT_SECRET:
        return {}
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        return decode_jwt(token, JWT_SECRET)
    except Exception:
        return None


def get_session():
    """Obtiene una nueva sesión de base de datos."""
    return SessionLocal()


def require_admin(func):
    """Decorator that allows only admin role."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = require_auth(request)
        if not auth or auth.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return func(*args, **kwargs)

    return wrapper


def require_client(func):
    """Decorator that enforces client role and exposes auth payload."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = require_auth(request)
        if (
            not auth
            or auth.get('role') != 'client'
            or not auth.get('client_id')
            or not auth.get('store_id')
        ):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return func(*args, auth=auth, **kwargs)

    return wrapper


def require_user(func):
    """Decorator that enforces user role and exposes auth payload."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = require_auth(request)
        if not auth or auth.get('role') != 'user' or not auth.get('store_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return func(*args, auth=auth, **kwargs)

    return wrapper


@app.route('/api/stores', methods=['GET', 'POST'])
def api_stores():
    auth = require_auth(request)
    if not auth:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    with get_session() as db:
        if request.method == 'GET':
            if auth.get('role') == 'admin':
                stores = db.query(Store).all()
            elif auth.get('role') == 'user':
                stores = db.query(Store).filter_by(id=auth.get('store_id')).all()
            else:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            result = [{'id': s.id, 'name': s.name} for s in stores]
            return jsonify(result), 200
        if auth.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = request.get_json() or {}
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'message': 'name requerido'}), 400
        store = Store(name=name)
        db.add(store)
        db.commit()
        return jsonify({'id': store.id, 'name': store.name}), 201


@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    auth = require_auth(request)
    if not auth:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    with get_session() as db:
        if request.method == 'GET':
            if auth.get('role') == 'admin':
                users = db.query(User).all()
            elif auth.get('role') == 'user':
                users = db.query(User).filter_by(username=auth.get('sub')).all()
            else:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            result = [
                {
                    'id': u.id,
                    'username': u.username,
                    'role': u.role,
                    'store_id': u.store_id,
                }
                for u in users
            ]
            return jsonify(result), 200
        if auth.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        store_id = data.get('store_id')
        if not username or not password or store_id is None:
            return jsonify({'success': False, 'message': 'username, password y store_id requeridos'}), 400
        store = db.query(Store).filter_by(id=store_id).first()
        if not store:
            return jsonify({'success': False, 'message': 'Store not found'}), 404
        user = User(username=username, role=role, store_id=store_id)
        user.set_password(password)
        db.add(user)
        db.commit()
        return jsonify({'id': user.id, 'username': user.username, 'store_id': user.store_id}), 201


@app.route('/login', methods=['POST'])
def login():
    """Endpoint de autenticación que devuelve un JWT según el usuario."""
    if not JWT_SECRET:
        return jsonify({'success': False, 'message': 'Auth disabled'}), 400
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    client_id = data.get('client_id')
    with get_session() as db:
        if username and password:
            admin = db.query(Admin).filter_by(username=username).first()
            if admin and admin.check_password(password):
                token = encode_jwt(username, JWT_SECRET, role='admin')
                return jsonify({'token': token}), 200
            user = db.query(User).filter_by(username=username).first()
            if user and user.check_password(password):
                token = encode_jwt(username, JWT_SECRET, role='user', store_id=user.store_id)
                return jsonify({'token': token}), 200
        if client_id:
            device = db.query(Device).filter_by(device_id=client_id).first()
            if device and device.clients:
                store_id = device.clients[0].store_id
                token = encode_jwt(
                    client_id,
                    JWT_SECRET,
                    role='client',
                    client_id=client_id,
                    store_id=store_id,
                )
                return jsonify({'token': token}), 200
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


def _generate_provisioning_string(server_url: str, device_id: str, skip_encryption: bool = True) -> str:
    """Devuelve la cadena en base64 utilizada para el aprovisionamiento por QR."""
    data = {
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME":
            "com.example.mdmjive/com.example.mdmjive.receivers.MDMDeviceAdminReceiver",
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION":
            f"{server_url}/downloads/mdm.apk",
        "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": skip_encryption,
        "serverUrl": server_url,
        "deviceId": device_id,
    }
    json_data = json.dumps(data)
    return base64.b64encode(json_data.encode("utf-8")).decode("utf-8")


@app.route('/provisioning/qr/<device_id>', methods=['GET'])
def get_provisioning_qr(device_id: str):
    """Genera y devuelve un código QR para aprovisionar el dispositivo."""
    server_url = request.url_root.rstrip('/')
    qr_string = _generate_provisioning_string(server_url, device_id)
    img = qrcode.make(qr_string)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

def _register_device():
    """Registra un dispositivo a partir de un JSON enviado por la app."""
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            device = Device(
                device_id=device_id,
                imei=data.get('imei'),
                model=data.get('model'),
                serial=data.get('serial'),
                info=json.dumps(data),
                fcm_token=data.get('fcmToken'),
            )
            db.add(device)
        else:
            device.imei = data.get('imei')
            device.model = data.get('model')
            device.serial = data.get('serial')
            device.info = json.dumps(data)
            if data.get('fcmToken'):
                device.fcm_token = data.get('fcmToken')
        db.commit()
    logging.info('registro dispositivo %s', device_id)
    return jsonify({'success': True, 'message': 'Dispositivo registrado'}), 200


@app.route('/admin/devices/register', methods=['POST'])
@require_admin
def register_device_admin():
    """Endpoint protegido para registrar dispositivos."""
    return _register_device()


@app.route('/devices/register', methods=['POST'])
def register_device_public():
    """Endpoint público para registrar dispositivos."""
    return _register_device()

@app.route('/client/devices/status', methods=['POST'])
@require_client
def update_status(auth):
    """Actualiza el estado del dispositivo previamente registrado."""
    data = request.get_json() or {}
    device_id = data.get('deviceId') or auth.get('client_id')
    if device_id != auth.get('client_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    with get_session() as db:
        device = (
            db.query(Device)
            .join(Device.clients)
            .filter(Device.device_id == device_id, Client.store_id == auth.get('store_id'))
            .first()
        )
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        status = json.loads(device.status or '{}')
        for field in (
            'status',
            'rootAttempt',
            'emulator',
            'unknownSources',
            'lastSync',
            'battery',
            'wipeDetected',
            'bootloaderTampered',
        ):
            if field in data:
                status[field] = data[field]
        device.status = json.dumps(status)
        if data.get('fcmToken'):
            device.fcm_token = data.get('fcmToken')
        db.commit()
    return jsonify({'success': True, 'message': 'Estado actualizado'}), 200


@app.route('/admin/devices', methods=['GET'])
@require_admin
def list_devices():
    """Devuelve la lista de dispositivos registrados."""
    with get_session() as db:
        devices = db.query(Device).all()
        result = []
        for d in devices:
            status = json.loads(d.status or '{}')
            result.append({
                'deviceId': d.device_id,
                'imei': d.imei,
                'model': d.model,
                'serial': d.serial,
                'status': status,
            })
    return jsonify(result), 200

@app.route('/admin/devices/<device_id>', methods=['GET'])
@require_admin
def get_device_info(device_id: str):
    """Devuelve la información completa almacenada de un dispositivo."""
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        info = json.loads(device.info or '{}')
        status = json.loads(device.status or '{}')
        result = {
            'model': device.model or info.get('model'),
            'code': info.get('code'),
            'serial': device.serial or info.get('serial'),
            'activationLocation': info.get('activationLocation'),
            'addedDate': device.added.isoformat() if device.added else None,
            'email': info.get('email'),
            'phone': info.get('phone'),
            'imei': device.imei or info.get('imei'),
            'status': status,
        }
    return jsonify(result), 200


@app.route('/client/device', methods=['GET'])
@require_client
def get_own_device(auth):
    """Devuelve la información del dispositivo asociado al cliente."""
    device_id = auth.get('client_id')
    with get_session() as db:
        device = (
            db.query(Device)
            .join(Device.clients)
            .filter(Device.device_id == device_id, Client.store_id == auth.get('store_id'))
            .first()
        )
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        info = json.loads(device.info or '{}')
        status = json.loads(device.status or '{}')
        result = {
            'model': device.model or info.get('model'),
            'code': info.get('code'),
            'serial': device.serial or info.get('serial'),
            'activationLocation': info.get('activationLocation'),
            'addedDate': device.added.isoformat() if device.added else None,
            'email': info.get('email'),
            'phone': info.get('phone'),
            'imei': device.imei or info.get('imei'),
            'status': status,
        }
    return jsonify(result), 200

# --- Endpoints para manejo de logs ---

@app.route('/client/logs', methods=['POST'])
@require_client
def upload_logs(auth):
    """Recibe una lista de logs enviados por un dispositivo."""
    data = request.get_json() or {}
    logs = data.get('logs', [])
    device_id = auth.get('client_id')
    with get_session() as db:
        device = (
            db.query(Device)
            .join(Device.clients)
            .filter(Device.device_id == device_id, Client.store_id == auth.get('store_id'))
            .first()
        )
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        if isinstance(logs, list):
            for entry in logs:
                db.add(LogEntry(device_id=device.id, log=json.dumps(entry)))
            db.commit()
    return jsonify({'success': True, 'message': 'Logs recibidos', 'count': len(logs)}), 200


@app.route('/admin/logs/<device_id>', methods=['GET'])
@require_admin
def get_logs(device_id: str):
    """Devuelve los logs almacenados de un dispositivo."""
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        logs = [json.loads(l.log) for l in device.logs]
    return jsonify({'logs': logs}), 200

# --- Endpoints de control de dispositivos ---


def _queue_command(device_id: str, action: str, extra: dict | None = None):
    """Almacena un comando para el dispositivo indicado."""
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return False
        payload = {'deviceId': device_id, 'action': action}
        if extra:
            payload.update(extra)
        db.add(Command(device_id=device.id, command=json.dumps(payload)))
        db.commit()
        token = device.fcm_token
    return _send_fcm_message(token, payload)


def _send_fcm_message(token: str | None, payload: dict) -> bool:
    if not token or not FCM_SERVER_KEY:
        return True
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    body = {"to": token, "data": payload}
    try:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(FCM_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.getcode()
            if status != 200:
                logging.warning("Error enviando FCM: HTTP %s", status)
                return False
    except Exception as exc:
        logging.warning("Error enviando FCM: %s", exc)
        return False
    return True


@app.route('/api/status', methods=['GET'])
def api_status():
    """Verifica el estado básico del servidor y dependencias."""
    db_ok = False
    try:
        with get_session() as db:
            db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    firebase_ok = bool(FCM_SERVER_KEY)
    return jsonify({'database': db_ok, 'firebase': firebase_ok}), 200


@app.route('/admin/config/fcm', methods=['GET', 'POST'])
@require_admin
def api_config_fcm():
    global FCM_SERVER_KEY
    if request.method == 'POST':
        data = request.get_json() or {}
        key = data.get('key')
        if not key:
            return jsonify({'success': False, 'message': 'key requerido'}), 400
        FCM_SERVER_KEY = key.strip()
        env_lines = []
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, 'r', encoding='utf-8') as fh:
                env_lines = [l for l in fh.readlines() if not l.startswith('FCM_SERVER_KEY=')]
        env_lines.append(f'FCM_SERVER_KEY={FCM_SERVER_KEY}\n')
        with open(ENV_PATH, 'w', encoding='utf-8') as fh:
            fh.writelines(env_lines)
        os.environ['FCM_SERVER_KEY'] = FCM_SERVER_KEY
        return jsonify({'success': True, 'message': 'Clave de Firebase guardada correctamente'}), 200
    return jsonify({'key': FCM_SERVER_KEY or ''}), 200


@app.route('/admin/config/tenant/<tenant>', methods=['GET'])
@require_admin
def api_config_tenant(tenant: str):
    """Devuelve la configuración específica para un subdominio.

    Busca un archivo JSON en el directorio ``configs`` con el nombre del
    subdominio. Si no existe, intenta cargar ``default.json``. Si tampoco
    está presente, devuelve un objeto vacío con estado 404.
    """
    config_dir = os.path.join(BASE_DIR, 'configs')
    specific = os.path.join(config_dir, f'{tenant}.json')
    fallback = os.path.join(config_dir, 'default.json')
    path = specific if os.path.exists(specific) else fallback
    if not os.path.exists(path):
        return jsonify({}), 404
    with open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    return jsonify(data), 200


@app.route('/admin/test-fcm', methods=['POST'])
@require_admin
def api_test_fcm():
    with get_session() as db:
        devices = db.query(Device).all()
    for d in devices:
        _send_fcm_message(d.fcm_token, {'action': 'test_message'})
    return jsonify({'success': True, 'sent': len(devices)}), 200


@app.route('/admin/device/wipe', methods=['POST'])
@require_admin
def api_device_wipe():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_wipe'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/admin/device/reboot', methods=['POST'])
@require_admin
def api_device_reboot():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_reboot'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/admin/device/lock', methods=['POST'])
@require_admin
def api_device_lock():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_lock'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/admin/device/screenshot', methods=['POST'])
@require_admin
def api_device_screenshot():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_screenshot'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/admin/app/install', methods=['POST'])
@require_admin
def api_app_install():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    url = data.get('url')
    if not device_id or not url:
        return jsonify({'success': False, 'message': 'deviceId y url requeridos'}), 400
    if not _queue_command(device_id, 'app_install', {'url': url}):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/admin/app/uninstall', methods=['POST'])
@require_admin
def api_app_uninstall():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    package = data.get('package')
    if not device_id or not package:
        return jsonify({'success': False, 'message': 'deviceId y package requeridos'}), 400
    if not _queue_command(device_id, 'app_uninstall', {'package': package}):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200

@app.route('/admin/commands', methods=['POST'])
@require_admin
def add_command():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    action = data.get('action')
    if not device_id or not action:
        return jsonify({'success': False, 'message': 'deviceId y action requeridos'}), 400
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        db.add(Command(device_id=device.id, command=json.dumps(data)))
        db.commit()
    return jsonify({'success': True, 'message': 'Comando almacenado'}), 200


@app.route('/client/commands', methods=['GET'])
@require_client
def get_client_commands(auth):
    device_id = auth.get('client_id')
    with get_session() as db:
        device = (
            db.query(Device)
            .join(Device.clients)
            .filter(Device.device_id == device_id, Client.store_id == auth.get('store_id'))
            .first()
        )
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        cmds = [json.loads(c.command) for c in device.commands]
        for c in device.commands:
            db.delete(c)
        db.commit()
    return jsonify(cmds), 200


# --- Endpoints de administración de clientes ---


def _require_admin(auth):
    return auth and auth.get('role') == 'admin'


@app.route('/admin/clients', methods=['GET', 'POST'])
def admin_clients():
    auth = require_auth(request)
    if not _require_admin(auth):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if request.method == 'GET':
        with get_session() as db:
            clients = db.query(Client).all()
            result = []
            for c in clients:
                result.append({
                    'id': c.id,
                    'username': c.user.username,
                    'permissions': json.loads(c.permissions or '[]'),
                    'devices': [d.device_id for d in c.devices],
                })
        return jsonify(result), 200
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'username y password requeridos'}), 400
    permissions = data.get('permissions', [])
    devices = data.get('devices', [])
    store_id = data.get('store_id')
    with get_session() as db:
        user = User(username=username, role='client', store_id=store_id)
        user.set_password(password)
        client = Client(user=user, permissions=json.dumps(permissions), store_id=store_id)
        for device_id in devices:
            device = db.query(Device).filter_by(device_id=device_id).first()
            if device:
                client.devices.append(device)
        db.add(client)
        db.commit()
        return jsonify({'id': client.id}), 201


@app.route('/admin/clients/<int:client_id>', methods=['PUT', 'DELETE'])
def admin_client_detail(client_id: int):
    auth = require_auth(request)
    if not _require_admin(auth):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    with get_session() as db:
        client = db.query(Client).filter_by(id=client_id).first()
        if not client:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404
        if request.method == 'DELETE':
            db.delete(client)
            if client.user:
                db.delete(client.user)
            db.commit()
            return jsonify({'success': True}), 200
        data = request.get_json() or {}
        if 'permissions' in data:
            client.permissions = json.dumps(data.get('permissions', []))
        if 'devices' in data:
            client.devices.clear()
            for device_id in data.get('devices', []):
                device = db.query(Device).filter_by(device_id=device_id).first()
                if device:
                    client.devices.append(device)
        db.commit()
        return jsonify({'success': True}), 200



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Servidor BizonMDM")
    parser.add_argument('--init-db', action='store_true', help='Inicializar base de datos y salir')
    args = parser.parse_args()

    if args.init_db:
        init_db(drop=True)
        print('Base de datos inicializada')
    else:
        host = os.getenv('BIZON_HOST', '0.0.0.0')
        port = int(os.getenv('BIZON_PORT', '5000'))
        ssl_cert = os.getenv('SSL_CERT')
        ssl_key = os.getenv('SSL_KEY')
        ssl_context = (ssl_cert, ssl_key) if ssl_cert and ssl_key else None
        init_db()
        app.run(host=host, port=port, ssl_context=ssl_context)
