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
                '/api/device/reboot',
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

    def test_client_crud(self):
        # create device to assign
        self.client.post('/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        # create client
        resp = self.client.post(
            '/admin/clients',
            json={'name': 'Acme', 'permissions': ['wipe'], 'deviceIds': ['d1']},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 201)
        cid = resp.get_json()['id']
        # list and check assignment
        resp = self.client.get('/admin/clients', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        clients = resp.get_json()
        self.assertEqual(clients[0]['devices'], ['d1'])
        # update client
        resp = self.client.put(
            f'/admin/clients/{cid}',
            json={'name': 'Acme2', 'permissions': ['reboot'], 'deviceIds': []},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(f'/admin/clients/{cid}', headers=self.auth_header())
        data = resp.get_json()
        self.assertEqual(data['name'], 'Acme2')
        self.assertEqual(data['permissions'], ['reboot'])
        self.assertEqual(data['devices'], [])
        # delete client
        resp = self.client.delete(f'/admin/clients/{cid}', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)

if __name__ == '__main__':
    unittest.main()
