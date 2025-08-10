import os
import tempfile
import sys
import pytest

# Set up temporary database and environment variables
DB_FD, DB_PATH = tempfile.mkstemp()
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
os.environ['JWT_SECRET'] = 'testsecret'
os.environ['SKIP_ALEMBIC'] = '1'

# Ensure modules in server directory can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from server import app, init_db, get_session  # type: ignore
from models import Admin  # type: ignore


@pytest.fixture(scope="module")
def client():
    """Create a Flask test client with a fresh database."""
    init_db(drop=True)
    import werkzeug
    if not hasattr(werkzeug, "__version__"):
        werkzeug.__version__ = "3"
    with app.test_client() as client:
        yield client
    os.close(DB_FD)
    os.unlink(DB_PATH)


def test_admin_login(client):
    """Admin can log in and receive a JWT token."""
    with get_session() as db:
        admin = Admin(username='adm')
        admin.set_password('pwd')
        db.add(admin)
        db.commit()
    resp = client.post('/login', json={'username': 'adm', 'password': 'pwd'})
    assert resp.status_code == 200
    assert 'token' in resp.get_json()
