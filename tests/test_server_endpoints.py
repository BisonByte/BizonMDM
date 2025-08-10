import os
import sys
import tempfile
import pathlib
import pytest

# Ensure server modules are importable
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "server" / "Servidor"))

# Configure environment for testing
os.environ["JWT_SECRET"] = "testsecret"
os.environ["SKIP_ALEMBIC"] = "1"
os.environ["REGISTRATION_TOKEN"] = "testreg"

@pytest.fixture()
def test_app():
    """Yield a Flask test client and related helpers using a temp database."""
    fd, path = tempfile.mkstemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    import importlib
    import server as server_module
    import models as models_module
    server_module = importlib.reload(server_module)
    models_module = importlib.reload(models_module)
    server_module.init_db(drop=True)
    import werkzeug
    if not hasattr(werkzeug, "__version__"):
        werkzeug.__version__ = "3"
    with server_module.app.test_client() as client:
        yield client, server_module, models_module
    os.close(fd)
    os.unlink(path)


def test_login_endpoint(test_app):
    """Admin can obtain a valid token via /login."""
    client, server_module, models_module = test_app
    with server_module.get_session() as db:
        admin = models_module.Admin(username="adm")
        admin.set_password("pwd")
        db.add(admin)
        db.commit()
    resp = client.post("/login", json={"username": "adm", "password": "pwd"})
    assert resp.status_code == 200
    payload = server_module.decode_jwt(resp.get_json()["token"], os.environ["JWT_SECRET"])
    assert payload["role"] == "admin"
