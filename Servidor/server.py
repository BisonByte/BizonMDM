"""Servidor REST de ejemplo utilizado por la aplicación BizonMDM.

Este script define dos endpoints muy sencillos que permiten registrar un
dispositivo y actualizar su estado. Todos los datos se almacenan en
memoria, por lo que el servidor está pensado exclusivamente para pruebas
locales.
"""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Diccionario en memoria para almacenar la información de los dispositivos
registered_devices: dict[str, dict] = {}

@app.route('/devices/register', methods=['POST'])
def register_device():
    """Registra un dispositivo a partir de un JSON enviado por la app."""
    data = request.get_json() or {}
    device_id = data.get('deviceId')
    if not device_id:
        return jsonify({'success': False, 'message': 'deviceId requerido'}), 400
    registered_devices[device_id] = {
        'info': data,
        'status': None
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

if __name__ == '__main__':
    host = os.getenv('BIZON_HOST', '0.0.0.0')
    port = int(os.getenv('BIZON_PORT', '5000'))
    app.run(host=host, port=port)
