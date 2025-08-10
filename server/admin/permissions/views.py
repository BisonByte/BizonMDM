"""Vistas para gestionar permisos de acciones sobre dispositivos.

Proporciona un pequeño formulario (endpoint JSON) para habilitar o
inhabilitar acciones por tienda o contrato. La información se almacena en
memoria para simplificar el ejemplo.
"""

from __future__ import annotations

from typing import Dict, Set, Tuple
from flask import Blueprint, jsonify, request

from device.permissions import AVAILABLE_ACTIONS

bp = Blueprint("permissions", __name__, url_prefix="/permissions")

# Almacén en memoria: {(tipo, id): {acciones}}
_ALLOWED_ACTIONS: Dict[Tuple[str, str], Set[str]] = {}


def _key(entity_type: str, entity_id: str) -> Tuple[str, str]:
    """Genera la clave interna del almacén."""

    return (entity_type, str(entity_id))


@bp.route("/configure", methods=["POST"])
def configure_permissions():
    """Configura las acciones permitidas para una tienda o contrato."""

    data = request.get_json() or {}
    entity_type = data.get("type")  # 'store' o 'contract'
    entity_id = data.get("id")
    actions = data.get("actions", [])
    if entity_type not in {"store", "contract"} or not entity_id:
        return (
            jsonify({"success": False, "message": "Entidad no válida"}),
            400,
        )
    invalid = [a for a in actions if a not in AVAILABLE_ACTIONS]
    if invalid:
        return (
            jsonify({"success": False, "invalid": invalid}),
            400,
        )
    _ALLOWED_ACTIONS[_key(entity_type, entity_id)] = set(actions)
    return jsonify({"success": True})


def get_allowed_actions(entity_type: str, entity_id: str) -> Set[str]:
    """Obtiene las acciones permitidas para la entidad indicada."""

    return _ALLOWED_ACTIONS.get(_key(entity_type, entity_id), set())


__all__ = ["bp", "get_allowed_actions"]
