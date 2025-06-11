from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Almacenamiento en memoria de dispositivos y estados
registered_devices = {}

@app.route('/devices/register', methods=['POST'])
def register_device():
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
