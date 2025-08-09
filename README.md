# BizonMDM

Esta versión incluye un proceso de instalación simplificado para el servidor de ejemplo y el panel de administración.

## Estructura del repositorio

- `mobile/`: aplicación móvil Android.
- `server/`: servidor en Flask y panel de administración web.

## Instalación del servidor

1. Clona este repositorio.
2. Instala las dependencias y ejecuta el script de instalación:
   ```bash
   pip install -r server/Servidor/requirements.txt
   python server/install_script.py
   ```
3. Abre `http://localhost:5000/install` en tu navegador y completa el formulario con:
   - Cadena de conexión de la base de datos.
   - Clave secreta JWT.
   - Clave de Firebase Cloud Messaging.
   - Usuario y contraseña del administrador inicial.
4. Al enviar el formulario se realizará automáticamente:
   - La creación del archivo `.env` con la configuración proporcionada.
   - El guardado de la clave de Firebase en `fcm_key.txt`.
   - La ejecución de las migraciones de Alembic para preparar la base de datos.
   - La creación del usuario administrador.
5. Tras una instalación exitosa serás redirigido al panel de administración.

Para iniciar el servidor después de la instalación:

```bash
python server/Servidor/server.py
```

## Panel de administración

La interfaz web ubicada en `server/admin-frontend/` obtiene la lista de dispositivos desde la API del servidor y permite enviar acciones como "Borrar datos" o "Bloquear dispositivo". También muestra un indicador de estado que comprueba la conexión con la base de datos y la validez de la clave de Firebase mediante el endpoint `/api/status`.
