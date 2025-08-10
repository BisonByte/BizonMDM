# BizonMDM

BizonMDM es una plataforma de Mobile Device Management (MDM) de código abierto. Permite registrar dispositivos Android, enviar acciones remotas y administrar la comunicación mediante un panel web.

## Tecnologías

- **Aplicación móvil:** Android escrita en Kotlin y construida con Gradle.
- **Backend:** Python 3 con Flask, SQLAlchemy y Alembic para las migraciones.
- **Panel de administración:** aplicación React servida por el backend.
- **Mensajería:** Firebase Cloud Messaging (FCM) para notificaciones push.

## Estructura del repositorio

- `mobile/`: aplicación móvil Android.
  - El servicio MDM se ejecuta como foreground y muestra una notificación persistente.
  - La URL del servidor se obtiene de `BuildConfig.BASE_URL`, definida a través de `gradle.properties`, variables de entorno o las `productFlavors` `dev` y `prod` en `mobile/app/build.gradle.kts`.
- `server/`: componentes del servidor y del panel web.
  - `Servidor/`: API en Flask, modelos de base de datos y scripts de instalación.
  - `admin/`, `alerts/`, `client/`, `device/`, `documents/`, `financing/`, `tasks/`: módulos Python que implementan la lógica del backend.
  - `admin-frontend/` y `client-frontend/`: interfaces web construidas en React.
  - `docker-compose.yml`: ejemplo de despliegue con contenedores.
  - `install.py` e `instalacion_bizonmdm.html`: utilidades para la instalación.
  - `SUBDOMAIN_SETUP.md`: ejemplo de configuración de NGINX/Apache para servir varios subdominios.
- `docs/`: documentación adicional incluyendo `documentation.html`.

### Configurar la URL del servidor en la app móvil

La aplicación obtiene la dirección del backend desde `BuildConfig.BASE_URL`. El valor puede definirse de las siguientes maneras:

- **`gradle.properties`** (`mobile/gradle.properties`):

  ```
  DEV_BASE_URL=https://dev.tuservidor.com/
  PROD_BASE_URL=https://tuservidor.com/
  ```

- **Variables de entorno**:

  ```
  export DEV_BASE_URL=https://dev.tuservidor.com/
  export PROD_BASE_URL=https://tuservidor.com/
  ```

Compila usando el flavor deseado:

```
./gradlew assembleDevDebug    # usa DEV_BASE_URL
./gradlew assembleProdRelease # usa PROD_BASE_URL
```

## Instalación rápida

```bash
cd server
docker-compose up -d
```

Accede al panel en `http://localhost:5000`.

### Variables de entorno opcionales

Puedes definir variables antes de levantar los contenedores:

- `DATABASE_URL`: cadena de conexión a la base de datos (por defecto `postgresql+psycopg2://postgres:postgres@db:5432/bizon`).
- `BIZON_HOST`: dirección en la que el servidor escucha (por defecto `0.0.0.0`).
- `BIZON_PORT`: puerto interno del servidor (por defecto `5000`).
- `JWT_SECRET`: clave para firmar tokens JWT.
- `FCM_SERVER_KEY`: clave de Firebase Cloud Messaging para notificaciones.

### Detener o eliminar contenedores

Detén los servicios con:

```bash
docker-compose down
```

Para eliminar también volúmenes y datos:

```bash
docker-compose down -v
```

## Instalación del servidor

### Requisitos previos

- Python 3.10+ y `pip`.
- Node.js 18+ si deseas recompilar el panel React.
- Una base de datos SQL (PostgreSQL, MySQL/MariaDB o SQLite para pruebas).
- Clave de servidor de Firebase Cloud Messaging.

### Pasos

1. Clona este repositorio.
2. Instala las dependencias y ejecuta el script de instalación:

```bash
pip install -r server/Servidor/requirements.txt
python server/install.py
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
6. (Opcional) Compila la interfaz web si realizaste cambios en `server/admin-frontend/`:

```bash
cd server/admin-frontend
npm install
npm run build
```

7. Inicia el servidor y comprueba el estado:

```bash
python server/Servidor/server.py &
curl http://localhost:5000/api/status
```

## Panel de administración

La interfaz web ubicada en `server/admin-frontend/` obtiene la lista de dispositivos desde la API del servidor y permite enviar acciones como "Borrar datos" o "Bloquear dispositivo". También muestra un indicador de estado que comprueba la conexión con la base de datos y la validez de la clave de Firebase mediante el endpoint `/api/status`.

## Gestión de usuarios y autenticación

BizonMDM permite registrar usuarios que acceden al panel cliente.

### Creación de usuarios

```bash
curl -X POST https://mi-servidor/api/users \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{"username":"jane","password":"secreta","role":"cliente"}'
```

### Inicio de sesión

```bash
curl -X POST https://mi-servidor/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"jane","password":"secreta"}'
```

La respuesta incluye un token JWT usado para llamadas posteriores.

### Permisos y roles

Los roles disponibles son `admin`, `operador` y `cliente`. Cada uno limita el acceso a los endpoints y al panel según sus privilegios.

### Uso del panel cliente

Los usuarios autenticados pueden acceder a `https://mi-servidor/cliente` para gestionar sus propios dispositivos, revisar el estado y ejecutar acciones permitidas.

#### Ejemplo: listar dispositivos

```bash
curl -H "Authorization: Bearer <token_cliente>" https://mi-servidor/api/devices
```

Con el identificador de un dispositivo también es posible enviar acciones:

```bash
curl -X POST https://mi-servidor/api/devices/42/lock \
  -H "Authorization: Bearer <token_cliente>"
```

### Consideraciones de seguridad

- Obliga HTTPS para todas las peticiones.
- Almacena las contraseñas con algoritmos de hash seguros (p. ej., bcrypt).
- Define tiempos de expiración cortos para los tokens JWT y rotación mediante refresh.
- Deshabilita o protege el endpoint `/install` una vez finalizada la configuración.
- Limita los intentos de inicio de sesión para mitigar fuerza bruta.

## Licencia

Este proyecto se distribuye bajo los términos de la licencia MIT. Consulta el archivo `LICENSE` para más información.
