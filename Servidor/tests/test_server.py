import os
import tempfile
import unittest
import sys

os.environ['BIZON_TOKEN'] = 'testtoken'

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from server import app, init_db

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['BIZON_DB'] = self.db_path
        init_db()
        self.client = app.test_client()
        self.token = 'testtoken'
        os.environ['BIZON_TOKEN'] = self.token

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def auth_header(self):
        return {'Authorization': f'Bearer {self.token}'}

    def test_register_device(self):
        data = {'deviceId': 'd1', 'model': 'Pixel'}
        resp = self.client.post('/devices/register', json=data, headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/devices/d1', headers=self.auth_header())
        self.assertEqual(resp.status_code, 200)
        info = resp.get_json()
        self.assertEqual(info['model'], 'Pixel')

if __name__ == '__main__':
    unittest.main()
