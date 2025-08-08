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

from models import Device, LogEntry, Command, SessionLocal, init_db
from sqlalchemy import text
from install_script import install_application

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


def encode_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt(token: str, secret: str) -> dict:
    header_b64, payload_b64, signature_b64 = token.split(".")
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = _b64url_decode(signature_b64)
    expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid signature")
    payload = json.loads(_b64url_decode(payload_b64))
    return payload


def require_auth(request) -> bool:
    """Valida el encabezado Authorization mediante JWT si está configurado."""
    if not JWT_SECRET:
        return True
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1]
    try:
        decode_jwt(token, JWT_SECRET)
        return True
    except Exception:
        return False


def get_session():
    """Obtiene una nueva sesión de base de datos."""
    return SessionLocal()


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

@app.route('/devices/register', methods=['POST'])
def register_device():
    """Registra un dispositivo a partir de un JSON enviado por la app."""
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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

@app.route('/devices/status', methods=['POST'])
def update_status():
    """Actualiza el estado del dispositivo previamente registrado."""
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        device.status = json.dumps(data)
        if data.get('fcmToken'):
            device.fcm_token = data.get('fcmToken')
        db.commit()
    return jsonify({'success': True, 'message': 'Estado actualizado'}), 200


@app.route('/devices', methods=['GET'])
def list_devices():
    """Devuelve la lista de dispositivos registrados."""
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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

@app.route('/devices/<device_id>', methods=['GET'])
def get_device_info(device_id: str):
    """Devuelve la información completa almacenada de un dispositivo."""
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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

# --- Endpoints para manejo de logs ---

@app.route('/logs', methods=['POST'])
def upload_logs():
    """Recibe una lista de logs enviados por un dispositivo."""
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    logs = data.get('logs', [])
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400

    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        if isinstance(logs, list):
            for entry in logs:
                db.add(LogEntry(device_id=device.id, log=json.dumps(entry)))
            db.commit()
    return jsonify({'success': True, 'message': 'Logs recibidos', 'count': len(logs)}), 200


@app.route('/logs/<device_id>', methods=['GET'])
def get_logs(device_id: str):
    """Devuelve los logs almacenados de un dispositivo."""
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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
    _send_fcm_message(token, payload)
    return True


def _send_fcm_message(token: str | None, payload: dict) -> None:
    if not token or not FCM_SERVER_KEY:
        return
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    body = {"to": token, "data": payload}
    try:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(FCM_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception as exc:
        logging.warning("Error enviando FCM: %s", exc)


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


@app.route('/api/config/fcm', methods=['GET', 'POST'])
def api_config_fcm():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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


@app.route('/api/test-fcm', methods=['POST'])
def api_test_fcm():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    with get_session() as db:
        devices = db.query(Device).all()
    for d in devices:
        _send_fcm_message(d.fcm_token, {'action': 'test_message'})
    return jsonify({'success': True, 'sent': len(devices)}), 200


@app.route('/api/device/wipe', methods=['POST'])
def api_device_wipe():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_wipe'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/api/device/reboot', methods=['POST'])
def api_device_reboot():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_reboot'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/api/device/lock', methods=['POST'])
def api_device_lock():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_lock'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/api/device/screenshot', methods=['POST'])
def api_device_screenshot():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    if not _queue_command(device_id, 'device_screenshot'):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/api/app/install', methods=['POST'])
def api_app_install():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    url = data.get('url')
    if not device_id or not url:
        return jsonify({'success': False, 'message': 'deviceId y url requeridos'}), 400
    if not _queue_command(device_id, 'app_install', {'url': url}):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200


@app.route('/api/app/uninstall', methods=['POST'])
def api_app_uninstall():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    package = data.get('package')
    if not device_id or not package:
        return jsonify({'success': False, 'message': 'deviceId y package requeridos'}), 400
    if not _queue_command(device_id, 'app_uninstall', {'package': package}):
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    return jsonify({'success': True, 'message': 'Comando enviado'}), 200

@app.route('/commands', methods=['POST'])
def add_command():
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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


@app.route('/commands/<device_id>', methods=['GET'])
def get_commands(device_id: str):
    if not require_auth(request):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    with get_session() as db:
        device = db.query(Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
        cmds = [json.loads(c.command) for c in device.commands]
        for c in device.commands:
            db.delete(c)
        db.commit()
    return jsonify(cmds), 200


@app.route('/api/install', methods=['POST'])
def install():
    data = request.json
    db_host = data.get('db_host')
    db_name = data.get('db_name')
    db_user = data.get('db_user')
    db_pass = data.get('db_pass')
    jwt_secret = data.get('jwt_secret')

    try:
        install_application(db_host, db_name, db_user, db_pass, jwt_secret)
        return jsonify({"success": True, "message": "Instalación completada."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Servidor BizonMDM")
    parser.add_argument('--init-db', action='store_true', help='Inicializar base de datos y salir')
    args = parser.parse_args()

    if args.init_db:
        init_db()
        print('Base de datos inicializada')
    else:
        host = os.getenv('BIZON_HOST', '0.0.0.0')
        port = int(os.getenv('BIZON_PORT', '5000'))
        ssl_cert = os.getenv('SSL_CERT')
        ssl_key = os.getenv('SSL_KEY')
        ssl_context = (ssl_cert, ssl_key) if ssl_cert and ssl_key else None
        init_db()
        app.run(host=host, port=port, ssl_context=ssl_context)
