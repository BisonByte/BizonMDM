from __future__ import annotations

"""Servicio para procesar cuotas próximas a vencer."""

from datetime import date, timedelta
from typing import Iterable

from financing.contracts.models import PaymentSchedule, SessionLocal


def upcoming_payments(days: int = 7) -> Iterable[PaymentSchedule]:
    """Obtiene las cuotas que vencerán dentro de ``days`` días.

    Args:
        days: Número de días hacia adelante para buscar cuotas pendientes.

    Returns:
        Iterable de :class:`PaymentSchedule` que cumplen los criterios.
    """

    today = date.today()
    limit = today + timedelta(days=days)

    with SessionLocal() as session:
        schedules = (
            session.query(PaymentSchedule)
            .filter(PaymentSchedule.due_date.between(today, limit))
            .filter(PaymentSchedule.paid.is_(False))
            .all()
        )
    return schedules


def process_upcoming_payments(days: int = 7) -> None:
    """Procesa las cuotas próximas a vencer.

    Por ahora solo imprime recordatorios en consola; en una implementación
    real se enviaría un correo o notificación.
    """

    for schedule in upcoming_payments(days):
        print(
            "Recordatorio de pago: contrato", schedule.contract_id,
            "- monto", schedule.amount,
            "- vence el", schedule.due_date,
        )


__all__ = ["upcoming_payments", "process_upcoming_payments"]
