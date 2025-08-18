"""Vistas para gestionar permisos de acciones sobre dispositivos.

Los permisos se almacenan en una tabla de base de datos. Opcionalmente se
cachean en memoria para acelerar las consultas. Cada vez que se actualizan los
permisos de una entidad, la caché correspondiente se invalida.
"""

from __future__ import annotations

import os
from typing import Dict, Set, Tuple

from flask import Blueprint, jsonify, request

from ...device.permissions import AVAILABLE_ACTIONS
from .models import Permission, SessionLocal, init_db

bp = Blueprint("permissions", __name__, url_prefix="/permissions")

CACHE_ENABLED = os.getenv("PERMISSIONS_CACHE", "1") == "1"
_cache: Dict[Tuple[str, str], Set[str]] = {}

init_db()


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
    with SessionLocal() as session:
        session.query(Permission).filter_by(
            entity_type=entity_type, entity_id=str(entity_id)
        ).delete()
        session.add_all(
            [
                Permission(
                    entity_type=entity_type, entity_id=str(entity_id), action=a
                )
                for a in actions
            ]
        )
        session.commit()
    if CACHE_ENABLED:
        _cache.pop(_key(entity_type, entity_id), None)
    return jsonify({"success": True})


def get_allowed_actions(entity_type: str, entity_id: str) -> Set[str]:
    """Obtiene las acciones permitidas para la entidad indicada."""

    key = _key(entity_type, entity_id)
    if CACHE_ENABLED and key in _cache:
        return _cache[key]
    with SessionLocal() as session:
        rows = (
            session.query(Permission.action)
            .filter_by(entity_type=entity_type, entity_id=str(entity_id))
            .all()
        )
        actions = {r[0] for r in rows}
    if CACHE_ENABLED:
        _cache[key] = actions
    return actions


__all__ = ["bp", "get_allowed_actions"]
