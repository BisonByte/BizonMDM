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
from server import app, init_db, encode_jwt, decode_jwt, get_session
from models import Admin


class ServerTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        os.close(DB_FD)
        os.unlink(DB_PATH)

    def setUp(self):
        init_db(drop=True)
        import werkzeug
        if not hasattr(werkzeug, "__version__"):
            werkzeug.__version__ = "3"
        self.client = app.test_client()
        self.token = encode_jwt('tester', os.environ['JWT_SECRET'], role='admin')

    def auth_header(self):
        return {'Authorization': f'Bearer {self.token}'}

    def client_header(self, device_id='d1'):
        token = encode_jwt(device_id, os.environ['JWT_SECRET'], role='client', client_id=device_id)
        return {'Authorization': f'Bearer {token}'}

    def test_login(self):
        with get_session() as db:
            admin = Admin(username='adm')
            admin.set_password('pwd')
            db.add(admin)
            db.commit()
        resp = self.client.post('/login', json={'username': 'adm', 'password': 'pwd'})
        self.assertEqual(resp.status_code, 200)
        token = resp.get_json()['token']
        payload = decode_jwt(token, os.environ['JWT_SECRET'])
        self.assertEqual(payload['role'], 'admin')
        self.assertNotIn('client_id', payload)

        # Login as client using an existing device
        self.client.post('/admin/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        resp = self.client.post('/login', json={'client_id': 'd1'})
        self.assertEqual(resp.status_code, 200)
        token = resp.get_json()['token']
        payload = decode_jwt(token, os.environ['JWT_SECRET'])
        self.assertEqual(payload['role'], 'client')
        self.assertEqual(payload['client_id'], 'd1')

    def test_register_device(self):
        data = {'deviceId': 'd1', 'model': 'Pixel', 'serial': '123', 'imei': '999'}
        resp = self.client.post('/admin/devices/register', json=data, headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/admin/devices/d1', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        info = resp.get_json()
        self.assertEqual(info['model'], 'Pixel')
        self.assertEqual(info['serial'], '123')
        self.assertEqual(info['imei'], '999')

    def test_device_control_endpoints(self):
        self.client.post('/admin/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        actions = [
            ('device_wipe', '/admin/device/wipe'),
            ('device_reboot', '/admin/device/reboot'),
            ('device_lock', '/admin/device/lock'),
            ('device_screenshot', '/admin/device/screenshot'),
        ]
        for action, endpoint in actions:
            resp = self.client.post(endpoint, json={'deviceId': 'd1'}, headers=self.auth_header())
            self.assertEqual(resp.status_code, 200)
            resp = self.client.get('/client/commands', headers=self.client_header('d1'))
            self.assertEqual(resp.status_code, 200)
            cmds = resp.get_json()
            self.assertEqual(len(cmds), 1)
            self.assertEqual(cmds[0]['action'], action)

    def test_app_management_endpoints(self):
        self.client.post('/admin/devices/register', json={'deviceId': 'd1'}, headers=self.auth_header())
        resp = self.client.post(
            '/admin/app/install',
            json={'deviceId': 'd1', 'url': 'http://example.com/app.apk'},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/client/commands', headers=self.client_header('d1'))
        cmds = resp.get_json()
        self.assertEqual(cmds[0]['action'], 'app_install')
        self.assertEqual(cmds[0]['url'], 'http://example.com/app.apk')

        resp = self.client.post(
            '/admin/app/uninstall',
            json={'deviceId': 'd1', 'package': 'com.example.app'},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/client/commands', headers=self.client_header('d1'))
        cmds = resp.get_json()
        self.assertEqual(cmds[0]['action'], 'app_uninstall')
        self.assertEqual(cmds[0]['package'], 'com.example.app')

    @mock.patch('server._send_fcm_message', return_value=True)
    def test_fcm_notification_sent(self, mock_send):
        os.environ['FCM_SERVER_KEY'] = 'dummy'
        try:
            self.client.post(
                '/admin/devices/register',
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

    def test_fcm_error_response(self):
        import server
        server.FCM_SERVER_KEY = 'dummy'
        mock_resp = mock.Mock()
        mock_resp.getcode.return_value = 500
        with mock.patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            with self.assertLogs(level='WARNING') as cm:
                ok = server._send_fcm_message('tok', {'action': 'x'})
        self.assertFalse(ok)
        self.assertIn('HTTP 500', cm.output[0])
        server.FCM_SERVER_KEY = None

    def test_fcm_exception_response(self):
        import server
        server.FCM_SERVER_KEY = 'dummy'
        with mock.patch('urllib.request.urlopen', side_effect=Exception('boom')):
            with self.assertLogs(level='WARNING'):
                ok = server._send_fcm_message('tok', {'action': 'x'})
        self.assertFalse(ok)
        server.FCM_SERVER_KEY = None

    def test_admin_clients_crud(self):
        # Register a device to assign later
        self.client.post('/devices/register', json={'deviceId': 'd1'})
        resp = self.client.post(
            '/admin/clients',
            json={'username': 'cli', 'password': 'pwd', 'permissions': ['wipe']},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 201)
        cid = resp.get_json()['id']
        resp = self.client.get('/admin/clients', headers=self.auth_header())
        self.assertEqual(len(resp.get_json()), 1)
        resp = self.client.put(
            f'/admin/clients/{cid}',
            json={'permissions': ['wipe', 'reboot'], 'devices': ['d1']},
            headers=self.auth_header(),
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/admin/clients', headers=self.auth_header())
        data = resp.get_json()[0]
        self.assertIn('reboot', data['permissions'])
        self.assertIn('d1', data['devices'])
        resp = self.client.delete(f'/admin/clients/{cid}', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/admin/clients', headers=self.auth_header())
        self.assertEqual(resp.get_json(), [])

    def test_init_db_preserves_data_without_drop_flag(self):
        """Calling init_db without drop should not remove existing data."""
        with get_session() as db:
            admin = Admin(username='keep')
            admin.set_password('pwd')
            db.add(admin)
            db.commit()

        init_db()

        with get_session() as db:
            admin = db.query(Admin).filter_by(username='keep').first()
            self.assertIsNotNone(admin)

if __name__ == '__main__':
    unittest.main()
