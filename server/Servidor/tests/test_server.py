import os
import tempfile
import unittest
import sys
from unittest import mock

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
        self.token = encode_jwt({'sub': 'tester', 'role': 'admin'}, os.environ['JWT_SECRET'])

    def auth_header(self):
        return {'Authorization': f'Bearer {self.token}'}

    def test_register_device(self):
        data = {'deviceId': 'd1', 'model': 'Pixel', 'serial': '123', 'imei': '999'}
        resp = self.client.post('/devices/register', json=data, headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/admin/devices/d1', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        info = resp.get_json()
        self.assertEqual(info['model'], 'Pixel')
        self.assertEqual(info['serial'], '123')
        self.assertEqual(info['imei'], '999')

    def test_device_control_endpoints(self):
        self.client.post('/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        actions = [
            ('device_wipe', '/admin/device/wipe'),
            ('device_reboot', '/admin/device/reboot'),
            ('device_lock', '/admin/device/lock'),
            ('device_screenshot', '/admin/device/screenshot'),
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
            '/admin/app/install',
            json={'deviceId': 'd1', 'url': 'http://example.com/app.apk'},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/commands/d1', headers=self.auth_header())
        cmds = resp.get_json()
        self.assertEqual(cmds[0]['action'], 'app_install')
        self.assertEqual(cmds[0]['url'], 'http://example.com/app.apk')

        resp = self.client.post(
            '/admin/app/uninstall',
            json={'deviceId': 'd1', 'package': 'com.example.app'},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/commands/d1', headers=self.auth_header())
        cmds = resp.get_json()
        self.assertEqual(cmds[0]['action'], 'app_uninstall')
        self.assertEqual(cmds[0]['package'], 'com.example.app')

    @mock.patch('server._send_fcm_message')
    def test_fcm_notification_sent(self, mock_send):
        os.environ['FCM_SERVER_KEY'] = 'dummy'
        try:
            self.client.post(
                '/devices/register',
                json={'deviceId': 'd1', 'fcmToken': 'tok'},
                headers=self.auth_header(),
            )
            resp = self.client.post(
                '/admin/device/reboot',
                json={'deviceId': 'd1'},
                headers=self.auth_header(),
            )
            self.assertEqual(resp.status_code, 200)
            mock_send.assert_called_once()
            token, payload = mock_send.call_args.args
            self.assertEqual(token, 'tok')
            self.assertEqual(payload['action'], 'device_reboot')
        finally:
            del os.environ['FCM_SERVER_KEY']

    def client_header(self, cid):
        tok = encode_jwt({'sub': cid, 'role': 'client', 'client_id': cid}, os.environ['JWT_SECRET'])
        return {'Authorization': f'Bearer {tok}'}

    def test_client_device_isolation(self):
        self.client.post('/devices/register', json={'deviceId': 'd1', 'clientId': 'c1'}, headers=self.auth_header())
        self.client.post('/devices/register', json={'deviceId': 'd2', 'clientId': 'c2'}, headers=self.auth_header())

        resp = self.client.get('/client/devices', headers=self.client_header('c1'))
        self.assertEqual(resp.status_code, 200)
        devices = resp.get_json()
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]['deviceId'], 'd1')

        resp = self.client.post('/client/device/wipe', json={'deviceId': 'd2'}, headers=self.client_header('c1'))
        self.assertEqual(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
