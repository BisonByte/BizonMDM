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
