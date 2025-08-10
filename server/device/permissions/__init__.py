"""Catálogo de acciones disponibles para dispositivos.

Este módulo centraliza las acciones que pueden ejecutarse sobre un dispositivo
desde el sistema de administración. Se utiliza para validar permisos y para
exponer la lista de acciones disponibles a otros módulos.
"""

from __future__ import annotations

from enum import Enum


class Action(str, Enum):
    """Acciones soportadas por los dispositivos."""

    LOCK = "lock"
    GPS = "gps"
    WIPE = "wipe"


# Conjunto inmutable de acciones disponibles
AVAILABLE_ACTIONS: set[str] = {action.value for action in Action}

__all__ = ["Action", "AVAILABLE_ACTIONS"]
