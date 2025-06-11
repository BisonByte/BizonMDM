# Servidor de ejemplo para BizonMDM

Este directorio contiene un peque\u00f1o servidor REST implementado con Flask. Se utiliza para registrar dispositivos, recibir su estado y almacenar logs enviados por la aplicaci\u00f3n BizonMDM. Toda la informaci\u00f3n se guarda en memoria, por lo que solo est\u00e1 pensado para pruebas locales.

## Contenido

- `server.py` - implementaci\u00f3n de los endpoints REST.
- `requirements.txt` - dependencias de Python (actualmente solo Flask).

## Requisitos

- Python 3.8 o superior
- `pip` para instalar dependencias

## Instalaci\u00f3n paso a paso

1. **Opcional**: crea un entorno virtual para aislar las dependencias.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instala los paquetes requeridos.

   ```bash
   pip install -r requirements.txt
   ```

## Uso

Desde esta carpeta ejecuta:

```bash
python server.py
```

Ver\u00e1s un mensaje como:

```
 * Running on http://0.0.0.0:5000/
```

Puedes detenerlo con `Ctrl+C`. El host y el puerto pueden cambiarse con las variables `BIZON_HOST` y `BIZON_PORT`:

```bash
BIZON_HOST=127.0.0.1 BIZON_PORT=8000 python server.py
```

## Pruebas r\u00e1pidas

Ejemplos de peticiones con `curl`:

Registrar un dispositivo:

```bash
curl -X POST http://localhost:5000/devices/register \
  -H 'Content-Type: application/json' \
  -d '{"deviceId": "123", "model": "Pixel", "manufacturer": "Google", "osVersion": "13", "email": "demo@example.com", "phone": "+123456789", "code": "PX-001", "serial": "ABC123", "activationLocation": "MX"}'
```

Actualizar el estado de un dispositivo:

```bash
curl -X POST http://localhost:5000/devices/status \
  -H 'Content-Type: application/json' \
  -d '{"deviceId": "123", "status": "OK", "lastUpdate": "2023-01-01T00:00:00"}'
```

Enviar logs:

```bash
curl -X POST http://localhost:5000/logs \
  -H 'Content-Type: application/json' \
  -d '{"deviceId": "123", "logs": [{"timestamp": 1700000000, "type": "INFO", "message": "Inicio", "severity": "LOW"}]}'
```

Todos los endpoints responden con un JSON similar a:

```json
{
  "success": true,
  "message": "..."
}
```

## Endpoints disponibles

- `POST /devices/register` – registra un dispositivo.
- `POST /devices/status` – actualiza su estado.
- `GET /devices/<deviceId>` – muestra la informaci\u00f3n almacenada.
- `POST /logs` – almacena logs de un dispositivo.
- `GET /logs/<deviceId>` – devuelve los logs registrados.
- `POST /commands` – guarda un comando pendiente.
- `GET /commands/<deviceId>` – obtiene y limpia los comandos para el dispositivo.

Este servidor es un ejemplo para desarrollo y pruebas.
