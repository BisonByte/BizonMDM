"""Vistas para gestión de documentos por parte del cliente.

Proporciona un formulario para subir archivos y un endpoint para consultar el
estado de revisión del documento cargado.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from documents.storage import get, save

bp = Blueprint("client_documents", __name__, url_prefix="/documents")


@bp.route("/upload", methods=["POST"])
def upload():
    """Recibe un archivo y lo almacena."""

    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"success": False, "message": "Archivo requerido"}), 400
    doc = save(file)
    return jsonify({"success": True, "document_id": doc.id, "url": doc.url}), 201


@bp.route("/status/<doc_id>", methods=["GET"])
def status(doc_id: str):
    """Devuelve el estado actual de un documento."""

    doc = get(doc_id)
    if not doc:
        return jsonify({"success": False, "message": "No encontrado"}), 404
    return jsonify(
        {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "url": doc.url,
        }
    )


__all__ = ["bp"]
