import os
import subprocess
import sys
from pathlib import Path


def test_server_requires_jwt_secret(tmp_path):
    """Importing the server without JWT_SECRET should fail."""
    env = os.environ.copy()
    env.pop("JWT_SECRET", None)
    env["DATABASE_URL"] = f"sqlite:///{tmp_path/'test.db'}"
    env["SKIP_ALEMBIC"] = "1"
    base = Path(__file__).resolve().parents[1]
    dotenv = base / ".env"
    backup = base / ".env.bak"
    if dotenv.exists():
        dotenv.rename(backup)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", "import server"],
            cwd=base,
            env=env,
            capture_output=True,
            text=True,
        )
    finally:
        if backup.exists():
            backup.rename(dotenv)
    assert proc.returncode != 0
    assert "JWT_SECRET" in proc.stderr
