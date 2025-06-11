# BizonMDM

BizonMDM es una solución sencilla de *Mobile Device Management* para Android. En este repositorio encontrarás la aplicación Android escrita en Kotlin junto con un pequeño servidor REST desarrollado en Python para propósitos de prueba.

La app permite registrar un dispositivo, sincronizar periódicamente su información y recibir comandos desde el servidor.

## Características de la aplicación

- **Registro y actualización de estado** del dispositivo mediante Retrofit.
- **Almacenamiento local** con Room para conservar datos y logs.
- **Servicios en segundo plano** con `WorkManager` y un `Service` dedicado.
- **Controles de seguridad** que aplican políticas sobre el dispositivo.
- **Modo sigiloso** que oculta la app y evita su desinstalación tras conceder privilegios de administrador.
- **Restricciones** que deshabilitan el formateo, fijan el brillo al 100 %, fuerzan el GPS activo y evitan cambios de fecha u hora.

## Estructura del repositorio

- `app/` – código de la aplicación Android.
- `Servidor/` – servidor REST de ejemplo para pruebas.
- Archivos Gradle en la raíz para compilar la app.

## Requisitos previos

- JDK 11 y Android Studio (o herramientas de Android SDK).
- Un dispositivo con **Android 7.0 (API 24)** o superior.
- Python 3.8+ si vas a utilizar el servidor incluido.

## Instalación de la aplicación

1. Clona este repositorio.
2. (Opcional) ajusta la URL del servidor en las clases:
   - `app/src/main/java/com/example/mdmjive/services/MDMService.kt`
   - `app/src/main/java/com/example/mdmjive/workers/SyncWorker.kt`
3. Ejecuta `./gradlew assembleDebug` para generar `app-debug.apk`.
4. Instala el APK en tu dispositivo, por ejemplo con `adb install app/build/outputs/apk/debug/app-debug.apk`.

### Aprovisionamiento mediante código QR

Si deseas automatizar la instalación sin intervención manual, el servidor puede
generar un código QR único para cada dispositivo. Al escanearlo desde el
asistente de configuración de Android, el sistema descargará el APK, lo
instalará de forma silenciosa y activará el modo MDM con la aplicación oculta.

1. Inicia el servidor y accede a `http://<host>:<puerto>/provisioning/qr/<id>`
   sustituyendo `<id>` por el identificador de tu dispositivo. Se mostrará una
   imagen con el QR.
2. En un teléfono recién restablecido elige la opción para escanear un código
   QR durante la configuración inicial y apunta al código generado.
3. Una vez completado el proceso el dispositivo quedará registrado con todos
   los permisos necesarios y la app funcionará en modo sigiloso.
4. Asegúrate de que el APK `mdm.apk` esté disponible en el servidor bajo
   `downloads/mdm.apk` para que el sistema pueda descargarlo.

## Uso de la aplicación

1. Abre la app y pulsa **"Activar MDM"** para conceder privilegios de administrador.
2. Después de la activación la app se oculta y el servicio queda corriendo en segundo plano.
3. El dispositivo se sincronizará con el servidor cada 15 minutos.

## Servidor de ejemplo

Dentro de `Servidor/` se incluye un backend minimalista basado en Flask. Para instalarlo y ponerlo en marcha:

```bash
cd Servidor
python3 -m venv venv       # opcional
source venv/bin/activate   # opcional
pip install -r requirements.txt
python server.py
```

Por defecto escuchará en `http://0.0.0.0:5000/`. Se pueden cambiar el host o el puerto mediante las variables `BIZON_HOST` y `BIZON_PORT`.

Consulta el [README del servidor](Servidor/README.md) para ver los endpoints disponibles y ejemplos de peticiones.

## Puesta en marcha

1. Inicia el servidor según las instrucciones anteriores.
2. Compila e instala la aplicación en el dispositivo.
3. Ejecuta la app y activa el modo MDM.
4. Desde ese momento la aplicación enviará su estado y recibirá comandos del servidor.
