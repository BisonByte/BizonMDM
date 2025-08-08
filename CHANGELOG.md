# Changelog

## v1.0.0 - 2025-08-08

### Features
- Initial stable release of BizonMDM.
- Flask-based REST API server for managing devices.
- Minimal web administration interface for issuing commands.
- Android client application that communicates with the server.

### Upgrade instructions
- Install Python dependencies with `pip install -r server/requirements.txt`.
- Install web interface dependencies with `npm install --prefix web-admin` and build using `npm run build --prefix web-admin`.
- Build the Android client using `./gradlew :android:assembleDebug`.
- Copy the sample environment file: `cp server/.env.example server/.env`.
