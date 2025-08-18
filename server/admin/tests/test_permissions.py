from __future__ import annotations

import importlib
import os

from flask import Flask
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
sys.modules.pop("server", None)
sys.modules.pop("server.admin", None)


def test_permissions_persist_and_cache_invalidation(tmp_path, monkeypatch):
    db_path = tmp_path / "perm.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    sys.modules.pop("server", None)
    sys.modules.pop("server.admin", None)

    # reload modules to ensure they use the temp database

    # Reload modules to pick up the new DATABASE_URL
    from server.admin.permissions import models
    importlib.reload(models)
    models.init_db(drop=True)
    from server.admin.permissions import views
    importlib.reload(views)

    app = Flask(__name__)
    app.register_blueprint(views.bp)
    import werkzeug
    if not hasattr(werkzeug, "__version__"):
        werkzeug.__version__ = "3"
    client = app.test_client()

    resp = client.post(
        "/permissions/configure",
        json={"type": "store", "id": "1", "actions": ["lock"]},
    )
    assert resp.status_code == 200
    assert views.get_allowed_actions("store", "1") == {"lock"}

    resp = client.post(
        "/permissions/configure",
        json={"type": "store", "id": "1", "actions": ["gps"]},
    )
    assert resp.status_code == 200
    assert views.get_allowed_actions("store", "1") == {"gps"}
