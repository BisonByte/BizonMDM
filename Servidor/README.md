# Servidor de ejemplo para BizonMDM

Este directorio contiene un ejemplo sencillo de servidor REST que expone los endpoints que la aplicación BizonMDM utiliza para registrar dispositivos y actualizar su estado.

## Requisitos

- Python 3.8 o superior
- pip para instalar dependencias

## Instalación

1. Opcional: crea un entorno virtual de Python.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instala las dependencias indicadas en `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

## Uso

Ejecuta el servidor con:

```bash
python server.py
```

Por defecto escucha en `http://0.0.0.0:5000/`.

## Endpoints

- `POST /devices/register`: registra un dispositivo. Debe enviarse un JSON con los campos:
  - `deviceId`
  - `model`
  - `manufacturer`
  - `osVersion`

- `POST /devices/status`: actualiza el estado del dispositivo. JSON esperado:
  - `deviceId`
  - `status`
  - `lastUpdate`

Ambos endpoints responden un JSON de la forma:

```json
{
  "success": true,
  "message": "..."
}
```

Este servidor es solo un ejemplo para propósitos de desarrollo y pruebas.
