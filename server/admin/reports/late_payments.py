"""Vistas de reportes de morosidad."""

from __future__ import annotations

import io
from datetime import date
from typing import List

from flask import Blueprint, jsonify, send_file

from financing.contracts.models import PaymentSchedule, SessionLocal

bp = Blueprint("late_payments", __name__, url_prefix="/reports/late-payments")


def _get_late_schedules() -> List[PaymentSchedule]:
    """Recupera cuotas vencidas y no pagadas."""

    today = date.today()
    with SessionLocal() as session:
        return (
            session.query(PaymentSchedule)
            .filter(PaymentSchedule.due_date < today)
            .filter(PaymentSchedule.paid.is_(False))
            .all()
        )


@bp.route("/table")
def table() -> "flask.Response":
    """Tabla JSON con las cuotas morosas."""

    data = [
        {
            "contract_id": s.contract_id,
            "due_date": s.due_date.isoformat(),
            "amount": s.amount,
        }
        for s in _get_late_schedules()
    ]
    return jsonify(data)


@bp.route("/chart")
def chart():  # pragma: no cover - depende de tener matplotlib
    """Gráfico de barras con los días de atraso."""

    schedules = _get_late_schedules()
    if not schedules:
        return jsonify({"message": "Sin pagos atrasados"})

    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        return jsonify({"error": str(exc)})

    days_overdue = [(date.today() - s.due_date).days for s in schedules]

    fig, ax = plt.subplots()
    ax.bar(range(len(days_overdue)), days_overdue)
    ax.set_title("Días de atraso por cuota")
    ax.set_xlabel("Cuota")
    ax.set_ylabel("Días")

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


__all__ = ["bp"]
