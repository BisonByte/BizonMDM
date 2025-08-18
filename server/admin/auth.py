from __future__ import annotations

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def require_admin(func):
    """Decorator that enforces presence of a valid admin JWT token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
        except Exception:  # noqa: BLE001
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        if claims.get("role") != "admin":
            return jsonify({"success": False, "message": "Forbidden"}), 403
        return func(*args, **kwargs)

    return wrapper

__all__ = ["require_admin"]
