"""Proceso de revisión y aprobación de documentos."""

from __future__ import annotations

from flask import Blueprint, jsonify

from documents.storage import list_pending, set_status

bp = Blueprint("document_review", __name__, url_prefix="/documents")


@bp.route("/pending", methods=["GET"])
def pending():
    """Lista los documentos que aún no han sido revisados."""

    docs = [
        {"id": d.id, "filename": d.filename, "status": d.status}
        for d in list_pending()
    ]
    return jsonify({"pending": docs})


@bp.route("/approve/<doc_id>", methods=["POST"])
def approve(doc_id: str):
    """Aprueba un documento."""

    if not set_status(doc_id, "approved"):
        return jsonify({"success": False, "message": "No encontrado"}), 404
    return jsonify({"success": True})


@bp.route("/reject/<doc_id>", methods=["POST"])
def reject(doc_id: str):
    """Rechaza un documento."""

    if not set_status(doc_id, "rejected"):
        return jsonify({"success": False, "message": "No encontrado"}), 404
    return jsonify({"success": True})


__all__ = ["bp"]
