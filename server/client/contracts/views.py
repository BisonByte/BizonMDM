from __future__ import annotations

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request

from financing.contracts.models import Contract, PaymentSchedule, SessionLocal
from server.Servidor.models import SessionLocal as MainSession, Client


bp = Blueprint("contracts", __name__, url_prefix="/contracts")


@bp.route("/register", methods=["POST"])
def register_contract():
    """Registra un contrato y genera su cronograma de pagos."""

    data = request.get_json() or {}
    client_id = data.get("client_id")
    store_id = data.get("store_id")
    amount = data.get("amount")
    interest_rate = data.get("interest_rate")
    term = data.get("term")
    if not all([client_id, amount, interest_rate, term, store_id]):
        return jsonify({"success": False, "message": "Campos incompletos"}), 400
    with MainSession() as mdb:
        client = mdb.query(Client).filter_by(id=client_id, store_id=store_id).first()
        if not client:
            return jsonify({"success": False, "message": "Cliente no encontrado"}), 404

    with SessionLocal() as db:
        contract = Contract(
            client_id=client_id, amount=amount, interest_rate=interest_rate, term=term
        )
        db.add(contract)
        db.flush()

        monthly_rate = (interest_rate / 12) / 100
        if monthly_rate:
            cuota = amount * (
                monthly_rate * (1 + monthly_rate) ** term
            ) / ((1 + monthly_rate) ** term - 1)
        else:
            cuota = amount / term

        for i in range(term):
            due_date = datetime.utcnow().date() + timedelta(days=30 * (i + 1))
            schedule = PaymentSchedule(
                contract_id=contract.id, due_date=due_date, amount=cuota
            )
            db.add(schedule)

        db.commit()

    return jsonify({"success": True, "contract_id": contract.id}), 201


@bp.route("/pending/<int:client_id>", methods=["GET"])
def pending_payments(client_id: int):
    """Lista los pagos pendientes de un cliente."""

    store_id = request.args.get("store_id", type=int)
    if store_id is None:
        return jsonify({"success": False, "message": "store_id requerido"}), 400
    with MainSession() as mdb:
        client = mdb.query(Client).filter_by(id=client_id, store_id=store_id).first()
        if not client:
            return jsonify({"pending": []})
    with SessionLocal() as db:
        schedules = (
            db.query(PaymentSchedule)
            .join(Contract)
            .filter(Contract.client_id == client_id, PaymentSchedule.paid.is_(False))
            .all()
        )

        result = [
            {
                "id": s.id,
                "contract_id": s.contract_id,
                "due_date": s.due_date.isoformat(),
                "amount": s.amount,
            }
            for s in schedules
        ]

    return jsonify({"pending": result})
