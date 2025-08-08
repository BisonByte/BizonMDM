import os
import tempfile
import unittest
import sys

# Configure database and token before importing the server
DB_FD, DB_PATH = tempfile.mkstemp()
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
os.environ['BIZON_TOKEN'] = 'testtoken'

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app, init_db


class ServerTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        os.close(DB_FD)
        os.unlink(DB_PATH)

    def setUp(self):
        init_db()
        import werkzeug
        if not hasattr(werkzeug, "__version__"):
            werkzeug.__version__ = "3"
        self.client = app.test_client()
        self.token = 'testtoken'

    def auth_header(self):
        return {'Authorization': f'Bearer {self.token}'}

    def test_register_device(self):
        data = {'deviceId': 'd1', 'model': 'Pixel', 'serial': '123', 'imei': '999'}
        resp = self.client.post('/devices/register', json=data, headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/devices/d1', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        info = resp.get_json()
        self.assertEqual(info['model'], 'Pixel')
        self.assertEqual(info['serial'], '123')
        self.assertEqual(info['imei'], '999')

if __name__ == '__main__':
    unittest.main()
