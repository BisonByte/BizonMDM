# Manual técnico de BizonMDM

## Visión general de la plataforma

BizonMDM es un sistema de gestión de dispositivos móviles compuesto por un
backend en **Flask**, dos interfaces web escritas en **React** y una
aplicación **Android** desarrollada en **Kotlin**. A continuación se
describe de forma detallada la arquitectura de cada componente.

## Backend Flask (`server/Servidor`)

### Organización de archivos

El directorio `server/Servidor` contiene la API REST principal:

- `server.py` inicializa la aplicación Flask, registra rutas y puede
  ejecutarse con los parámetros `BIZON_HOST`, `BIZON_PORT` y `JWT_SECRET`.
- `models.py` define los modelos de base de datos con SQLAlchemy.
- `configs/` almacena plantillas de configuración y la plantilla del
  archivo `.env` generado durante la instalación.
- `alembic/` y `alembic.ini` gestionan las migraciones de esquema mediante
  Alembic.

Además del módulo `Servidor`, la carpeta `server/` incluye paquetes
especializados (`admin`, `alerts`, `client`, `device`, `documents`,
`financing`, `tasks`) que encapsulan la lógica del dominio y exponen
blueprints de Flask para ampliar la API.

### Flujo de peticiones y seguridad

El servicio expone endpoints para registrar dispositivos, consultar su
estado, enviar comandos y recuperar logs. La autenticación se realiza con
**JSON Web Tokens (JWT)** firmados con la variable de entorno
`JWT_SECRET`. Los endpoints administrativos verifican el rol del usuario
antes de ejecutar cualquier acción.

Las peticiones se persisten en una base de datos SQL mediante
**SQLAlchemy**. Las migraciones se controlan con **Alembic**, permitiendo
actualizar el esquema sin perder datos.

### Integraciones externas

- **Firebase Cloud Messaging (FCM):** si se define `FCM_SERVER_KEY` el
  servidor envía notificaciones push cuando se encola un comando.
- **Provisión mediante QR:** el endpoint `/provisioning/qr/<deviceId>`
  genera códigos QR para aprovisionamiento sin intervención manual.

## Módulos React (`admin-frontend` y `client-frontend`)

Las interfaces web viven en `server/admin-frontend` y
`server/client-frontend` respectivamente. Cada módulo contiene:

- `index.html` que carga React desde CDN y monta la aplicación.
- `app.jsx` con los componentes principales escritos con la API de
  funciones (`useState`, `useEffect`).
- `package.json` con dependencias ligeras como `recharts` para gráficas y
  `framer-motion` para animaciones. No se requiere un bundler complejo;
  los archivos JSX se transpilan de forma sencilla para producción.

### Panel de administración

`admin-frontend/app.jsx` utiliza un helper `apiFetch` que añade el token
JWT almacenado en `localStorage` y consume endpoints como `/devices` o
`/api/status`. Presenta un tablero con el listado de dispositivos y un
indicador de salud del servidor.

### Panel de cliente

`client-frontend/app.jsx` ofrece una interfaz simplificada para que los
usuarios finales consulten el estado de sus propios dispositivos y
reciban notificaciones visuales de los comandos enviados.

Ambos módulos se sirven como archivos estáticos desde Flask y pueden
recompilarse con `npm install` seguido de `npm run build` en sus
respectivos directorios.

## Aplicación Android en Kotlin (`mobile/app`)

### Estructura general

El proyecto Android utiliza Gradle con flavors `dev` y `prod` que definen
la URL del backend mediante `BuildConfig.BASE_URL`. Dentro de
`mobile/app/src/main/java/com/example/mdmjive/` se encuentran los módulos
principales:

- **Servicios:** `MDMService` mantiene un servicio en primer plano con una
  notificación persistente y programa tareas periódicas con `WorkManager`.
  `FCMService` maneja los mensajes push de Firebase.
- **Receivers:** `MDMDeviceAdminReceiver` y `SecurityEventReceiver`
  administran eventos del `DevicePolicyManager` y del sistema.
- **Núcleo y utilidades:** `MDMCore` centraliza la lógica de negocio,
  mientras que `TokenManager`, `SecurityUtils` y `QRConfig` proveen
  funcionalidades de soporte.
- **Persistencia:** `LogDatabase` implementa una base de datos local con
  **Room** para almacenar eventos, políticas y auditorías.
- **Comunicación remota:** `ApiService` usa **Retrofit** para interactuar
  con la API del servidor (`devices/register`, `client/logs`,
  `client/commands`, etc.).
- **Seguridad:** `SecurityChecker`, `DeviceCertificationManager` y
  `PolicyManager` verifican el estado del dispositivo, aplican políticas y
  cifran información sensible mediante `EncryptionManager`.
- **Tareas en segundo plano:** `SyncWorker` sincroniza periódicamente el
  estado y los logs con el backend.

### Flujo de operación

Al iniciar el dispositivo se levanta `MDMService`, que a su vez programa
`SyncWorker` y monitoriza el `DevicePolicyManager`. Los eventos de
seguridad se registran en `LogDatabase` y pueden enviarse al servidor
cuando haya conectividad. Los comandos recibidos vía FCM se delegan a
`CommandExecutor`, que aplica acciones como bloqueo o borrado remoto.

## Despliegue y consideraciones finales

- **Servidor:** puede ejecutarse directamente con `python
  server/Servidor/server.py` o mediante `docker-compose` para incluir la
  base de datos y el panel web.
- **Frontends:** tras cualquier modificación en los archivos JSX, ejecutar
  `npm install` y `npm run build` dentro de cada módulo para generar la
  versión optimizada.
- **Aplicación móvil:** compilar con `./gradlew assembleDevDebug` o
  `./gradlew assembleProdRelease` según el entorno deseado.

Este manual proporciona una visión técnica integral para desarrolladores
y administradores que necesiten comprender o extender BizonMDM.
