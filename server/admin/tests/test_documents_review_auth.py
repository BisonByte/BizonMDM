import os
import sys
import unittest

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
import werkzeug

# Ensure modules in server directory can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from admin.documents.review import bp  # type: ignore  # noqa: E402


class ReviewAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["JWT_SECRET_KEY"] = "testsecret"
        JWTManager(self.app)
        if not hasattr(werkzeug, "__version__"):
            werkzeug.__version__ = "3"  # pragma: no cover
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

    def _user_token(self):
        with self.app.app_context():
            return create_access_token("user1", additional_claims={"role": "user"})

    def test_pending_requires_admin(self):
        resp = self.client.get("/documents/pending")
        self.assertEqual(resp.status_code, 401)
        token = self._user_token()
        resp = self.client.get(
            "/documents/pending", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(resp.status_code, 403)

    def test_modify_requires_admin(self):
        for endpoint in ["/documents/approve/1", "/documents/reject/1"]:
            resp = self.client.post(endpoint)
            self.assertEqual(resp.status_code, 401)
            token = self._user_token()
            resp = self.client.post(
                endpoint, headers={"Authorization": f"Bearer {token}"}
            )
            self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main()
