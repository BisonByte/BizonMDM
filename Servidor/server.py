"""Servidor REST utilizado por la aplicación BizonMDM.

Ahora almacena la información en una base de datos SQLite en lugar de
mantener todo en memoria. Permite opcionalmente proteger los endpoints
mediante un token especificado en ``BIZON_TOKEN``.
"""

from flask import Flask, request, jsonify, send_file
import os
import json
import base64
import io
import qrcode
import logging

from models import Device, LogEntry, Command, SessionLocal, init_db

app = Flask(__name__)


# Configuración ---------------------------------------------------------------
BIZON_TOKEN = os.getenv("BIZON_TOKEN")
logging.basicConfig(filename="server.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def require_auth(request) -> bool:
    """Valida el encabezado Authorization si BIZON_TOKEN está definido."""
    if not BIZON_TOKEN:
        return True
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and auth.split(" ", 1)[1] == BIZON_TOKEN:
        return True
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
            device = Device(device_id=device_id, info=json.dumps(data))
            db.add(device)
        else:
            device.info = json.dumps(data)
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
        db.commit()
    return jsonify({'success': True, 'message': 'Estado actualizado'}), 200

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
        result = {
            'model': info.get('model'),
            'code': info.get('code'),
            'serial': info.get('serial'),
            'activationLocation': info.get('activationLocation'),
            'addedDate': device.added.isoformat() if device.added else None,
            'email': info.get('email'),
            'phone': info.get('phone')
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
        init_db()
        app.run(host=host, port=port)
