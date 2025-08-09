# BizonMDM

BizonMDM es una plataforma de Mobile Device Management (MDM) de código abierto. Permite registrar dispositivos Android, enviar acciones remotas y administrar la comunicación mediante un panel web.

## Tecnologías

- **Aplicación móvil:** Android escrita en Kotlin y construida con Gradle.
- **Backend:** Python 3 con Flask, SQLAlchemy y Alembic para las migraciones.
- **Panel de administración:** aplicación React servida por el backend.
- **Mensajería:** Firebase Cloud Messaging (FCM) para notificaciones push.

## Estructura del repositorio

- `mobile/`: aplicación móvil Android.
- `server/`: archivos relacionados con el servidor y el panel de administración.
  - `Servidor/`: API en Flask, modelos de base de datos y scripts de instalación.
  - `admin-frontend/`: interfaz web de administración construida en React.
  - `docker-compose.yml`: ejemplo de despliegue con contenedores.
  - `install_script.py` e `instalacion_bizonmdm.html`: utilidades para la instalación.

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

## Licencia

Este proyecto se distribuye bajo los términos de la licencia MIT. Consulta el archivo `LICENSE` para más información.
