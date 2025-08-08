import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .utils.config_loader import load_config

limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
    cfg = load_config()
    app.config.update(cfg)

    CORS(app, origins=[cfg.get('APP_URL')] if cfg.get('APP_URL') else [])
    limiter.init_app(app)

    @app.route('/panel/health')
    def health():
        return jsonify({"ok": True, "installed": bool(cfg.get('INSTALLED'))})

    @app.errorhandler(400)
    def err400(e):
        return jsonify({'error': 'bad_request'}), 400

    @app.errorhandler(401)
    def err401(e):
        return jsonify({'error': 'unauthorized'}), 401

    @app.errorhandler(403)
    def err403(e):
        return jsonify({'error': 'forbidden'}), 403

    @app.errorhandler(500)
    def err500(e):
        return jsonify({'error': 'server_error'}), 500

    if not cfg.get('INSTALLED'):
        from .install import bp as install_bp
        app.register_blueprint(install_bp, url_prefix='/panel')
    else:
        from .api.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/panel/api')

    return app
