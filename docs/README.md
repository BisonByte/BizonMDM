# Documentación

La documentación completa de BizonMDM se encuentra en `documentation.html`. Abre este archivo en tu navegador para obtener una guía detallada de instalación y uso.

## Novedades

- La carpeta `DEMO/` ahora utiliza un estilo unificado para el panel administrativo y el del cliente.
- Todas las vistas incluyen la etiqueta `meta viewport` e iconos de Font Awesome para mejorar la apariencia.
- Puedes personalizar los colores y la estética editando `DEMO/style.css`.

## Instalación del servidor

### Requisitos previos

- Python 3.10+ y `pip`.
- Node.js 18+ si necesitas recompilar el panel React.
- Una base de datos SQL (PostgreSQL, MySQL/MariaDB o SQLite para pruebas).
- Clave de servidor de Firebase Cloud Messaging.

### Variables de entorno

Define antes de instalar:

```bash
export DATABASE_URL="postgresql://usuario:pass@localhost/bizon"
export BIZON_HOST=0.0.0.0
export BIZON_PORT=5000
export JWT_SECRET="cambia_esta_clave"
export FCM_SERVER_KEY="tu_clave_de_fcm"
```

> **Nota de seguridad:** guarda estas variables en un archivo `.env` con permisos restrictivos y nunca lo incluyas en el control de versiones.

### Instalación

```bash
pip install -r server/Servidor/requirements.txt
python server/install.py
docker-compose up -d
```

Verifica el estado del servicio con:

```bash
curl http://localhost:5000/api/status
```

### Notas de seguridad

- Ejecuta el servidor detrás de HTTPS.
- Protege el endpoint `/install` una vez finalizado el proceso.
- Mantén secreta la clave de Firebase y la variable `JWT_SECRET`.

## Configuración de la aplicación móvil

### Definir `BuildConfig.BASE_URL`

La app obtiene la URL del backend desde `BuildConfig.BASE_URL`.
Puedes establecerla mediante variables de entorno, `gradle.properties` o los `productFlavors`.

### `gradle.properties`

Ejemplo de definición:

```properties
DEV_BASE_URL=https://dev.tuservidor.com/
PROD_BASE_URL=https://tuservidor.com/
```

> **Nota:** evita subir `gradle.properties` con valores sensibles al repositorio.

### Compilar los flavors `dev` y `prod`

```bash
./gradlew assembleDevDebug    # usa DEV_BASE_URL
./gradlew assembleProdRelease # usa PROD_BASE_URL
```

### Notas de seguridad

- Usa URLs de producción solo para builds destinadas a usuarios finales.
- Revisa que los certificados SSL sean válidos en los entornos de producción y pruebas.
