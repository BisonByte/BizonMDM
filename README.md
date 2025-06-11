# BizonMDM

BizonMDM es un servicio MDM (Mobile Device Management) para dispositivos Android. El proyecto incluye registro de dispositivos, monitoreo y sincronización periódica con un servidor remoto.

## Características principales

- **Registro y actualización de estado** del dispositivo mediante Retrofit.
- **Almacenamiento local** con Room para conservar información y logs.
- **Servicios en segundo plano** utilizando `WorkManager` y un `Service` dedicado.
- **Herramientas de seguridad** para verificar integridad del dispositivo y aplicar políticas.
- **Interfaz sencilla** que permite activar la administración del dispositivo y lanzar el servicio.
- **Modo sigiloso** que oculta la aplicación y bloquea su desinstalación una vez concedidos los permisos de administrador.
- **Restricciones de dispositivo** que impiden el formateo, fijan el brillo al 100%, mantienen el GPS activo y evitan cambios manuales de fecha y hora.

## Estructura del proyecto

- `app/src/main/java/com/example/mdmjive` – Código fuente principal.
- `network` – Comunicación con el servidor.
- `database` – Entidades y DAOs de Room.
- `services` y `workers` – Componentes que se ejecutan en segundo plano.

## Compilación

1. Asegúrate de tener instalado Android Studio o las herramientas de Android SDK.
2. Ejecuta `./gradlew assembleDebug` para generar el APK de desarrollo.

El proyecto requiere un mínimo de **Android 7.0 (API 24)**.

## Uso básico

1. Instala la aplicación en el dispositivo.
2. Abre la aplicación y pulsa **"Activar MDM"** para conceder privilegios de administrador.
3. Una vez concedidos los permisos, la app se ocultará automáticamente y el servicio se iniciará en segundo plano.

## Servidor de ejemplo

En la carpeta `Servidor` se incluye un pequeño servidor REST escrito en
Python para propósitos de prueba. Consulta su [README](Servidor/README.md)
para instrucciones de instalación y ejecución.

## Configuración del servidor

Para que la aplicación se comunique con tu servidor debes modificar la URL
base que utiliza el cliente HTTP. Edita las siguientes clases y reemplaza
`https://example.com/` por la dirección donde ejecutes el servidor:

- `app/src/main/java/com/example/mdmjive/services/MDMService.kt`
- `app/src/main/java/com/example/mdmjive/workers/SyncWorker.kt`

Una vez actualizadas las rutas, compila e instala la aplicación.

## Puesta en marcha

1. Inicia el servidor como se indica en la carpeta `Servidor`.
2. Instala el APK generado en tu dispositivo Android.
3. Abre la app y pulsa **"Activar MDM"** para conceder privilegios.
4. Tras la activación, la app se ocultará y comenzará a sincronizarse con el
   servidor cada 15 minutos.


