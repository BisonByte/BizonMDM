# Development Setup

## Server

1. Create and activate a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r server/requirements.txt
   ```
3. Copy the environment template and adjust values:
   ```bash
   cp server/.env.example server/.env
   ```
4. Run the server:
   ```bash
   python server/server.py
   ```

## Web Admin

1. Install dependencies:
   ```bash
   npm install --prefix web-admin
   ```
2. Start a development server or serve the static files:
   ```bash
   npm run build --prefix web-admin
   ```

## Android

Build the Android application with Gradle:
```bash
./gradlew :android:assembleDebug
```
