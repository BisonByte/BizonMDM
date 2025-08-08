# BizonMDM

BizonMDM is a simple mobile device management solution composed of a Python backend, a web administration interface and an Android client.

## Architecture

- **server**: Flask REST API that stores device information and processes commands.
- **web-admin**: minimal web UI for managing devices through the API.
- **android**: Android application that communicates with the server.

## Run with Docker

```bash
cd infra
docker compose up
```

This starts a PostgreSQL database and the server on port `5000`.

## Run services without Docker

### Server
```bash
pip install -r server/requirements.txt
cp server/.env.example server/.env
python server/server.py
```

### Web Admin
```bash
npm install --prefix web-admin
npm run build --prefix web-admin
```
Serve the contents of `web-admin/` with your preferred static server.

### Android
```bash
./gradlew :android:assembleDebug
```

See [docs/DEV_SETUP.md](docs/DEV_SETUP.md) for detailed setup instructions.

## Seguridad

- Los endpoints sensibles `/panel/install` y `/panel/api/auth/*` están protegidos por un límite de 5 peticiones cada 10 segundos mediante `flask-limiter`:

  ```python
  @limiter.limit("5 per 10 seconds")
  ```

- Durante la instalación se exige que la contraseña del administrador sea fuerte (mínimo 14 caracteres con mayúsculas, minúsculas y números).

- La API de autenticación emite tokens de acceso y de refresco. El token de refresco se rota en cada petición y el JTI del token previo se guarda en la lista negra (`jwt_blacklist`).

  ```bash
  # iniciar sesión
  curl -X POST http://localhost:5000/panel/api/auth/login \\
       -H 'Content-Type: application/json' \\
       -d '{"email":"admin@example.com","password":"<contraseña>"}'

  # renovar token
  curl -X POST http://localhost:5000/panel/api/auth/refresh \\
       -H 'Authorization: Bearer <refresh_token>'
  ```

- Todas las operaciones críticas se registran en la tabla `audit_logs` para auditoría.
