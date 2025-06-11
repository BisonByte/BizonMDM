"""Servidor REST de ejemplo utilizado por la aplicación BizonMDM.

Este script define varios endpoints muy sencillos para registrar un dispositivo,
actualizar su estado y almacenar logs enviados por la aplicación. Todos los
datos se guardan en memoria, por lo que el servidor está pensado
exclusivamente para pruebas locales.
"""

from flask import Flask, request, jsonify, send_file
import os
import datetime
import json
import base64
import io
import qrcode

app = Flask(__name__)

# Diccionario en memoria para almacenar la información de los dispositivos
registered_devices: dict[str, dict] = {}
# Diccionario en memoria para almacenar los logs enviados por cada dispositivo
device_logs: dict[str, list] = {}
# Cola en memoria de comandos pendientes por dispositivo
pending_commands: dict[str, list] = {}


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
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    registered_devices[device_id] = {
        'info': data,
        'status': None,
        'added': datetime.datetime.utcnow().isoformat()
    }
    return jsonify({'success': True, 'message': 'Dispositivo registrado'}), 200

@app.route('/devices/status', methods=['POST'])
def update_status():
    """Actualiza el estado del dispositivo previamente registrado."""
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id or device_id not in registered_devices:
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    registered_devices[device_id]['status'] = data
    return jsonify({'success': True, 'message': 'Estado actualizado'}), 200

@app.route('/devices/<device_id>', methods=['GET'])
def get_device_info(device_id: str):
    """Devuelve la información completa almacenada de un dispositivo."""
    device = registered_devices.get(device_id)
    if not device:
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404

    info = device['info']
    result = {
        'model': info.get('model'),
        'code': info.get('code'),
        'serial': info.get('serial'),
        'activationLocation': info.get('activationLocation'),
        'addedDate': device.get('added'),
        'email': info.get('email'),
        'phone': info.get('phone')
    }
    return jsonify(result), 200

# --- Endpoints para manejo de logs ---

@app.route('/logs', methods=['POST'])
def upload_logs():
    """Recibe una lista de logs enviados por un dispositivo."""
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    logs = data.get('logs', [])
    if not device_id or device_id not in registered_devices:
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404

    stored = device_logs.setdefault(device_id, [])
    if isinstance(logs, list):
        stored.extend(logs)
    return jsonify({'success': True, 'message': 'Logs recibidos', 'count': len(logs)}), 200


@app.route('/logs/<device_id>', methods=['GET'])
def get_logs(device_id: str):
    """Devuelve los logs almacenados de un dispositivo."""
    if device_id not in registered_devices:
        return jsonify({'success': False, 'message': 'Dispositivo no encontrado'}), 404
    logs = device_logs.get(device_id, [])
    return jsonify({'logs': logs}), 200

# --- Endpoints de control de dispositivos ---

@app.route('/commands', methods=['POST'])
def add_command():
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    action = data.get('action')
    if not device_id or not action:
        return jsonify({'success': False, 'message': 'deviceId y action requeridos'}), 400
    pending_commands.setdefault(device_id, []).append(data)
    return jsonify({'success': True, 'message': 'Comando almacenado'}), 200


@app.route('/commands/<device_id>', methods=['GET'])
def get_commands(device_id: str):
    cmds = pending_commands.get(device_id, [])
    pending_commands[device_id] = []
    return jsonify(cmds), 200

if __name__ == '__main__':
    host = os.getenv('BIZON_HOST', '0.0.0.0')
    port = int(os.getenv('BIZON_PORT', '5000'))
    app.run(host=host, port=port)
