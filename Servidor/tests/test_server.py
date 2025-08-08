import os
import tempfile
import unittest
import sys

# Configure database and token before importing the server
DB_FD, DB_PATH = tempfile.mkstemp()
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
os.environ['JWT_SECRET'] = 'testsecret'

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app, init_db, encode_jwt


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
        self.token = encode_jwt({'sub': 'tester'}, os.environ['JWT_SECRET'])

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

    def test_device_control_endpoints(self):
        self.client.post('/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        actions = [
            ('device_wipe', '/api/device/wipe'),
            ('device_reboot', '/api/device/reboot'),
            ('device_lock', '/api/device/lock'),
            ('device_screenshot', '/api/device/screenshot'),
        ]
        for action, endpoint in actions:
            resp = self.client.post(endpoint, json={'deviceId': 'd1'}, headers=self.auth_header())
            self.assertEqual(resp.status_code, 200)
            resp = self.client.get('/commands/d1', headers=self.auth_header())
            self.assertEqual(resp.status_code, 200)
            cmds = resp.get_json()
            self.assertEqual(len(cmds), 1)
            self.assertEqual(cmds[0]['action'], action)

    def test_app_management_endpoints(self):
        self.client.post('/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        resp = self.client.post(
            '/api/app/install',
            json={'deviceId': 'd1', 'url': 'http://example.com/app.apk'},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/commands/d1', headers=self.auth_header())
        cmds = resp.get_json()
        self.assertEqual(cmds[0]['action'], 'app_install')
        self.assertEqual(cmds[0]['url'], 'http://example.com/app.apk')

        resp = self.client.post(
            '/api/app/uninstall',
            json={'deviceId': 'd1', 'package': 'com.example.app'},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/commands/d1', headers=self.auth_header())
        cmds = resp.get_json()
        self.assertEqual(cmds[0]['action'], 'app_uninstall')
        self.assertEqual(cmds[0]['package'], 'com.example.app')

if __name__ == '__main__':
    unittest.main()
