# Servidor de ejemplo para BizonMDM

Este directorio contiene un servidor REST muy sencillo que expone los endpoints que la aplicación BizonMDM utiliza para registrar dispositivos y actualizar su estado. Se ha pensado como referencia para pruebas locales y no debe usarse en producción.

## Requisitos

- Python 3.8 o superior (comprueba la versión con `python --version`)
- pip para instalar dependencias

## Instalación paso a paso

1. **Opcional:** crea un entorno virtual para aislar las dependencias.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Actualiza `pip` e instala los paquetes requeridos.

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Uso

Asegúrate de estar situado dentro de esta carpeta y ejecuta:

```bash
python server.py
```

Al iniciarse verás un mensaje similar a:

```
 * Running on http://0.0.0.0:5000/
```

Para detener el servidor utiliza `Ctrl+C` en la misma consola.

Por defecto escucha en `http://0.0.0.0:5000/`. Puedes cambiar el host o el puerto mediante las variables de entorno `BIZON_HOST` y `BIZON_PORT`:

```bash
BIZON_HOST=127.0.0.1 BIZON_PORT=8000 python server.py
```

## Pruebas rápidas

Puedes probar los endpoints con `curl` u otra herramienta como Postman.

Registrar un dispositivo:

```bash
curl -X POST http://localhost:5000/devices/register \
  -H 'Content-Type: application/json' \
  -d '{"deviceId": "123", "model": "Pixel", "manufacturer": "Google", "osVersion": "13"}'
```

Actualizar el estado de un dispositivo:

```bash
curl -X POST http://localhost:5000/devices/status \
  -H 'Content-Type: application/json' \
  -d '{"deviceId": "123", "status": "OK", "lastUpdate": "2023-01-01T00:00:00"}'
```

Ambos devolverán un JSON de la forma:

```json
{
  "success": true,
  "message": "..."
}
```

## Endpoints disponibles

- `POST /devices/register` – registra un dispositivo; requiere los campos `deviceId`, `model`, `manufacturer` y `osVersion`.
- `POST /devices/status` – actualiza el estado del dispositivo; requiere `deviceId`, `status` y `lastUpdate`.

Este servidor es solo un ejemplo para propósitos de desarrollo y pruebas.
