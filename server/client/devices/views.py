"""Vistas de dispositivo para los clientes.

Expone un endpoint que devuelve únicamente las acciones permitidas para una
entidad determinada (tienda o contrato).
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from device.permissions import AVAILABLE_ACTIONS
from admin.permissions.views import get_allowed_actions

bp = Blueprint("devices", __name__, url_prefix="/devices")


@bp.route("/actions", methods=["GET"])
def list_actions():
    """Devuelve la lista de acciones permitidas."""

    entity_type = request.args.get("type")
    entity_id = request.args.get("id")
    allowed = get_allowed_actions(entity_type or "", entity_id or "")
    visible = [a for a in AVAILABLE_ACTIONS if a in allowed]
    return jsonify({"actions": visible})


__all__ = ["bp"]
