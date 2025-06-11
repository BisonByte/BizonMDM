# Manual completo del servidor de ejemplo

Este documento detalla el funcionamiento del servidor incluido en el directorio `Servidor/`. Se basa en Flask y sirve como backend de pruebas para la aplicación BizonMDM.

## 1. ¿Qué contiene el servidor?

En este directorio encontrarás principalmente dos archivos:

- `server.py`: implementa los distintos endpoints REST.
- `requirements.txt`: lista las dependencias necesarias (Flask, SQLAlchemy y qrcode).

## 2. Requisitos previos

- Python **3.8 o superior**.
- `pip` para instalar las dependencias.

## 3. Instalación paso a paso

1. (Opcional) crea un entorno virtual y actívalo:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## 4. Puesta en marcha del servidor

Ejecuta los siguientes comandos en esta carpeta:

```bash
python server.py --init-db      # solo la primera vez
python server.py
```

Esto inicializa la base de datos (archivo SQLite) la primera vez y luego levanta el servicio. Verás un mensaje como:

```
 * Running on http://0.0.0.0:5000/
```

Se pueden modificar la dirección y el puerto mediante las variables de entorno `BIZON_HOST` y `BIZON_PORT`. Si defines `BIZON_TOKEN`, todas las peticiones deberán incluir el encabezado `Authorization: Bearer <token>`.
La ruta del archivo de base de datos puede cambiarse con `BIZON_DB` (por defecto `bizon.db`).

## 5. Características y funcionamiento interno

- **Persistencia de datos**: se utiliza SQLite a través de SQLAlchemy. Las tablas (dispositivos, logs y comandos) están definidas en `models.py`. La función `init_db()` crea las tablas necesarias si no existen.
- **Seguridad opcional**: al definir `BIZON_TOKEN`, los endpoints exigen autenticación mediante el encabezado mencionado.
- **Endpoints principales**:
  - `/devices/register` para registrar un dispositivo (`POST`).
  - `/devices/status` para actualizar su estado (`POST`).
  - `/logs` para almacenar registros (`POST`).
  - `/commands` para guardar comandos pendientes (`POST`).
  - `/commands/<device_id>` para obtener y limpiar comandos (`GET`).
  - `/provisioning/qr/<device_id>` para generar el código QR de aprovisionamiento (`GET`).

## 6. Generación del código QR de aprovisionamiento

Puedes solicitar un código QR con:

```
http://<host>:<puerto>/provisioning/qr/<deviceId>
```

Ese QR debe escanearse desde el asistente de configuración de un dispositivo recién restaurado. Asegúrate de colocar `mdm.apk` en el directorio `downloads/` para que el sistema pueda descargarlo automáticamente.

## 7. Ejemplos de uso con `curl`

Registrar un dispositivo:

```bash
curl -X POST http://localhost:5000/devices/register \
  -H 'Content-Type: application/json' \
  -d '{"deviceId": "123", "model": "Pixel", "manufacturer": "Google", "osVersion": "13"}'
```

Actualizar su estado:

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

Todas las respuestas usan el siguiente formato JSON:

```json
{
  "success": true,
  "message": "..."
}
```

## 8. Uso junto a la aplicación

1. Inicia el servidor como se indicó anteriormente.
2. Compila e instala la aplicación Android en el dispositivo.
3. La app se comunicará periódicamente con el servidor para enviar su estado y recibir comandos.

## 9. Resumen de pasos

1. Clona este repositorio y entra en `Servidor/`.
2. (Opcional) crea un entorno virtual.
3. Instala las dependencias con `pip install -r requirements.txt`.
4. Inicializa la base de datos: `python server.py --init-db`.
5. Ejecuta `python server.py` para levantar el servicio.
6. (Opcional) genera un QR para aprovisionar dispositivos y coloca `mdm.apk` en `downloads/`.
7. Interactúa con los endpoints para registrar dispositivos, enviar logs y gestionar comandos.

Este servidor está pensado para desarrollo y pruebas; si se desea usar en producción conviene reforzarlo y ajustarlo a las necesidades específicas.
