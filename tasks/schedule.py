"""Configuración de tareas programadas."""

from __future__ import annotations

import time

from alerts.payment_reminders import process_upcoming_payments


def run_scheduler() -> None:
    """Inicia un bucle simple de tareas programadas.

    Utiliza la librería ``schedule`` si está disponible. Ejecuta el servicio
    :func:`alerts.payment_reminders.process_upcoming_payments` todos los días a
    las 9 AM.
    """

    try:
        import schedule
    except ImportError as exc:  # pragma: no cover - depende del entorno
        raise RuntimeError(
            "La librería 'schedule' es necesaria para ejecutar las tareas"
        ) from exc

    schedule.every().day.at("09:00").do(process_upcoming_payments)

    while True:  # pragma: no cover - bucle infinito
        schedule.run_pending()
        time.sleep(60)


__all__ = ["run_scheduler"]
